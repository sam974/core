"""Constants for the Zibase welcome integration."""
from typing import Final

from homeassistant.components.switch import SwitchDeviceClass

from .entity import ZibaseLightEntityDescription

DOMAIN = "zibase"

ACTIONNEURS = {
    "LAMPE_SALON": "A1",
    "PISCINE": "G3",
    "PRISE_CHAUFFE_EAU": "A4",
    "POMPE_CESI": "A15",
    "SIRENE_VISONIC": "A3",
    "VMC": "G2",
}

SWITCH_TYPES: Final[dict[str, ZibaseLightEntityDescription]] = {
    "lampe_salon": ZibaseLightEntityDescription(
        name="Lampe Ilot",
        key="A1",
        toggle_command="toggle_ilot",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    # "manual_override": ZibaseLightEntityDescription(
    #     name="Manual Override",
    #     key="manual_override",
    #     toggle_command="toggle_override",
    #     device_class=SwitchDeviceClass.SWITCH,
    # ),
}
