from __future__ import annotations

from unittest.mock import patch

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
