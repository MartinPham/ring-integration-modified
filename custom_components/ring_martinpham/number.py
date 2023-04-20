"""Component providing HA sensor support for Ring numbers."""

from __future__ import annotations
from datetime import timedelta
from dataclasses import dataclass

import requests
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
    NumberEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

from . import DOMAIN
from .entity import RingEntityMixin


SKIP_UPDATES_DELAY = timedelta(seconds=5)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    devices = hass.data[DOMAIN][config_entry.entry_id]["devices"]

    """Some accounts returned data without intercom devices"""
    devices.setdefault("other", [])

    entities = [
        description.cls(config_entry.entry_id, device, description)
        for device_type in ("other",)
        for description in BUTTON_TYPES
        if device_type in description.category
        for device in devices[device_type]
    ]

    async_add_entities(entities)


@dataclass
class RingRequiredKeysMixin:
    category: list[str]
    cls: type[RingNumber]


@dataclass
class RingNumberEntityDescription(NumberEntityDescription, RingRequiredKeysMixin):
    kind: str | None = None


class RingDoorVolume(RingEntityMixin, NumberEntity):
    entity_description: RingNumberEntityDescription

    def __init__(
        self,
        config_entry_id,
        device,
        description: RingNumberEntityDescription,
    ) -> None:
        super().__init__(config_entry_id, device)
        self.entity_description = description
        self._extra = None
        self._attr_name = f"{device.name} {description.name}"
        self._attr_unique_id = f"{device.id}-{description.key}"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 11
        self._no_updates_until = dt_util.utcnow()

        sensor_type = self.entity_description.key

        if sensor_type == "mic_volume":
            self._attr_native_value = self._device.mic_volume
        if sensor_type == "voice_volume":
            self._attr_native_value = self._device.voice_volume

    @callback
    def _update_callback(self):
        """Call update method."""
        if self._no_updates_until > dt_util.utcnow():
            return

        sensor_type = self.entity_description.key
        if sensor_type == "mic_volume":
            self._attr_native_value = self._device.mic_volume
        if sensor_type == "voice_volume":
            self._attr_native_value = self._device.voice_volume
        self.async_write_ha_state()

    @property
    def icon(self):
        """Return the icon."""
        sensor_type = self.entity_description.key

        if sensor_type == "mic_volume":
            return "mdi:account-voice"
        if sensor_type == "voice_volume":
            return "mdi:bell-ring-outline"

    def set_native_value(self, value: float) -> None:
        """Set new value."""
        sensor_type = self.entity_description.key
        try:
            self._device.set_volume(sensor_type, value)
        except requests.Timeout:
            _LOGGER.error("Time out setting %s volume to %s", self.entity_id, value)
            return

        if sensor_type == "mic_volume":
            self._attr_native_value = self._device.mic_volume
        if sensor_type == "voice_volume":
            self._attr_native_value = self._device.voice_volume
        self.async_write_ha_state()

        self._no_updates_until = dt_util.utcnow() + SKIP_UPDATES_DELAY
        self.schedule_update_ha_state()


BUTTON_TYPES: tuple[RingNumberEntityDescription, ...] = (
    RingNumberEntityDescription(
        key="mic_volume",
        name="Mic volume",
        category=["other"],
        icon="mdi:door-closed-lock",
        cls=RingDoorVolume,
    ),
    RingNumberEntityDescription(
        key="voice_volume",
        name="Voice volume",
        category=["other"],
        icon="mdi:door-closed-lock",
        cls=RingDoorVolume,
    ),
)
