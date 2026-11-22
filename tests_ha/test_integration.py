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
        result["flow_id"], {"button_next_player": True, "auto_next_player": True, "debounce_ms": 300, "led_effects": False}
    )
    assert entry.options["debounce_ms"] == 300 and entry.options["sounds"]["winner"].endswith("win.mp3")
    await hass.config_entries.async_unload(entry.entry_id)


async def test_dart_after_full_turn_goes_to_next_player(hass: HomeAssistant) -> None:
    entry = await _setup(hass, options={"connect": False})
    coordinator = entry.runtime_data
    coordinator._warmup._until = 0
    await hass.services.async_call(DOMAIN, "new_game", {"game": "x01", "start": 301, "players": ["A", "B"]}, blocking=True)
    for frame, gap in ((b"3.4@", 0), (b"3.6@", 0), (b"3.4@", 0)):
        coordinator._dedupe.reset()
        coordinator._handle_payload(frame)
    assert coordinator.game.turn_complete and coordinator.game.current == 0
    coordinator._dedupe.reset()
    coordinator._handle_payload(b"GB7;1013.6@")  # 4th dart, with the connect banner glued on
    await hass.async_block_till_done()
    assert coordinator.game.current == 1 and coordinator.game.players[1].score == 261
    hass.config_entries.async_update_entry(entry, options={**entry.options, "auto_next_player": False})
    for _ in range(3):
        coordinator._dedupe.reset()
        coordinator._handle_payload(b"3.6@")
    assert coordinator.game.current == 1 and coordinator.game.turn_complete
    await hass.config_entries.async_unload(entry.entry_id)


async def _ring_setup(hass: HomeAssistant):
    entry = await _setup(hass, options={"connect": False})
    coordinator = entry.runtime_data
    writes: list[bytes] = []

    class FakeClient:
        async def write_gatt_char(self, uuid, data, response=False):
            writes.append(bytes(data))

    coordinator._client = FakeClient()
    coordinator.data.write_uuid = "442f1572-8a00-9a28-cbe1-e1d4212d53eb"
    coordinator._warmup._until = 0
    coordinator._set_connected(True)
    await hass.async_block_till_done()
    return entry, coordinator, writes


async def test_led_ring_light_solid_pause_and_resume(hass: HomeAssistant) -> None:
    from custom_components.granboard import led

    ring = "light.granboard_5547_led_ring"
    real_sleep = __import__("asyncio").sleep

    async def fast_sleep(*_args):
        await real_sleep(0)  # still yields, like a real wait

    with patch(f"{CO}.asyncio.sleep", new=fast_sleep):
        entry, coordinator, writes = await _ring_setup(hass)
        assert hass.states.get(ring).state == "off"
        assert hass.states.get(ring).attributes["effect_list"][:3] == ["Solid", "Blink", "Breathe"]
        await hass.services.async_call(
            "light", "turn_on", {"entity_id": ring, "rgb_color": [255, 0, 0], "brightness": 128}, blocking=True
        )
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [led.ring_command((128, 0, 0))]
        state = hass.states.get(ring)
        assert state.state == "on" and state.attributes["paused_for_game"] is False
        writes.clear()

        # A game takes over: the light stays on but paused, and writes nothing of its own.
        await hass.services.async_call("granboard", "new_game", {"game": "501", "players": ["Andrew"]}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert hass.states.get(ring).attributes["paused_for_game"] is True
        assert led.ring_command((128, 0, 0)) not in writes
        writes.clear()
        coordinator._handle_payload(b"3.4@")
        await hass.async_block_till_done(wait_background_tasks=True)
        assert led.ring_command((128, 0, 0)) not in writes
        writes.clear()

        # Clearing the game brings the light back after the game effects.
        await hass.services.async_call("granboard", "end_game", {}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [bytes(20), led.ring_command((128, 0, 0))]
        assert hass.states.get(ring).attributes["paused_for_game"] is False
        writes.clear()

        # A hit outside a game flashes, then the light comes back.
        await hass.services.async_call("granboard", "throw", {"segment": "S5"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes[0][0] == led.HIT_SINGLE and writes[-1] == led.ring_command((128, 0, 0))
        writes.clear()

        await hass.services.async_call("light", "turn_off", {"entity_id": ring}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [bytes(20)]
        writes.clear()

        # Offline: nothing is written. Back online with the light on: it is re-applied.
        await hass.services.async_call("light", "turn_on", {"entity_id": ring, "brightness": 255}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        writes.clear()
        client = coordinator._client
        coordinator._client = None
        coordinator._set_connected(False)
        await hass.async_block_till_done(wait_background_tasks=True)
        await hass.services.async_call("light", "turn_on", {"entity_id": ring, "rgb_color": [0, 0, 255]}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == []
        coordinator._client = client
        coordinator._set_connected(True)
        await real_sleep(0)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [led.ring_command((0, 0, 255))]
    coordinator._client = None
    await hass.config_entries.async_unload(entry.entry_id)


async def test_led_ring_effect_loop_starts_and_cancels(hass: HomeAssistant) -> None:
    import asyncio

    from custom_components.granboard import led

    ring = "light.granboard_5547_led_ring"
    real_sleep = asyncio.sleep
    gate = asyncio.Event()
    loop_waits: list[float] = []

    async def fake_sleep(seconds, *args):
        if seconds >= led.AMBIENT_MIN_GAP_MS / 1000 and seconds < 1:  # ambient loop gaps
            loop_waits.append(seconds)
            if len(loop_waits) >= 3:
                await gate.wait()  # hold the loop here until it is cancelled
        await real_sleep(0)

    with patch(f"{CO}.asyncio.sleep", new=fake_sleep):
        entry, coordinator, writes = await _ring_setup(hass)
        await hass.services.async_call(
            "light", "turn_on", {"entity_id": ring, "rgb_color": [0, 255, 0], "effect": "Circular Wipe"}, blocking=True
        )
        for _ in range(50):
            await real_sleep(0)
        assert [w[10] for w in writes] == [led.LED_POSITIONS[n] for n in led.CLOCKWISE_ORDER[:3]]
        assert all(w[0] == led.HIT_SINGLE and w[1:4] == bytes((0, 255, 0)) for w in writes)
        assert min(loop_waits) >= 0.25
        light = hass.data["light"].get_entity(ring)
        task = light._task
        assert task is not None and not task.done()

        # A new game cancels the loop.
        await hass.services.async_call("granboard", "new_game", {"game": "501", "players": ["Andrew"]}, blocking=True)
        for _ in range(10):
            await real_sleep(0)
        assert task.done() and light._task is None
        await hass.services.async_call("granboard", "end_game", {}, blocking=True)
        for _ in range(50):
            await real_sleep(0)
        assert light._task is not None and not light._task.done()

        # Turning off cancels the loop and clears the ring.
        task = light._task
        writes.clear()
        await hass.services.async_call("light", "turn_off", {"entity_id": ring}, blocking=True)
        for _ in range(10):
            await real_sleep(0)
        assert task.done() and writes[-1] == bytes(20)
    coordinator._client = None
    await hass.config_entries.async_unload(entry.entry_id)


async def test_led_ring_restores_last_state(hass: HomeAssistant) -> None:
    from pytest_homeassistant_custom_component.common import mock_restore_cache

    from homeassistant.core import State

    mock_restore_cache(
        hass,
        [State("light.granboard_5547_led_ring", "on", {"rgb_color": [0, 0, 255], "brightness": 64, "effect": "Chase"})],
    )
    entry = await _setup(hass, options={"connect": False})
    state = hass.states.get("light.granboard_5547_led_ring")
    assert state.state == "on"
    assert tuple(state.attributes["rgb_color"]) == (0, 0, 255)
    assert state.attributes["brightness"] == 64 and state.attributes["effect"] == "Chase"
    coordinator = entry.runtime_data
    assert coordinator._led_listeners  # listening for game effects
    await hass.config_entries.async_unload(entry.entry_id)
    assert not coordinator._led_listeners


async def test_ring_settings_entities_drive_the_light(hass: HomeAssistant) -> None:
    import asyncio

    from homeassistant.exceptions import HomeAssistantError
    from pytest_homeassistant_custom_component.common import mock_restore_cache_with_extra_data

    from homeassistant.core import State

    from custom_components.granboard import led
    from custom_components.granboard import palettes as P

    dev = "granboard_5547"
    mock_restore_cache_with_extra_data(
        hass,
        [(State(f"select.{dev}_ring_palette", "Ocean"), {}), (State(f"text.{dev}_ring_color_2", "#00ff00"), {}),
         (State(f"number.{dev}_ring_speed", "200"), {"native_value": 200, "native_min_value": 0, "native_max_value": 255,
                                                       "native_step": 1, "native_unit_of_measurement": None})],
    )
    real_sleep = asyncio.sleep
    gate = asyncio.Event()
    gaps: list[float] = []

    async def fake_sleep(seconds, *args):
        if 0.25 <= seconds < 1:
            gaps.append(seconds)
            if len(gaps) >= 2:
                await gate.wait()
        await real_sleep(0)

    with patch(f"{CO}.asyncio.sleep", new=fake_sleep):
        entry, coordinator, writes = await _ring_setup(hass)
        assert hass.states.get(f"select.{dev}_ring_palette").state == "Ocean"
        assert "Orange & Teal" in hass.states.get(f"select.{dev}_ring_palette").attributes["options"]
        assert hass.states.get(f"number.{dev}_ring_speed").state == "200.0"
        assert hass.states.get(f"number.{dev}_ring_intensity").state == "128.0"
        assert hass.states.get(f"text.{dev}_ring_color_2").state == "#00ff00"
        assert coordinator.ring_settings == {"palette": "Ocean", "speed": 200, "intensity": 128, "color2": "#00ff00"}

        ring = f"light.{dev}_led_ring"
        await hass.services.async_call("light", "turn_on", {"entity_id": ring, "rgb_color": [255, 0, 0], "effect": "Chase"}, blocking=True)
        for _ in range(30):
            await real_sleep(0)
        first = P.color_at("Ocean", 0, (255, 0, 0), (0, 255, 0))
        assert writes[0][0] == led.HIT_SINGLE and writes[0][1:4] == bytes(first)
        assert gaps[0] == 0.25  # speed 200 hits the 250 ms floor, never faster

        # Changing the palette restarts the effect in the new colours.
        task = hass.data["light"].get_entity(ring)._task
        writes.clear()
        gaps.clear()
        await hass.services.async_call("select", "select_option", {"entity_id": f"select.{dev}_ring_palette", "option": "Heat"}, blocking=True)
        for _ in range(30):
            await real_sleep(0)
        assert task.done()
        assert writes[0][1:4] == bytes(P.color_at("Heat", 0, (255, 0, 0), (0, 255, 0)))

        await hass.services.async_call("number", "set_value", {"entity_id": f"number.{dev}_ring_intensity", "value": 40}, blocking=True)
        assert coordinator.ring_settings["intensity"] == 40
        await hass.services.async_call("text", "set_value", {"entity_id": f"text.{dev}_ring_color_2", "value": ""}, blocking=True)
        assert coordinator.ring_settings["color2"] == "" and hass.states.get(f"text.{dev}_ring_color_2").state == ""
        try:
            await hass.services.async_call("text", "set_value", {"entity_id": f"text.{dev}_ring_color_2", "value": "#12345"}, blocking=True)
        except (HomeAssistantError, ValueError):
            pass
        assert coordinator.ring_settings["color2"] == ""
        await hass.services.async_call("light", "turn_off", {"entity_id": ring}, blocking=True)
    coordinator._client = None
    await hass.config_entries.async_unload(entry.entry_id)


async def test_options_flow_wled_lights(hass: HomeAssistant) -> None:
    entry = await _setup(hass, options={"connect": False})
    hass.states.async_set("light.tree", "on")
    hass.states.async_set("light.shelf", "on")
    flow = await hass.config_entries.options.async_init(entry.entry_id)
    assert "wled" in flow["menu_options"]
    menu = await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled"})
    assert menu["menu_options"] == ["wled_settings", "wled_add"]
    form = await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled_add"})
    done = await hass.config_entries.options.async_configure(flow["flow_id"], {"entity_id": "light.tree", "position": "left", "angle": 0, "spread": 0})
    assert done["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["wled_lights"] == [{"entity_id": "light.tree", "position": "left", "angle": 0.0, "spread": 0.0}]

    flow = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled"})
    await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled_add"})
    dup = await hass.config_entries.options.async_configure(flow["flow_id"], {"entity_id": "light.tree", "position": "top"})
    assert dup["errors"] == {"entity_id": "already_added"}
    await hass.config_entries.options.async_configure(flow["flow_id"], {"entity_id": "light.shelf", "position": "custom", "angle": 100, "spread": 60})

    flow = await hass.config_entries.options.async_init(entry.entry_id)
    menu = await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled"})
    assert menu["menu_options"] == ["wled_settings", "wled_add", "wled_edit", "wled_remove"]
    await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled_edit"})
    form = await hass.config_entries.options.async_configure(flow["flow_id"], {"entity_id": "light.tree"})
    assert form["step_id"] == "wled_edit_light"
    await hass.config_entries.options.async_configure(flow["flow_id"], {"position": "top_right", "angle": 0, "spread": 30})
    assert entry.options["wled_lights"][0]["position"] == "top_right" and entry.options["wled_lights"][0]["spread"] == 30
    assert entry.options["wled_lights"][1] == {"entity_id": "light.shelf", "position": "custom", "angle": 100.0, "spread": 60.0}

    flow = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled"})
    await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled_settings"})
    await hass.config_entries.options.async_configure(flow["flow_id"], {"wled_enabled": True, "wled_flash_ms": 900, "wled_only_on": True})
    assert entry.options["wled_flash_ms"] == 900 and entry.runtime_data.wled.flash_ms == 900

    flow = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled"})
    await hass.config_entries.options.async_configure(flow["flow_id"], {"next_step_id": "wled_remove"})
    await hass.config_entries.options.async_configure(flow["flow_id"], {"lights": ["light.tree"]})
    assert [l["entity_id"] for l in entry.options["wled_lights"]] == ["light.shelf"]
    assert entry.options["connect"] is False  # other options kept
    await hass.config_entries.async_unload(entry.entry_id)


async def test_wled_sections_flash_and_restore_only_lights_that_were_on(hass: HomeAssistant) -> None:
    from pytest_homeassistant_custom_component.common import async_mock_service

    lights = [
        {"entity_id": "light.top", "position": "top"},
        {"entity_id": "light.right", "position": "right"},
        {"entity_id": "light.bottom", "position": "bottom"},
        {"entity_id": "light.left", "position": "left"},
    ]
    entry = await _setup(hass, options={"connect": False, "wled_lights": lights, "wled_flash_ms": 200})
    hass.states.async_set("light.top", "on", {"color_mode": "rgb", "rgb_color": (10, 20, 30), "brightness": 77,
                                              "effect": "Solid", "effect_list": ["Solid", "Rainbow"]})
    hass.states.async_set("light.right", "on", {"color_mode": "color_temp", "color_temp_kelvin": 3000, "brightness": 200})
    hass.states.async_set("light.bottom", "off", {})
    hass.states.async_set("light.left", "on", {"color_mode": "hs", "hs_color": (120, 50), "brightness": 10,
                                               "effect": "Rainbow", "effect_list": ["Solid", "Rainbow"]})
    on = async_mock_service(hass, "light", "turn_on")
    off = async_mock_service(hass, "light", "turn_off")
    coordinator = entry.runtime_data

    async def wait_done():
        task = coordinator.wled._task
        if task is not None:
            await task
        await hass.async_block_till_done()

    await hass.services.async_call("granboard", "throw", {"segment": "S20"}, blocking=True)
    await wait_done()
    by = [(c.data["entity_id"], c.data) for c in on]
    flashes = {e: d["brightness"] for e, d in by if d.get("rgb_color") == [255, 0, 0]}
    # Three lights are on (120 degrees each): the top is full, its neighbours glow softly.
    assert flashes["light.top"] == 255 and 0 < flashes["light.right"] < 255 and 0 < flashes["light.left"] < 255
    restored = {e: d for e, d in by if d.get("rgb_color") != [255, 0, 0]}
    assert restored["light.top"] == {"entity_id": "light.top", "transition": 0.2, "brightness": 77, "rgb_color": [10, 20, 30]}
    assert all(e != "light.bottom" for e, _ in by) and not off
    on.clear()

    # A turn change sweeps round the lights that are on, in board order, and puts each back.
    await hass.services.async_call("granboard", "new_game", {"game": "501", "players": ["A", "B"], "colors": ["red", "blue"]}, blocking=True)
    await wait_done()
    on.clear()
    await hass.services.async_call("granboard", "next_player", {}, blocking=True)
    await wait_done()
    sets = [c.data["entity_id"] for c in on if c.data.get("rgb_color") == [0, 0, 255]]
    assert sets == ["light.top", "light.right", "light.left"]  # bottom is off: skipped
    restores = {c.data["entity_id"]: c.data for c in on if c.data.get("rgb_color") != [0, 0, 255]}
    assert restores["light.right"]["color_temp_kelvin"] == 3000 and restores["light.right"]["brightness"] == 200
    assert restores["light.left"]["effect"] == "Rainbow" and restores["light.left"]["hs_color"] == [120, 50]
    assert not off
    on.clear()

    # A new hit interrupts a running sweep; the lights still go back to the original look.
    coordinator.wled.turn((0, 255, 0))
    await asyncio_sleep(0.05)
    coordinator.wled.throw({"ring": "single_inner", "number": 11}, [], (255, 0, 0))
    await wait_done()
    last = {c.data["entity_id"]: c.data for c in on}
    assert last["light.top"]["rgb_color"] == [10, 20, 30]
    assert last["light.left"]["effect"] == "Rainbow"

    # Switched off in Configure: nothing happens.
    on.clear()
    hass.config_entries.async_update_entry(entry, options={**entry.options, "wled_enabled": False})
    await hass.services.async_call("granboard", "throw", {"segment": "T20"}, blocking=True)
    await wait_done()
    assert not on
    await hass.config_entries.async_unload(entry.entry_id)


async def asyncio_sleep(seconds):
    import asyncio

    await asyncio.sleep(seconds)


async def test_wled_sections_use_wled_json_api(hass: HomeAssistant, aioclient_mock) -> None:
    from homeassistant.helpers import entity_registry as er

    wled_entry = MockConfigEntry(domain="wled", data={"host": "10.0.0.50"})
    wled_entry.add_to_hass(hass)
    er.async_get(hass).async_get_or_create("light", "wled", "aabbccddeeff", config_entry=wled_entry, suggested_object_id="tree")
    hass.states.async_set("light.tree", "on", {"brightness": 128})
    saved = {"on": True, "bri": 128, "ps": 3, "seg": [{"id": 0, "n": "Tree", "col": [[1, 2, 3]], "fx": 9, "pal": 6}]}
    aioclient_mock.get("http://10.0.0.50/json/state", json=saved)
    aioclient_mock.post("http://10.0.0.50/json/state", json={"success": True})
    entry = await _setup(hass, options={"connect": False, "wled_lights": [{"entity_id": "light.tree", "position": "top"}], "wled_flash_ms": 200})
    coordinator = entry.runtime_data
    coordinator.wled.throw({"ring": "double", "number": 20}, [], (255, 0, 0))
    await coordinator.wled._task
    posts = [call[2] for call in aioclient_mock.mock_calls if call[0] == "POST"]
    assert posts[0] == {"on": True, "bri": 255, "tt": 1, "seg": [{"id": 0, "col": [[255, 0, 0]], "fx": 0}]}
    assert posts[-1]["on"] is True and posts[-1]["bri"] == 128
    assert posts[-1]["seg"] == [{"id": 0, "col": [[1, 2, 3]], "fx": 9, "pal": 6}]  # no preset reload, name untouched
    assert "ps" not in posts[-1]
    await hass.config_entries.async_unload(entry.entry_id)


async def test_led_raw_test_frame_holds_ring_light_until_clear(hass: HomeAssistant) -> None:
    import asyncio

    import pytest as _pytest
    from homeassistant.exceptions import ServiceValidationError

    from custom_components.granboard import led

    ring = "light.granboard_5547_led_ring"
    real_sleep = asyncio.sleep

    async def fast_sleep(*_args):
        await real_sleep(0)

    with patch(f"{CO}.asyncio.sleep", new=fast_sleep):
        entry, coordinator, writes = await _ring_setup(hass)
        await hass.services.async_call("light", "turn_on", {"entity_id": ring, "rgb_color": [0, 255, 0]}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        writes.clear()
        await hass.services.async_call("granboard", "led", {"effect": "raw", "raw": "10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [bytes([0x10]) + bytes(15)]  # exactly one frame; the ring light does not come back over it
        assert hass.states.get(ring).attributes["paused_for_raw_frame"] is True
        for bad in ("20" + "00" * 15, "10 00", "08" + "00" * 19):
            with _pytest.raises((ServiceValidationError, ValueError)):
                await hass.services.async_call("granboard", "led", {"effect": "raw", "raw": bad}, blocking=True)
        assert writes == [bytes([0x10]) + bytes(15)]
        # Clear ends the test and the ring light returns.
        await hass.services.async_call("granboard", "led", {"effect": "clear"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes[1:] == [bytes(20), led.ring_command((0, 255, 0))]
        assert hass.states.get(ring).attributes["paused_for_raw_frame"] is False
        # Released board: nothing is sent.
        coordinator._client = None
        coordinator._set_connected(False)
        with _pytest.raises(ServiceValidationError):
            await hass.services.async_call("granboard", "led", {"effect": "raw", "raw": "10" + "00" * 15}, blocking=True)
    await hass.config_entries.async_unload(entry.entry_id)


async def test_rainbow_sweep_effect_and_service(hass: HomeAssistant) -> None:
    import asyncio

    from custom_components.granboard import led

    ring = "light.granboard_5547_led_ring"
    real_sleep = asyncio.sleep

    async def fast_sleep(*_args):
        await real_sleep(0)

    with patch(f"{CO}.asyncio.sleep", new=fast_sleep):
        entry, coordinator, writes = await _ring_setup(hass)
        assert "Rainbow Sweep" in hass.states.get(ring).attributes["effect_list"]
        await hass.services.async_call("light", "turn_on", {"entity_id": ring, "effect": "Rainbow Sweep"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [led.rainbow_command()]  # one write; the board animates by itself
        await hass.services.async_call("select", "select_option", {"entity_id": "select.granboard_5547_ring_palette", "option": "Lava"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [led.rainbow_command()]  # palette does not apply: nothing re-sent
        # Resumes with one write after a game.
        await hass.services.async_call("granboard", "new_game", {"game": "501", "players": ["A"]}, blocking=True)
        await hass.services.async_call("granboard", "end_game", {}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes[-1] == led.rainbow_command()
        await hass.services.async_call("light", "turn_off", {"entity_id": ring}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        writes.clear()
        await hass.services.async_call("granboard", "led", {"effect": "rainbow"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes == [led.rainbow_command()] and coordinator.led_hold is True
        await hass.services.async_call("granboard", "led", {"effect": "clear"}, blocking=True)
        await hass.async_block_till_done(wait_background_tasks=True)
        assert writes[-1] == bytes(20) and coordinator.led_hold is False
    coordinator._client = None
    await hass.config_entries.async_unload(entry.entry_id)
