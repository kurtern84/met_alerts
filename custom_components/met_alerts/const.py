"""Constants for the Met Alerts integration."""
#
# Icon data is embedded via icon_data.py (auto-generated from NRK/yr-warning-icons, CC BY 4.0)
# See LICENSE_yr_icons.txt for full license text and attribution requirements.

from .icon_data import ICON_DATA_URLS

CONF_SENSOR_MODE = "sensor_mode"
SENSOR_MODE_LEGACY = "legacy"
SENSOR_MODE_ARRAY = "array"

ICON_ATTRIBUTION = (
	"Warning icons by NRK/yr.no, CC BY 4.0, "
	"https://github.com/nrkno/yr-warning-icons"
)

DOMAIN = "met_alerts"
DEFAULT_NAME = "Met Alerts"
DEFAULT_LANG = "no"
CONF_LANG = "lang"
PLATFORMS = ["sensor"]
