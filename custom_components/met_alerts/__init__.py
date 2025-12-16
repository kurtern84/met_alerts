"""The Met Alerts integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, PLATFORMS, CONF_SENSOR_MODE, SENSOR_MODE_ARRAY, SENSOR_MODE_LEGACY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Met Alerts from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update and clean up old entities when switching modes."""
    entity_registry = er.async_get(hass)
    
    # Get current sensor mode
    sensor_mode = entry.options.get(CONF_SENSOR_MODE, SENSOR_MODE_LEGACY)
    
    # Get all entities for this config entry
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    
    # Remove incompatible entities based on new mode
    for entity in entities:
        if sensor_mode == SENSOR_MODE_ARRAY:
            # In array mode, remove legacy sensors (_2, _3, _4, and base without _array suffix)
            if entity.unique_id and not entity.unique_id.endswith("_array"):
                _LOGGER.info(f"Removing legacy sensor entity {entity.entity_id} (switching to array mode)")
                entity_registry.async_remove(entity.entity_id)
        else:
            # In legacy mode, remove array sensor
            if entity.unique_id and entity.unique_id.endswith("_array"):
                _LOGGER.info(f"Removing array sensor entity {entity.entity_id} (switching to legacy mode)")
                entity_registry.async_remove(entity.entity_id)
    
    # Reload the integration to create new entities
    await hass.config_entries.async_reload(entry.entry_id)

