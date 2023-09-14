"""Support for Zibase entities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.light import LightEntity, LightEntityDescription
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.entity import DeviceInfo

from .zapi import core

# from .const import DOMAIN


@dataclass
class ZibaseLightEntityDescription(LightEntityDescription):
    """Class describing Zibase select entities."""

    toggle_command: str | None = None


class ZibaseLight(LightEntity):
    """Representation of a Zibase Light."""

    def __init__(self, zibase, description) -> None:
        """Initialize an ZibaseLight."""
        self.zibase = zibase
        self._light_id = description.key
        self._name = description.name
        self._state = STATE_OFF

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state == STATE_ON

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self.zibase.send_command(
            self._light_id, core.ZbAction.ON, core.ZbProtocol.CHACON
        )
        self._state = STATE_ON

    @property
    def device_info(self) -> DeviceInfo:
        """Return a port description for device registry."""
        info = DeviceInfo(
            manufacturer="Zibase",
            name="Lights",
            # "connections": {(DOMAIN, self._light_id)},
        )

        return info

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self.zibase.send_command(
            self._light_id, core.ZbAction.OFF, core.ZbProtocol.CHACON
        )
        self._state = STATE_OFF

    # def update(self) -> None:
    #     """Fetch new state data for this light.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     pass
    # self._light.update()
    # self._state = self._light.is_on()
