from __future__ import annotations

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

PLATFORMS: list[str] = ["light"]

class Hub:
    def __init__(self, hass: HomeAssistant, address: str, type: str) -> None:
        """Init dummy hub."""
        self.address = address
        self.type = type


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Govee BLE device from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    address = entry.unique_id
    assert address is not None
    ble_device = bluetooth.async_ble_device_from_address(hass, address.upper(), True)
    if not ble_device:
        if bluetooth.async_scanner_count(hass, connectable=False):
            raise ConfigEntryNotReady(
                "No bluetooth scanner detected. \
                Enable the bluetooth integration or ensure an esphome device \
                is running as a bluetooth proxy"
            )
        else:
            raise ConfigEntryNotReady(
                f"Could not find LED BLE device with address {address}"
            )

    hass.data[DOMAIN][entry.entry_id] = Hub(hass, address, entry.data.get("type"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, PLATFORMS)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok