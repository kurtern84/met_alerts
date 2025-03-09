import logging
from datetime import timedelta
import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

DOMAIN = "met_alerts"
DEFAULT_NAME = "Met Alerts"
DEFAULT_LANG = "no"  # Default value for lang
SCAN_INTERVAL = timedelta(hours=1)

CONF_LANG = "lang"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_LATITUDE): cv.latitude,
    vol.Required(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_LANG, default=DEFAULT_LANG): cv.string,  # Add lang config option
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config[CONF_NAME]
    latitude = config[CONF_LATITUDE]
    longitude = config[CONF_LONGITUDE]
    lang = config.get(CONF_LANG, DEFAULT_LANG)  # Get lang config option
    coordinator = MetAlertsCoordinator(hass, latitude, longitude, lang)
    await coordinator.async_refresh()
    entities = [
        MetAlertsSensor(f"{name}", coordinator, 0),
        MetAlertsSensor(f"{name}_2", coordinator, 1),
        MetAlertsSensor(f"{name}_3", coordinator, 2),
        MetAlertsSensor(f"{name}_4", coordinator, 3),
    ]
    async_add_entities(entities, True)    

class MetAlertsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, latitude, longitude, lang):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.latitude = latitude
        self.longitude = longitude
        self.lang = lang  # Store lang parameter

    async def _async_update_data(self):
        """Fetch data from API."""
        url = f"https://api.met.no/weatherapi/metalerts/2.0/current.json?lat={self.latitude}&lon={self.longitude}&lang={self.lang}"
        headers = {"User-Agent": "HomeAssistantMetAlerts/1.0 (kurtern84@gmail.com)"}  # Add User-Agent header
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.get(url, headers=headers) as response:
                        if response.status == 400:
                            _LOGGER.error("Error fetching data: 400 Bad Request. Check parameters.")
                            raise UpdateFailed("Error fetching data: 400 Bad Request")
                        if response.status == 403:
                            _LOGGER.error("Error fetching data: 403 Forbidden. Check API access.")
                            raise UpdateFailed("Error fetching data: 403 Forbidden")
                        if response.status != 200:
                            _LOGGER.error(f"Error fetching data: {response.status}")
                            raise UpdateFailed(f"Error fetching data: {response.status}")

                        content_type = response.headers.get('Content-Type', '')
                        if 'application/json' not in content_type:
                            _LOGGER.error(f"Unexpected Content-Type: {content_type}")
                            raise UpdateFailed(f"Unexpected Content-Type: {content_type}")

                        response_text = await response.text()
                        if not response_text:
                            _LOGGER.error("Received empty response")
                            raise UpdateFailed("Received empty response")

                        try:
                            json_data = await response.json()
                            _LOGGER.debug(f"Response JSON: {json_data}")

                            # Handle case where there are no alerts
                            if not json_data.get("features"):
                                _LOGGER.info("No active alerts available.")
                                return {"features": []}
                            
                            return json_data
                        except aiohttp.ClientResponseError as err:
                            _LOGGER.error("JSON decode error: Response content was empty or invalid")
                            _LOGGER.debug(f"Response content: {response_text}")
                            raise UpdateFailed(f"JSON decode error: {err}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching data: {err}")

class MetAlertsSensor(SensorEntity):
    def __init__(self, name, coordinator, index):
        self._name = name
        self.coordinator = coordinator
        self._state = None
        self._attributes = {}
        self.index = index

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
    
    async def async_update(self):
        await self.coordinator.async_request_refresh()
        features = self.coordinator.data.get("features", []) if self.coordinator.data else []

        if not features:
            self._state = "No Alert"
            self._attributes = {"message": "No active alerts available."}
            return

        # Sort features by awareness_level
        features.sort(key=lambda x: x["properties"].get("awareness_level", "0"), reverse=True)

        if len(features) > self.index:
            alert = features[self.index]
            properties = alert["properties"]

            # Extract starttime and endtime from the title
            title, starttime, endtime = extract_times_from_title(properties.get("title", ""))

            # Extract the URL of the PNG image
            resources = properties.get("resources", [])
            map_url = next((r.get("uri") for r in resources if r.get("mimeType") == "image/png"), None)

            # Update attributes
            self._state = properties.get("event", "No Alert")
            self._attributes = {
                "title": title,
                "starttime": starttime,
                "endtime": endtime,
                "description": properties.get("description", ""),
                "certainty": properties.get("certainty", ""),
                "severity": properties.get("severity", ""),
                "instruction": properties.get("instruction", ""),
                "contact": properties.get("contact", ""),
                "map_url": map_url,
            }
        else:
            self._state = "No Alert"
            self._attributes = {"message": "No active alerts available."}

def extract_times_from_title(title):
    import re
    timestamps = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}", title)
    if len(timestamps) >= 2:
        return title.replace(timestamps[0], "").replace(timestamps[1], "").strip(", "), timestamps[0], timestamps[1]
    return title, None, None
