from __future__ import annotations

from unittest.mock import AsyncMock, patch

import custom_components.granboard  # noqa: F401
import custom_components.granboard.config_flow  # noqa: F401
import custom_components.granboard.coordinator  # noqa: F401
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

DOMAIN = "granboard"
ADDRESS = "CA:0F:52:F5:55:47"
CO = "custom_components.granboard.coordinator"


async def _setup(hass: HomeAssistant, options=None) -> MockConfigEntry:
    hass.config.components.add("bluetooth")
    entry = MockConfigEntry(domain=DOMAIN, unique_id=ADDRESS, data={"address": ADDRESS}, title="Granboard 5547", options=options or {})
    entry.add_to_hass(hass)
    with patch(f"{CO}.bluetooth.async_last_service_info", return_value=None), patch(
        f"{CO}.async_register_callback", return_value=lambda: None
    ), patch(f"{CO}.bluetooth.async_ble_device_from_address", return_value=None):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_manual_flow(hass: HomeAssistant) -> None:
    hass.config.components.add("bluetooth")
    with patch("custom_components.granboard.config_flow.async_discovered_service_info", return_value=[]):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
        assert result["type"] is FlowResultType.FORM
        bad = await hass.config_entries.flow.async_configure(result["flow_id"], {"address": "nope"})
        assert bad["errors"] == {"address": "invalid_address"}
        with patch("custom_components.granboard.async_setup_entry", return_value=True):
            done = await hass.config_entries.flow.async_configure(result["flow_id"], {"address": ADDRESS.lower()})
    assert done["type"] is FlowResultType.CREATE_ENTRY
    assert done["data"] == {"address": ADDRESS}


async def test_entities_game_and_kill_switch(hass: HomeAssistant) -> None:
    entry = await _setup(hass)
    coordinator = entry.runtime_data
    assert hass.states.get("switch.granboard_5547_granboard_connection").state == "on"
    assert hass.states.get("binary_sensor.granboard_5547_connected").state == "off"
    assert hass.states.get("sensor.granboard_5547_game").state == "idle"

    hits, awards = [], []
    hass.bus.async_listen("granboard_hit", lambda e: hits.append(e.data))
    hass.bus.async_listen("granboard_award", lambda e: awards.append(e.data))
    await hass.services.async_call(DOMAIN, "new_game", {"game": "x01", "start": 301, "players": ["Andrew", "Guest"]}, blocking=True)
    for seg in ("T20", "T20", "T20"):
        await hass.services.async_call(DOMAIN, "throw", {"segment": seg}, blocking=True)
    await hass.async_block_till_done()
    game = hass.states.get("sensor.granboard_5547_game")
    assert game.state == "playing"
    assert game.attributes["players"][0]["score"] == 121
    assert hits[0]["segment"] == "T20" and hits[0]["score"] == 60
    assert [a["type"] for a in awards] == ["ton_80"]
    assert hass.states.get("sensor.granboard_5547_last_hit").state == "T20"

    # Board frames: button ends the turn, unknown frames are reported.
    coordinator.handle_frame("BTN@")
    coordinator.handle_frame("42.42@")
    await hass.async_block_till_done()
    assert coordinator.game.player.name == "Guest"
    assert hits[-1]["segment"] == "unknown"
    await hass.services.async_call(DOMAIN, "undo", {}, blocking=True)
    assert coordinator.game.player.name == "Andrew"

    # Release Board turns the kill switch off and stops the loop.
    await hass.services.async_call("button", "press", {"entity_id": "button.granboard_5547_release_board"}, blocking=True)
    await hass.async_block_till_done()
    assert hass.states.get("switch.granboard_5547_granboard_connection").state == "off"
    assert entry.options["connect"] is False
    assert coordinator._task is None
    coordinator._retry_now.clear()
    coordinator._on_advertisement(type("I", (), {"rssi": -70})(), None)
    assert not coordinator._retry_now.is_set()
    assert hass.states.get("sensor.granboard_5547_signal_strength").state == "-70"

    await hass.config_entries.async_unload(entry.entry_id)


async def test_released_state_survives_restart(hass: HomeAssistant) -> None:
    with patch(f"{CO}.GranboardCoordinator._start_loop") as start:
        entry = await _setup(hass, options={"connect": False})
        assert not start.called
    assert hass.states.get("switch.granboard_5547_granboard_connection").state == "off"
    with patch(f"{CO}.GranboardCoordinator._start_loop") as start:
        await hass.services.async_call("switch", "turn_on", {"entity_id": "switch.granboard_5547_granboard_connection"}, blocking=True)
        assert start.called
    assert entry.options["connect"] is True
    await hass.config_entries.async_unload(entry.entry_id)


async def test_discovery_and_warmup(hass: HomeAssistant) -> None:
    from types import SimpleNamespace as NS

    entry = await _setup(hass, options={"connect": False})
    coordinator = entry.runtime_data
    svc = "442f1570-8a00-9a28-cbe1-e1d4212d53eb"
    client = NS(services=[
        NS(uuid="0000180a-0000-1000-8000-00805f9b34fb", characteristics=[NS(uuid="00002a29-0000-1000-8000-00805f9b34fb", properties=["read"], handle=3)]),
        NS(uuid=svc, characteristics=[
            NS(uuid="442f1571-8a00-9a28-cbe1-e1d4212d53eb", properties=["notify"], handle=10),
            NS(uuid="442f1572-8a00-9a28-cbe1-e1d4212d53eb", properties=["write-without-response"], handle=13),
        ]),
    ])
    assert coordinator._discover(client) == "442f1571-8a00-9a28-cbe1-e1d4212d53eb"
    assert coordinator.data.write_uuid == "442f1572-8a00-9a28-cbe1-e1d4212d53eb"
    assert len(coordinator.data.characteristics) == 3

    hits = []
    hass.bus.async_listen("granboard_hit", lambda e: hits.append(e.data))
    coordinator._warmup.arm()
    coordinator._handle_payload(b"3.4@")  # replayed on connect: dropped
    coordinator._warmup._until = 0
    coordinator._handle_payload(b"4.")
    coordinator._handle_payload(b"0@")
    await hass.async_block_till_done()
    assert [h["segment"] for h in hits] == ["DB"]
    assert hits[0]["ring"] == "bullseye" and hits[0]["raw"] == "4.0@"
    await hass.config_entries.async_unload(entry.entry_id)


async def test_repeat_frames_count_once(hass: HomeAssistant) -> None:
    entry = await _setup(hass, options={"connect": False})
    coordinator = entry.runtime_data
    coordinator._warmup._until = 0
    clock = [10.0]
    coordinator._dedupe._clock = lambda: clock[0]
    hits = []
    from homeassistant.core import callback

    hass.bus.async_listen("granboard_hit", callback(lambda e: hits.append(e.data["segment"])))
    for dt in (0, 0.06, 0.15):  # one press, three frames
        clock[0] += dt
        coordinator._handle_payload(b"3.4@")
    clock[0] += 0.01
    coordinator._handle_payload(b"3.6@")  # different bed: counts
    clock[0] += 0.7
    coordinator._handle_payload(b"3.6@")  # same bed, later: a new dart
    await hass.async_block_till_done()
    assert hits == ["T20", "D20", "D20"]
    hass.config_entries.async_update_entry(entry, options={**entry.options, "debounce_ms": 0})
    coordinator._handle_payload(b"3.6@")
    await hass.async_block_till_done()
    assert hits[-1] == "D20" and len(hits) == 4
    await hass.config_entries.async_unload(entry.entry_id)


async def test_led_effects_follow_hits_turns_and_service(hass: HomeAssistant) -> None:
    from homeassistant.core import callback

    from custom_components.granboard import led

    entry = await _setup(hass, options={"connect": False})
    coordinator = entry.runtime_data
    writes: list[tuple[str, bytes, bool]] = []

    class FakeClient:
        async def write_gatt_char(self, uuid, data, response=False):
            writes.append((uuid, bytes(data), response))

    coordinator._client = FakeClient()
    coordinator.data.connected = True
    coordinator.data.write_uuid = "442f1572-8a00-9a28-cbe1-e1d4212d53eb"
    coordinator._warmup._until = 0
    turns = []
    hits = []
    hass.bus.async_listen("granboard_turn", callback(lambda e: turns.append(e.data)))
    hass.bus.async_listen("granboard_hit", callback(lambda e: hits.append(e.data)))
    with patch(f"{CO}.asyncio.sleep", new=AsyncMock()):
        await hass.services.async_call(
            "granboard", "new_game", {"game": "501", "players": ["Andrew", "Guest"], "colors": ["green"]}, blocking=True
        )
        await hass.async_block_till_done()
        assert len(writes) == 22  # clear + 20-step sweep + blink
        writes.clear()
        for _ in range(3):  # one physical press = three identical frames
            coordinator._handle_payload(b"3.4@")
        await hass.async_block_till_done()
        assert hits[-1]["color"] == "#00ff00" and hits[-1]["player"] == "Andrew" and len(hits) == 1
        assert [w[1][0] for w in writes] == [3, led.WAVE]  # triple 20: 3 blinks + wave
        assert writes[0][1][1:4] == bytes((0x00, 0xFF, 0x00))
        writes.clear()
        await hass.services.async_call("granboard", "next_player", {}, blocking=True)
        await hass.async_block_till_done()
        assert turns[-1]["player"] == "Guest" and turns[-1]["color"] == "#0000ff"
        assert len(writes) == 21 and writes[-1][1] == bytes(20)  # circular wipe, then clear
        writes.clear()
        await hass.services.async_call("granboard", "led", {"effect": "blink", "color": "red"}, blocking=True)
        await hass.async_block_till_done()
        assert writes[0][1][0] == led.BLINK and writes[0][1][1:4] == bytes((0xFF, 0x00, 0x00))
        writes.clear()
        hass.config_entries.async_update_entry(entry, options={**entry.options, "led_effects": False})
        await hass.services.async_call("granboard", "throw", {"segment": "S5"}, blocking=True)
        await hass.async_block_till_done()
        assert writes == []
    coordinator._client = None
    await hass.config_entries.async_unload(entry.entry_id)


async def test_sounds_play_on_configured_player(hass: HomeAssistant) -> None:
    from homeassistant.core import callback

    entry = await _setup(
        hass,
        options={
            "connect": False,
            "sound_player": "media_player.game_room",
            "sounds": {"triple_20": "/local/granboard/sounds/t20.mp3", "ton_80": "/local/granboard/sounds/180.mp3", "next_player": "/local/granboard/sounds/clear.mp3"},
            "sound_volumes": {"ton_80": 90},
        },
    )
    hass.config.external_url = "https://example.ui.nabu.casa"
    calls = []

    async def record(call):
        calls.append((call.service, dict(call.data)))

    hass.services.async_register("media_player", "play_media", record)
    hass.services.async_register("media_player", "volume_set", record)
    sounds = []
    hass.bus.async_listen("granboard_sound", callback(lambda e: sounds.append(e.data["sound"])))
    signer = patch(
        "homeassistant.components.media_player.async_process_play_media_url", side_effect=lambda _h, u: "https://example" + u
    )
    signer.start()
    await hass.services.async_call("granboard", "new_game", {"game": "501", "players": ["A", "B"]}, blocking=True)
    await hass.services.async_call("granboard", "throw", {"segment": "T20"}, blocking=True)
    await hass.async_block_till_done()
    assert calls[-1][0] == "play_media" and calls[-1][1]["media_content_id"].endswith("/local/granboard/sounds/t20.mp3")
    assert not any(c[0] == "volume_set" for c in calls)
    await hass.services.async_call("granboard", "throw", {"segment": "T20"}, blocking=True)
    await hass.services.async_call("granboard", "throw", {"segment": "T20"}, blocking=True)
    await hass.async_block_till_done()
    assert ("volume_set", {"entity_id": "media_player.game_room", "volume_level": 0.6}) in calls  # 90 % capped to 60 %
    assert calls[-1][1]["media_content_id"].endswith("180.mp3")
    await hass.services.async_call("granboard", "next_player", {}, blocking=True)
    await hass.async_block_till_done()
    signer.stop()
    assert sounds == ["triple_20", "triple_20", "ton_80", "next_player"]
    await hass.config_entries.async_unload(entry.entry_id)


async def test_options_menu_sounds_and_volumes(hass: HomeAssistant) -> None:
    entry = await _setup(hass, options={"connect": False})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == "menu"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"next_step_id": "sounds"})
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"sound_player": "media_player.game_room", "winner": "/local/granboard/sounds/win.mp3", "bust": " "}
    )
    assert entry.options["sounds"] == {"winner": "/local/granboard/sounds/win.mp3"}
    assert entry.options["connect"] is False  # kill switch state kept
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"next_step_id": "volumes"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"winner": 50})
    assert entry.options["sound_volumes"] == {"winner": 50}
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"next_step_id": "general"})
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"button_next_player": True, "debounce_ms": 300, "led_effects": False}
    )
    assert entry.options["debounce_ms"] == 300 and entry.options["sounds"]["winner"].endswith("win.mp3")
    await hass.config_entries.async_unload(entry.entry_id)
