"""The Zibase welcome integration."""
from __future__ import annotations

import logging

from homeassistant.const import CONF_HOST, EntityCategory, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import SWITCH_TYPES
from .entity import ZibaseLight, ZibaseLightEntityDescription
from .zapi import core

_LOGGER = logging.getLogger(__name__)

# List the platforms that you want to support.
PLATFORMS: list[Platform] = [Platform.LIGHT]


LIGHTS: dict[str, tuple[ZibaseLightEntityDescription, ...]] = {
    # Curtain Switch
    # https://developer.tuya.com/en/docs/iot/category-clkg?id=Kaiuz0gitil39
    "lampe_ilot": (
        ZibaseLightEntityDescription(
            key="A1",
            name="Lampe Ilot",
            entity_category=EntityCategory.CONFIG,
        ),
    ),
}


class ZibaseHAManager(core.ZiBase):
    """Add HA entity features."""

    def __init__(self, config) -> None:
        """Initialize Zibase IP address."""
        host = config[CONF_HOST]
        super().__init__(host)

    def lights(self):
        """Define all lights monitored by zibase."""
        # lights = [ZibaseLight(self, "A1", "Lumière ilot")]
        switches = []
        for switch in SWITCH_TYPES:  # pylint: disable=consider-using-dict-items
            switches.append(
                # ZibaseLight(self, "A1", "Lumière ilot")
                ZibaseLight(self, SWITCH_TYPES[switch])
            )
        return switches


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    # Setup connection with devices/cloud
    zibase = ZibaseHAManager(config)

    # Verify that passed in configuration works
    # if not hub.is_valid_login():
    #     _LOGGER.error("Could not connect to AwesomeLight hub")
    #     return

    # Add devices
    # add_entities(AwesomeLight(light) for light in hub.lights())
    add_entities(zibase.lights())


def device_info(self) -> DeviceInfo:
    """Return a port description for device registry."""
    return DeviceInfo(
        manufacturer="Zibase",
        name="ZIBASE_NAME",
    )


# async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Set up Zibase welcome from a config entry."""

#     hass.data.setdefault(DOMAIN, {})
#     # 1. Create API instance
#     # 2. Validate the API connection (and authentication)
#     # 3. S:tore an API object for your platforms to access
#     # hass.data[DOMAIN][entry.entry_id] = ZiBase.ZiBase("192.168.100.177")

#     await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

#     return True


# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Unload a config entry."""
#     if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
#         hass.data[DOMAIN].pop(entry.entry_id)

#     return unload_ok


#######################################################
# async def send_command(handler, command) -> None:
#     """Send command to OpenEVSE device via RAPI."""
#     cmd, response = await handler.send_command(command)
#     _LOGGER.debug("send_command: %s, %s", cmd, response)
#     if cmd == command:
#         if response == "$NK^21":
#             raise InvalidValue
#         return None

#     raise CommandFailed


# class OpenEVSEManager:
#     """OpenEVSE connection manager."""

#     def __init__(  # pylint: disable-next=unused-argument
#         self, hass: HomeAssistant, config_entry: ConfigEntry
#     ) -> None:
#         """Initialize."""
#         self._host = config_entry.data.get(CONF_HOST)
#         self._username = config_entry.data.get(CONF_USERNAME)
#         self._password = config_entry.data.get(CONF_PASSWORD)
#         self.charger = OpenEVSE(self._host, user=self._username, pwd=self._password)
