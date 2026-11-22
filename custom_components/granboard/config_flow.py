"""Config flow: Bluetooth discovery, or pick / type the board address."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AUTO_NEXT,
    CONF_BUTTON_NEXT,
    CONF_DEBOUNCE_MS,
    CONF_LED_FX,
    CONF_ALEXA_AUDIO,
    CONF_SOUND_PLAYER,
    CONF_SOUND_VOLUMES,
    CONF_SOUNDS,
    DEFAULT_ALEXA_AUDIO,
    CONF_WLED_ENABLED,
    CONF_WLED_FLASH_MS,
    CONF_WLED_LIGHTS,
    CONF_WLED_ONLY_ON,
    DEFAULT_AUTO_NEXT,
    DEFAULT_BUTTON_NEXT,
    DEFAULT_DEBOUNCE_MS,
    DEFAULT_LED_FX,
    DEFAULT_WLED_FLASH_MS,
    DOMAIN,
)
from .sections import CUSTOM, POSITIONS
from .sounds import SOUND_KEYS
from .protocol import BOARD_NAME, SERVICE_UUID

_MAC = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$")


def is_granboard(info: BluetoothServiceInfoBleak) -> bool:
    """Name starts with GRANBOARD or the dart service is advertised."""
    names = (
        getattr(info, "name", None),
        getattr(getattr(info, "advertisement", None), "local_name", None),
        getattr(getattr(info, "device", None), "name", None),
    )
    if any(isinstance(n, str) and n.upper().startswith(BOARD_NAME) for n in names):
        return True
    return SERVICE_UUID in {u.lower() for u in (info.service_uuids or [])}


class GranboardConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add a Granboard."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovery: BluetoothServiceInfoBleak | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return GranboardOptionsFlow()

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> ConfigFlowResult:
        if not is_granboard(discovery_info):
            return self.async_abort(reason="not_supported")
        await self.async_set_unique_id(discovery_info.address.upper())
        self._abort_if_unique_id_configured()
        self._discovery = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name or BOARD_NAME}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        assert self._discovery is not None
        if user_input is not None:
            return self._create(self._discovery.address.upper(), self._discovery.name)
        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self._discovery.name or BOARD_NAME, "address": self._discovery.address},
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            address = str(user_input[CONF_ADDRESS]).strip().upper().replace("-", ":")
            if not _MAC.match(address):
                errors[CONF_ADDRESS] = "invalid_address"
            else:
                await self.async_set_unique_id(address, raise_on_progress=False)
                self._abort_if_unique_id_configured()
                return self._create(address, None)
        current = self._async_current_ids(include_ignore=False)
        found = [
            {"value": info.address.upper(), "label": f"{info.name or BOARD_NAME} ({info.address})"}
            for info in async_discovered_service_info(self.hass, connectable=True)
            if is_granboard(info) and info.address.upper() not in current
        ]
        schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS, default=found[0]["value"] if found else ""): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=found, custom_value=True, mode=selector.SelectSelectorMode.DROPDOWN)
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    def _create(self, address: str, name: str | None) -> ConfigFlowResult:
        title = name if name and name.upper() != BOARD_NAME else f"Granboard {address[-5:].replace(':', '')}"
        return self.async_create_entry(title=title, data={CONF_ADDRESS: address})


class GranboardOptionsFlow(OptionsFlow):
    """General settings, sounds, and sound volumes."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(step_id="init", menu_options=["general", "sounds", "volumes", "wled"])

    def _save(self, **changes: Any) -> ConfigFlowResult:
        return self.async_create_entry(data={**self.config_entry.options, **changes})

    async def async_step_general(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self._save(**user_input)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(CONF_BUTTON_NEXT, default=options.get(CONF_BUTTON_NEXT, DEFAULT_BUTTON_NEXT)): bool,
                vol.Required(CONF_AUTO_NEXT, default=options.get(CONF_AUTO_NEXT, DEFAULT_AUTO_NEXT)): bool,
                vol.Required(
                    CONF_DEBOUNCE_MS, default=int(options.get(CONF_DEBOUNCE_MS, DEFAULT_DEBOUNCE_MS))
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=2000)),
                vol.Required(CONF_LED_FX, default=options.get(CONF_LED_FX, DEFAULT_LED_FX)): bool,
            }
        )
        return self.async_show_form(step_id="general", data_schema=schema)

    async def async_step_sounds(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            player = user_input.get(CONF_SOUND_PLAYER) or None
            sounds = {k: str(user_input.get(k) or "").strip() for k in SOUND_KEYS if str(user_input.get(k) or "").strip()}
            alexa = bool(user_input.get(CONF_ALEXA_AUDIO, DEFAULT_ALEXA_AUDIO))
            return self._save(**{CONF_SOUND_PLAYER: player, CONF_SOUNDS: sounds, CONF_ALEXA_AUDIO: alexa})
        options = self.config_entry.options
        current = options.get(CONF_SOUNDS) or {}
        fields: dict[Any, Any] = {
            vol.Optional(CONF_SOUND_PLAYER, description={"suggested_value": options.get(CONF_SOUND_PLAYER)}): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="media_player")
            ),
            vol.Required(CONF_ALEXA_AUDIO, default=options.get(CONF_ALEXA_AUDIO, DEFAULT_ALEXA_AUDIO)): bool,
        }
        for key in SOUND_KEYS:
            fields[vol.Optional(key, description={"suggested_value": current.get(key, "")})] = selector.TextSelector()
        return self.async_show_form(step_id="sounds", data_schema=vol.Schema(fields))

    async def async_step_volumes(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            volumes = {k: int(v) for k, v in user_input.items() if k in SOUND_KEYS and v not in (None, "")}
            return self._save(**{CONF_SOUND_VOLUMES: volumes})
        current = self.config_entry.options.get(CONF_SOUND_VOLUMES) or {}
        number = selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=60, step=1, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="%")
        )
        fields = {vol.Optional(key, description={"suggested_value": current.get(key)}): number for key in SOUND_KEYS}
        return self.async_show_form(step_id="volumes", data_schema=vol.Schema(fields))

    # ------------------------------------------------------------ WLED Sections
    def _wled_lights(self) -> list[dict[str, Any]]:
        return [dict(light) for light in self.config_entry.options.get(CONF_WLED_LIGHTS) or []]

    async def async_step_wled(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        options = ["wled_settings", "wled_add"]
        if self._wled_lights():
            options += ["wled_edit", "wled_remove"]
        return self.async_show_menu(step_id="wled", menu_options=options)

    async def async_step_wled_settings(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self._save(**user_input)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(CONF_WLED_ENABLED, default=options.get(CONF_WLED_ENABLED, True)): bool,
                vol.Required(CONF_WLED_FLASH_MS, default=int(options.get(CONF_WLED_FLASH_MS, DEFAULT_WLED_FLASH_MS))): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=200, max=5000, step=50, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="ms")
                ),
                vol.Required(CONF_WLED_ONLY_ON, default=options.get(CONF_WLED_ONLY_ON, True)): bool,
            }
        )
        return self.async_show_form(step_id="wled_settings", data_schema=schema)

    def _light_schema(self, current: dict[str, Any] | None, with_entity: bool) -> vol.Schema:
        current = current or {}
        fields: dict[Any, Any] = {}
        if with_entity:
            fields[vol.Required("entity_id")] = selector.EntitySelector(selector.EntitySelectorConfig(domain="light"))
        fields[vol.Required("position", default=current.get("position", "top"))] = selector.SelectSelector(
            selector.SelectSelectorConfig(options=list(POSITIONS), translation_key="wled_position", mode=selector.SelectSelectorMode.DROPDOWN)
        )
        fields[vol.Optional("angle", default=float(current.get("angle", 0)))] = selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=359, step=1, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="°")
        )
        fields[vol.Optional("spread", default=float(current.get("spread", 0)))] = selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=180, step=5, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="°")
        )
        return vol.Schema(fields)

    @staticmethod
    def _light_conf(entity_id: str, user_input: dict[str, Any]) -> dict[str, Any]:
        position = user_input.get("position") or "top"
        return {
            "entity_id": entity_id,
            "position": position if position in POSITIONS else CUSTOM,
            "angle": float(user_input.get("angle") or 0) % 360,
            "spread": float(user_input.get("spread") or 0),
        }

    async def async_step_wled_add(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        lights = self._wled_lights()
        if user_input is not None:
            entity_id = user_input["entity_id"]
            if any(light["entity_id"] == entity_id for light in lights):
                errors["entity_id"] = "already_added"
            else:
                lights.append(self._light_conf(entity_id, user_input))
                return self._save(**{CONF_WLED_LIGHTS: lights})
        return self.async_show_form(step_id="wled_add", data_schema=self._light_schema(user_input, True), errors=errors)

    async def async_step_wled_edit(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        lights = self._wled_lights()
        if user_input is not None:
            self._editing = user_input["entity_id"]
            return await self.async_step_wled_edit_light()
        schema = vol.Schema(
            {
                vol.Required("entity_id"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=[light["entity_id"] for light in lights], mode=selector.SelectSelectorMode.DROPDOWN)
                )
            }
        )
        return self.async_show_form(step_id="wled_edit", data_schema=schema)

    async def async_step_wled_edit_light(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        lights = self._wled_lights()
        entity_id = getattr(self, "_editing", None)
        current = next((light for light in lights if light["entity_id"] == entity_id), None)
        if current is None:
            return self.async_abort(reason="light_not_found")
        if user_input is not None:
            new = self._light_conf(entity_id, user_input)
            lights = [new if light["entity_id"] == entity_id else light for light in lights]
            return self._save(**{CONF_WLED_LIGHTS: lights})
        return self.async_show_form(
            step_id="wled_edit_light",
            data_schema=self._light_schema(current, False),
            description_placeholders={"light": entity_id},
        )

    async def async_step_wled_remove(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        lights = self._wled_lights()
        if user_input is not None:
            remove = set(user_input.get("lights") or [])
            return self._save(**{CONF_WLED_LIGHTS: [light for light in lights if light["entity_id"] not in remove]})
        schema = vol.Schema(
            {
                vol.Optional("lights", default=[]): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=[light["entity_id"] for light in lights], multiple=True, mode=selector.SelectSelectorMode.LIST)
                )
            }
        )
        return self.async_show_form(step_id="wled_remove", data_schema=schema)
