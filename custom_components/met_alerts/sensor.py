"""Met Alerts sensor platform."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
import re

import aiohttp
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_LANG,
    CONF_LANG,
    CONF_SENSOR_MODE,
    SENSOR_MODE_LEGACY,
    SENSOR_MODE_ARRAY,
    ICON_DATA_URLS,
    ICON_ATTRIBUTION,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)

# Support for legacy YAML configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_LATITUDE): cv.latitude,
    vol.Required(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_LANG, default=DEFAULT_LANG): cv.string,
})



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Met Alerts sensor from a config entry."""
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    latitude = entry.data.get(CONF_LATITUDE)
    longitude = entry.data.get(CONF_LONGITUDE)
    lang = entry.data.get(CONF_LANG, DEFAULT_LANG)
    # Read sensor mode from options, fallback to legacy
    sensor_mode = entry.options.get(CONF_SENSOR_MODE, SENSOR_MODE_LEGACY) if hasattr(entry, 'options') else SENSOR_MODE_LEGACY

    coordinator = MetAlertsCoordinator(hass, latitude, longitude, lang)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    if sensor_mode == SENSOR_MODE_ARRAY:
        entities.append(MetAlertsArraySensor(coordinator, name, entry.entry_id))
    else:
        # Default: legacy mode (4 sensors)
        entities = [
            MetAlertsSensor(coordinator, f"{name}", 0, entry.entry_id),
            MetAlertsSensor(coordinator, f"{name}_2", 1, entry.entry_id),
            MetAlertsSensor(coordinator, f"{name}_3", 2, entry.entry_id),
            MetAlertsSensor(coordinator, f"{name}_4", 3, entry.entry_id),
        ]
    async_add_entities(entities)

# New: Array mode sensor (single entity with all alerts as attribute)
class MetAlertsArraySensor(CoordinatorEntity, SensorEntity):
    """Single sensor with all alerts as attribute (array mode)."""

    def __init__(self, coordinator: MetAlertsCoordinator, name: str, entry_id: str | None):
        super().__init__(coordinator)
        self._attr_name = name
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_array" if entry_id else None
        self._attr_has_entity_name = False

    @property
    def native_value(self):
        """Return the state: number of active alerts, or 'No Alert'."""
        if not self.coordinator.data:
            return "No Alert"
        features = self.coordinator.data.get("features", [])
        return len(features) if features else "No Alert"

    @property
    def extra_state_attributes(self):
        """Return all alerts as an array attribute."""
        if not self.coordinator.data:
            return {"alerts": []}
        features = self.coordinator.data.get("features", [])
        alerts = []
        for feature in features:
            props = feature.get("properties", {})
            title, starttime, endtime = extract_times_from_title(props.get("title", ""))
            awareness_level = props.get("awareness_level", "")
            try:
                awareness_level_numeric, awareness_level_color, _ = awareness_level.split("; ")
            except ValueError:
                awareness_level_numeric = ""
                awareness_level_color = ""
            alerts.append({
                "title": title,
                "starttime": starttime,
                "endtime": endtime,
                "description": props.get("description", ""),
                "awareness_level": awareness_level,
                "awareness_level_numeric": awareness_level_numeric,
                "awareness_level_color": awareness_level_color,
                "certainty": props.get("certainty", ""),
                "severity": props.get("severity", ""),
                "instruction": props.get("instruction", ""),
                "contact": props.get("contact", ""),
                "resources": props.get("resources", []),
                "area": props.get("area", ""),
                "event_awareness_name": props.get("eventAwarenessName", ""),
                "consequences": props.get("consequences", ""),
            })
        return {"alerts": alerts}

    @property
    def entity_picture(self):
        """Return the icon for the most severe alert (if any)."""
        if not self.coordinator.data:
            return None
        features = self.coordinator.data.get("features", [])
        if not features:
            return None
        # Use the first alert (highest awareness_level after sorting)
        sorted_features = sorted(
            features,
            key=lambda x: x["properties"]["awareness_level"],
            reverse=True,
        )
        props = sorted_features[0].get("properties", {})
        event = props.get("event", "").lower().replace(" ", "-")
        awareness_level = props.get("awareness_level", "")
        try:
            _, color, _ = awareness_level.split("; ")
        except ValueError:
            color = ""
        key = f"{event}-{color.lower()}" if color else event
        return ICON_DATA_URLS.get(key)

    @property
    def attribution(self):
        """Return attribution for warning icons."""
        return ICON_ATTRIBUTION


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Met Alerts sensor from YAML configuration (legacy)."""
    _LOGGER.warning(
        "Configuration of Met Alerts via YAML is deprecated. "
        "Please remove it from your configuration and use the UI instead."
    )
    name = config[CONF_NAME]
    latitude = config[CONF_LATITUDE]
    longitude = config[CONF_LONGITUDE]
    lang = config.get(CONF_LANG, DEFAULT_LANG)
    
    coordinator = MetAlertsCoordinator(hass, latitude, longitude, lang)
    await coordinator.async_refresh()
    
    entities = [
        MetAlertsSensor(coordinator, f"{name}", 0, None),
        MetAlertsSensor(coordinator, f"{name}_2", 1, None),
        MetAlertsSensor(coordinator, f"{name}_3", 2, None),
        MetAlertsSensor(coordinator, f"{name}_4", 3, None),
    ]
    async_add_entities(entities)


class MetAlertsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Met Alerts data."""

    def __init__(self, hass, latitude, longitude, lang):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.latitude = latitude
        self.longitude = longitude
        self.lang = lang

    async def _async_update_data(self):
        """Fetch data from API."""
        url = f"https://aa015h6buqvih86i1.api.met.no/weatherapi/metalerts/2.0/current.json?lat={self.latitude}&lon={self.longitude}&lang={self.lang}"
        #url = f"https://api.met.no/weatherapi/metalerts/2.0/example.json?lang={self.lang}"
        try:
            async with aiohttp.ClientSession() as session:
                async with asyncio.timeout(10):
                    async with session.get(url) as response:
                        if response.status != 200:
                            _LOGGER.error("Error fetching data: %s", response.status)
                            raise UpdateFailed(f"Error fetching data: {response.status}")

                        content_type = response.headers.get("Content-Type", "")
                        if "application/json" not in content_type:
                            _LOGGER.error("Unexpected Content-Type: %s", content_type)
                            raise UpdateFailed(f"Unexpected Content-Type: {content_type}")

                        response_text = await response.text()
                        if not response_text:
                            _LOGGER.error("Received empty response")
                            raise UpdateFailed("Received empty response")

                        try:
                            json_data = await response.json()
                            _LOGGER.info("Successfully fetched Met alerts data")
                            _LOGGER.debug("Full API response: %s", json_data)
                            
                            # Log the number of features found
                            features = json_data.get("features", [])
                            _LOGGER.info("Found %d alert(s) in response", len(features))
                            
                            # Log details of each alert
                            for idx, feature in enumerate(features):
                                props = feature.get("properties", {})
                                _LOGGER.info(
                                    "Alert %d: event='%s', awareness_level='%s', title='%s'",
                                    idx + 1,
                                    props.get("event"),
                                    props.get("awareness_level"),
                                    props.get("title"),
                                )
                            
                            return json_data
                        except aiohttp.ClientResponseError as err:
                            _LOGGER.error("JSON decode error: Response content was empty or invalid")
                            _LOGGER.debug("Response content: %s", response_text)
                            raise UpdateFailed(f"JSON decode error: {err}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching data: {err}")

class MetAlertsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Met Alerts sensor."""

    def __init__(self, coordinator: MetAlertsCoordinator, name: str, index: int, entry_id: str | None):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = name
        self.index = index
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{index}" if entry_id else None
        self._attr_has_entity_name = False

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "No Alert"
            
        features = self.coordinator.data.get("features", [])
        
        _LOGGER.debug(
            "Sensor %s (index %d): Processing %d features",
            self._attr_name,
            self.index,
            len(features),
        )

        # Sort features by awareness_level
        sorted_features = sorted(
            features,
            key=lambda x: x["properties"]["awareness_level"],
            reverse=True,
        )

        if len(sorted_features) > self.index:
            alert = sorted_features[self.index]
            properties = alert["properties"]
            event = properties.get("event", "No Alert")
            _LOGGER.debug("Sensor %s: Alert found - %s", self._attr_name, event)
            return event
        
        _LOGGER.debug(
            "Sensor %s (index %d): No alert available",
            self._attr_name,
            self.index,
        )
        return "No Alert"

    @property
    def entity_picture(self):
        """Return the icon image for the alert (if any)."""
        if not self.coordinator.data:
            return None
        features = self.coordinator.data.get("features", [])
        sorted_features = sorted(
            features,
            key=lambda x: x["properties"]["awareness_level"],
            reverse=True,
        )
        if len(sorted_features) > self.index:
            properties = sorted_features[self.index]["properties"]
            event = properties.get("event", "").lower().replace(" ", "-")
            awareness_level = properties.get("awareness_level", "")
            try:
                _, color, _ = awareness_level.split("; ")
            except ValueError:
                color = ""
            key = f"{event}-{color.lower()}" if color else event
            return ICON_DATA_URLS.get(key)
        return None

    @property
    def attribution(self):
        """Return attribution for warning icons."""
        return ICON_ATTRIBUTION

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
            
        features = self.coordinator.data.get("features", [])
        
        # Sort features by awareness_level
        sorted_features = sorted(
            features,
            key=lambda x: x["properties"]["awareness_level"],
            reverse=True,
        )

        if len(sorted_features) > self.index:
            alert = sorted_features[self.index]
            properties = alert["properties"]

            # Extract starttime and endtime from the title
            title, starttime, endtime = extract_times_from_title(
                properties.get("title", "")
            )

            # Extract the URL of the PNG image
            resources = properties.get("resources", [])
            map_url = None
            for resource in resources:
                if resource.get("mimeType") == "image/png":
                    map_url = resource.get("uri")
                    break

            # Split awareness_level into numeric, color, and name
            awareness_level = properties.get("awareness_level", "")
            try:
                awareness_level_numeric, awareness_level_color, _ = awareness_level.split("; ")
            except ValueError:
                awareness_level_numeric = ""
                awareness_level_color = ""

            return {
                "title": title,
                "starttime": starttime,
                "endtime": endtime,
                "description": properties.get("description", ""),
                "awareness_level": properties.get("awareness_level", ""),
                "awareness_level_numeric": awareness_level_numeric,
                "awareness_level_color": awareness_level_color,
                "certainty": properties.get("certainty", ""),
                "severity": properties.get("severity", ""),
                "instruction": properties.get("instruction", ""),
                "contact": properties.get("contact", ""),
                "resources": properties.get("resources", []),
                "area": properties.get("area", ""),
                "event_awareness_name": properties.get("eventAwarenessName", ""),
                "consequences": properties.get("consequences", ""),
                "map_url": map_url,
            }
        
        return {}

def extract_times_from_title(title: str) -> tuple[str, str | None, str | None]:
    """Extract timestamps from alert title."""
    timestamps = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}", title)

    if len(timestamps) >= 2:
        starttime = timestamps[0]
        endtime = timestamps[1]
        # Remove the timestamps from the title
        title = title.replace(starttime, "").replace(endtime, "").strip(", ").strip()
        return title, starttime, endtime
    else:
        return title, None, None
