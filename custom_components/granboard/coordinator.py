"""Bluetooth session and game state for one Granboard."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import (
    BleakClientWithServiceCache,
    close_stale_connections_by_address,
    establish_connection,
)

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothChange,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_register_callback,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_BUTTON_NEXT,
    CONF_CONNECT,
    CONF_DEBOUNCE_MS,
    CONF_LED_FX,
    DEFAULT_BUTTON_NEXT,
    DEFAULT_DEBOUNCE_MS,
    DEFAULT_LED_FX,
    DOMAIN,
    EVENT_AWARD,
    EVENT_BUTTON,
    EVENT_HIT,
    EVENT_TURN,
    NOTIFY_UUID,
    SERVICE_UUID,
    STORAGE_VERSION,
    WRITE_UUID,
)
from . import led
from .colors import to_rgb
from .game import Game
from .protocol import Button, FrameBuffer, Hit, decode_frame
from .reconnect import DuplicateFilter, WarmupGate, backoff_seconds

_LOGGER = logging.getLogger(__name__)

LED_QUEUE_MAX = 48

type GranboardConfigEntry = ConfigEntry["GranboardCoordinator"]


@dataclass
class BoardData:
    """What the entities read."""

    connected: bool = False
    rssi: int | None = None
    last_hit: Hit | None = None
    last_hit_time: datetime | None = None
    last_raw: str | None = None
    notify_uuid: str | None = None
    write_uuid: str | None = None
    characteristics: list[str] = field(default_factory=list)


class GranboardCoordinator(DataUpdateCoordinator[BoardData]):
    """Keeps the board connected while enabled and turns frames into events."""

    def __init__(self, hass: HomeAssistant, entry: GranboardConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=entry.title, config_entry=entry)
        self.entry = entry
        self.address: str = entry.unique_id or entry.data["address"]
        self.data = BoardData()
        self.game = Game()
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{self.address.replace(':', '').lower()}")
        self._buffer = FrameBuffer()
        self._warmup = WarmupGate()
        self._dedupe = DuplicateFilter(self.debounce_ms)
        self._led_queue: deque[led.Step] = deque()
        self._led_task: asyncio.Task[None] | None = None
        self._write_response = False
        self.led_writes = 0
        self._client: BleakClientWithServiceCache | None = None
        self._device: BLEDevice | None = None
        self._disconnected = asyncio.Event()
        self._retry_now = asyncio.Event()
        self._task: asyncio.Task[None] | None = None
        self._ble_unsub: Any = None
        self._attempt = 0
        self._stopping = False
        self._shut_down = False

    # ------------------------------------------------------------ lifecycle
    @property
    def enabled(self) -> bool:
        return bool(self.entry.options.get(CONF_CONNECT, True))

    @property
    def button_next_player(self) -> bool:
        return bool(self.entry.options.get(CONF_BUTTON_NEXT, DEFAULT_BUTTON_NEXT))

    @property
    def led_effects(self) -> bool:
        return bool(self.entry.options.get(CONF_LED_FX, DEFAULT_LED_FX))

    @property
    def debounce_ms(self) -> int:
        return int(self.entry.options.get(CONF_DEBOUNCE_MS, DEFAULT_DEBOUNCE_MS))

    async def async_start(self) -> None:
        stored = await self._store.async_load()
        self.game = Game.load(stored)
        info = bluetooth.async_last_service_info(self.hass, self.address, connectable=False)
        if info is not None:
            self.data.rssi = info.rssi
        self._ble_unsub = async_register_callback(
            self.hass,
            self._on_advertisement,
            BluetoothCallbackMatcher(address=self.address),
            BluetoothScanningMode.PASSIVE,
        )
        if self.enabled:
            self._start_loop()

    def _start_loop(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._stopping = False
        self._attempt = 0
        self._task = self.entry.async_create_background_task(
            self.hass, self._run(), name=f"{DOMAIN}-{self.address}"
        )

    async def _stop_loop(self) -> None:
        self._stopping = True
        self._disconnected.set()
        self._retry_now.set()
        task, self._task = self._task, None
        if task is not None and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        await self._disconnect_client()
        self._set_connected(False)

    async def async_shutdown(self) -> None:
        if self._shut_down:
            return
        self._shut_down = True
        if self._ble_unsub is not None:
            self._ble_unsub()
            self._ble_unsub = None
        await self._stop_loop()
        await self._store.async_save(self.game.dump())
        await super().async_shutdown()

    async def async_set_enabled(self, enabled: bool) -> None:
        """The Granboard Connection kill switch.

        Off disconnects now and holds no connection (no retries, no advert
        wake-ups) until it is turned back on, so the phone app can connect.
        Stored in the entry options, so it survives restarts.
        """
        if enabled != self.enabled:
            options = {**self.entry.options, CONF_CONNECT: enabled}
            self.hass.config_entries.async_update_entry(self.entry, options=options)
        if enabled:
            self._start_loop()
        else:
            _LOGGER.info("Releasing Granboard %s so another app can connect", self.address)
            await self._stop_loop()
        self.async_update_listeners()

    # ------------------------------------------------------------ connection
    async def _run(self) -> None:
        while not self._stopping and self.enabled:
            try:
                await self._session()
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001 - Bleak errors must not end the loop
                level = logging.INFO if self._attempt == 0 else logging.DEBUG
                _LOGGER.log(level, "Granboard %s not connected: %s", self.address, err)
            self._set_connected(False)
            if self._stopping or not self.enabled:
                break
            delay = backoff_seconds(self._attempt)
            self._attempt += 1
            self._retry_now.clear()
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._retry_now.wait(), timeout=delay)

    async def _session(self) -> None:
        device = bluetooth.async_ble_device_from_address(self.hass, self.address, connectable=True)
        if device is None:
            raise ConnectionError("not visible to any connectable Bluetooth adapter or proxy")
        self._device = device
        await close_stale_connections_by_address(self.address)
        self._disconnected.clear()
        self._buffer.clear()
        self._dedupe.reset()
        client = await establish_connection(
            BleakClientWithServiceCache,
            device,
            self.name,
            self._on_disconnect,
            max_attempts=3,
            ble_device_callback=self._fresh_device,
        )
        self._client = client
        try:
            notify_uuid = self._discover(client)
            self._warmup.arm()
            await client.start_notify(notify_uuid, self._on_notify)
            self._attempt = 0
            self._set_connected(True)
            _LOGGER.info("Connected to Granboard %s, listening on %s", self.address, notify_uuid)
            await self._disconnected.wait()
        finally:
            self._client = None
            self._led_queue.clear()
            with contextlib.suppress(Exception):
                await client.disconnect()

    def _discover(self, client: BleakClientWithServiceCache) -> str:
        """Log every characteristic; pick notify and write ones on the dart service."""
        lines: list[str] = []
        notify: str | None = None
        write: str | None = None
        for service in client.services:
            for char in service.characteristics:
                props = ",".join(char.properties)
                lines.append(f"{service.uuid} / {char.uuid} [{props}] handle={char.handle}")
                if service.uuid.lower() != SERVICE_UUID:
                    continue
                if notify is None and ("notify" in char.properties or "indicate" in char.properties):
                    notify = char.uuid
                if write is None and ("write" in char.properties or "write-without-response" in char.properties):
                    write = char.uuid
                    self._write_response = "write-without-response" not in char.properties
        for line in lines:
            _LOGGER.debug("Granboard %s GATT: %s", self.address, line)
        if notify is None:
            _LOGGER.warning("Granboard %s: no notify characteristic found on %s; trying %s", self.address, SERVICE_UUID, NOTIFY_UUID)
            notify = NOTIFY_UUID
        if write is not None and write.lower() != WRITE_UUID:
            _LOGGER.info("Granboard %s write characteristic is %s (expected %s)", self.address, write, WRITE_UUID)
        self.data.notify_uuid = notify
        self.data.write_uuid = write
        self.data.characteristics = lines
        return notify

    def _fresh_device(self) -> BLEDevice:
        device = bluetooth.async_ble_device_from_address(self.hass, self.address, connectable=True)
        if device is not None:
            self._device = device
        if self._device is None:
            raise BleakError(f"{self.address} disappeared")
        return self._device

    def _on_disconnect(self, _client: Any) -> None:
        self.hass.loop.call_soon_threadsafe(self._disconnected.set)

    async def _disconnect_client(self) -> None:
        client, self._client = self._client, None
        if client is not None:
            with contextlib.suppress(Exception):
                await client.disconnect()

    @callback
    def _on_advertisement(self, info: BluetoothServiceInfoBleak, _change: BluetoothChange) -> None:
        changed = info.rssi != self.data.rssi
        self.data.rssi = info.rssi
        # Released: never reconnect from an advert. The phone app owns the board.
        if self.enabled and not self.data.connected and not self._stopping:
            self._retry_now.set()
        if changed:
            self.async_update_listeners()

    def _set_connected(self, connected: bool) -> None:
        if self.data.connected != connected:
            self.data.connected = connected
            self.hass.loop.call_soon_threadsafe(self.async_update_listeners)

    # ------------------------------------------------------------ frames
    def _on_notify(self, _char: Any, data: bytearray) -> None:
        """Bleak may call this off the event loop."""
        payload = bytes(data)
        self.hass.loop.call_soon_threadsafe(self._handle_payload, payload)

    @callback
    def _handle_payload(self, payload: bytes) -> None:
        _LOGGER.debug("Granboard %s notify %s (%r)", self.address, payload.hex(), payload)
        for frame in self._buffer.feed(payload):
            if not self._warmup.open():
                _LOGGER.debug("Granboard %s ignoring warm-up frame %s", self.address, frame)
                continue
            self._dedupe.set_window_ms(self.debounce_ms)  # Configure changes apply without a reload
            if not self._dedupe.accept(frame):
                _LOGGER.debug("Granboard %s ignoring repeat frame %s", self.address, frame)
                continue
            self.handle_frame(frame)

    @callback
    def handle_frame(self, frame: str) -> None:
        decoded = decode_frame(frame)
        self.data.last_raw = frame
        if isinstance(decoded, Button):
            self.hass.bus.async_fire(EVENT_BUTTON, self._event_base({"raw": decoded.raw}))
            if self.button_next_player and self.game.status == "playing":
                self.next_player()
            self.async_update_listeners()
            return
        if not decoded.known:
            _LOGGER.warning(
                "Granboard %s sent unknown frame %r (bytes %s). Note which bed you hit and report it.",
                self.address,
                frame,
                frame.encode("ascii", "replace").hex(),
            )
        self.record_hit(decoded)

    @callback
    def record_hit(self, hit: Hit) -> None:
        """A dart from the board or the throw service."""
        self.data.last_hit = hit
        self.data.last_hit_time = datetime.now(timezone.utc)
        playing = self.game.status == "playing"
        color = self.game.color_of(self.game.current) if playing else self.game.color_of(None)
        extra = {"player": self.game.player.name, "player_index": self.game.current} if playing else {}
        self.hass.bus.async_fire(EVENT_HIT, self._event_base({**hit.as_dict(), **extra, "color": color}))
        awards: list[dict[str, Any]] = []
        if playing:
            awards = self.game.throw(hit)
            self._fire_awards(awards)
            self._game_changed()
        if self.led_effects:
            self.led_play(led.plan_throw(hit.as_dict(), awards, to_rgb(color)))
        self.async_update_listeners()

    def _event_base(self, data: dict[str, Any]) -> dict[str, Any]:
        return {**data, "address": self.address, "entry_id": self.entry.entry_id}

    def _fire_awards(self, awards: list[dict[str, Any]]) -> None:
        for award in awards:
            self.hass.bus.async_fire(EVENT_AWARD, self._event_base(award))

    # ------------------------------------------------------------ game
    @callback
    def _game_changed(self) -> None:
        self._store.async_delay_save(self.game.dump, 5)
        self.async_update_listeners()

    @callback
    def new_game(self, **kwargs: Any) -> None:
        self.game.new_game(**kwargs)
        self._game_changed()
        if self.led_effects:
            self.led_play(led.plan_new_game(to_rgb(self.game.color_of(0))))

    @callback
    def undo(self) -> None:
        self.game.undo()
        self._game_changed()

    @callback
    def next_player(self) -> None:
        awards = self.game.next_player()
        self._fire_awards(awards)
        self._game_changed()
        steps = [s for a in awards for s in led.plan_award(a)] if self.led_effects else []
        if self.game.status == "playing":
            color = self.game.color_of(self.game.current)
            self.hass.bus.async_fire(
                EVENT_TURN,
                self._event_base(
                    {"player": self.game.player.name, "player_index": self.game.current, "color": color, "round": self.game.round}
                ),
            )
            if self.led_effects:
                steps += led.plan_next_player(to_rgb(color))
        self.led_play(steps)

    @callback
    def end_game(self) -> None:
        self.game.end_game()
        self._game_changed()
        if self.led_effects:
            self.led_play([(led.clear_command(), led.MIN_GAP_MS)])

    # ------------------------------------------------------------ LED ring
    @property
    def can_write(self) -> bool:
        return self._client is not None and self.data.connected and bool(self.data.write_uuid)

    @callback
    def led_play(self, steps: list[led.Step], replace: bool = True) -> None:
        """Queue LED commands. A new effect replaces what is still waiting, so the
        newest dart always lights first and nothing piles up."""
        if not steps or not self.can_write:
            return
        if replace:
            self._led_queue.clear()
        room = LED_QUEUE_MAX - len(self._led_queue)
        self._led_queue.extend(steps[: max(0, room)])
        if self._led_task is None or self._led_task.done():
            self._led_task = self.entry.async_create_background_task(
                self.hass, self._led_worker(), name=f"{DOMAIN}-{self.address}-led"
            )

    async def _led_worker(self) -> None:
        while self._led_queue:
            data, wait_ms = self._led_queue.popleft()
            client, uuid = self._client, self.data.write_uuid
            if client is None or not uuid:
                self._led_queue.clear()
                return
            try:
                await client.write_gatt_char(uuid, data, response=self._write_response)
                self.led_writes += 1
            except Exception as err:  # noqa: BLE001 - never let the ring break hit reading
                _LOGGER.debug("Granboard %s LED write failed: %s", self.address, err)
                self._led_queue.clear()
                return
            await asyncio.sleep(max(led.MIN_GAP_MS, wait_ms) / 1000)

    async def _async_update_data(self) -> BoardData:
        return self.data
