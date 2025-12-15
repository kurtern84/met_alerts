"""Config flow for Met Alerts integration."""
import asyncio
import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_LANG,
    CONF_LANG,
    CONF_SENSOR_MODE,
    SENSOR_MODE_LEGACY,
    SENSOR_MODE_ARRAY,
)

_LOGGER = logging.getLogger(__name__)


async def validate_coordinates(hass: HomeAssistant, latitude: float, longitude: float, lang: str):
    """Validate that the coordinates work with the API."""
    url = f"https://aa015h6buqvih86i1.api.met.no/weatherapi/metalerts/2.0/current.json?lat={latitude}&lon={longitude}&lang={lang}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(10):
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError(f"API returned status {response.status}")
                    
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' not in content_type:
                        raise ValueError(f"Unexpected content type: {content_type}")
                    
                    # Try to parse JSON
                    await response.json()
                    return True
    except aiohttp.ClientError as err:
        raise ValueError(f"Cannot connect to API: {err}")
    except Exception as err:
        raise ValueError(f"Unexpected error: {err}")


class MetAlertsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Met Alerts."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the coordinates work
                await validate_coordinates(
                    self.hass,
                    user_input[CONF_LATITUDE],
                    user_input[CONF_LONGITUDE],
                    user_input.get(CONF_LANG, DEFAULT_LANG),
                )

                # Create a unique ID based on coordinates
                await self.async_set_unique_id(
                    f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )
            except ValueError as err:
                _LOGGER.error("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show the form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(
                    CONF_LATITUDE,
                    default=self.hass.config.latitude,
                ): cv.latitude,
                vol.Required(
                    CONF_LONGITUDE,
                    default=self.hass.config.longitude,
                ): cv.longitude,
                vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(["no", "en"]),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return MetAlertsOptionsFlow()


class MetAlertsOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Met Alerts."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the new coordinates if changed
                await validate_coordinates(
                    self.hass,
                    user_input[CONF_LATITUDE],
                    user_input[CONF_LONGITUDE],
                    user_input.get(CONF_LANG, DEFAULT_LANG),
                )

                # Update config entry data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_LATITUDE: user_input[CONF_LATITUDE],
                        CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                        CONF_LANG: user_input.get(CONF_LANG, DEFAULT_LANG),
                    },
                )
                # Return options data (sensor_mode only)
                options_data = {}
                if CONF_SENSOR_MODE in user_input:
                    options_data[CONF_SENSOR_MODE] = user_input[CONF_SENSOR_MODE]
                return self.async_create_entry(title="", data=options_data)
            except ValueError as err:
                _LOGGER.error("Validation failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Get current values from config entry and options
        current_name = self.config_entry.data.get(CONF_NAME, DEFAULT_NAME)
        current_lat = self.config_entry.data.get(CONF_LATITUDE, self.hass.config.latitude)
        current_lon = self.config_entry.data.get(CONF_LONGITUDE, self.hass.config.longitude)
        current_lang = self.config_entry.data.get(CONF_LANG, DEFAULT_LANG)
        current_mode = self.config_entry.options.get(CONF_SENSOR_MODE, SENSOR_MODE_LEGACY)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=current_name): cv.string,
                vol.Required(CONF_LATITUDE, default=current_lat): cv.latitude,
                vol.Required(CONF_LONGITUDE, default=current_lon): cv.longitude,
                vol.Optional(CONF_LANG, default=current_lang): vol.In(["no", "en"]),
                vol.Optional(CONF_SENSOR_MODE, default=current_mode): vol.In([SENSOR_MODE_LEGACY, SENSOR_MODE_ARRAY]),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
