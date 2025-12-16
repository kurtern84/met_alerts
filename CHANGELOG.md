# Changelog

All notable changes to the Met Alerts integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.0] - 2025-12-16

### 🎉 Major Release - Breaking Changes

This release represents a significant upgrade to the Met Alerts integration with improved architecture, better HACS compatibility, and enhanced dashboard capabilities.

### ✨ Added

- **Array Mode** - New single-sensor mode with all alerts in attributes array
  - All alerts available via `alerts` attribute on one sensor
  - Cleaner entity list and simpler dashboard configuration
  - Fallback to legacy mode (4 sensors) for backward compatibility
  - Easy mode switching through integration options

- **Unified Alert Schema** - Cross-integration compatibility fields
  - Added standardized fields: `source`, `alert_category`, `alert_type`, `severity_level`, `severity_color`, `valid_from`, `valid_to`, `areas`, `url`
  - Enables future unified dashboard card supporting multiple alert sources
  - All original fields retained for backward compatibility
  - See documentation for field mapping details

- **Test Mode** - Fake alert injection for testing dashboards
  - Generates 2 test alerts (orange wind + red rain) for "Testville"
  - Perfect for testing when Norway has no active warnings
  - Enable via integration options UI
  - See [TEST_MODE.md](TEST_MODE.md) for usage guide

- **Dashboard Examples** - Comprehensive card templates
  - 10+ ready-to-use copy-paste examples in [CARD_EXAMPLES.md](CARD_EXAMPLES.md)
  - Compact status, timeline views, color-coded badges, and more
  - Mobile-optimized layouts
  - Conditional visibility based on alert severity

- **Official Yr.no Warning Icons** - Embedded SVG icons
  - Automatic icon display based on alert type and severity
  - 48x48px canvas with 8px padding for consistency
  - Base64-encoded, no external dependencies
  - Licensed under CC BY 4.0 from Yr/NRK
  - Icons for: gale, rain, snow, ice, wind, thunderstorm, fog, heat, cold
  - All three severity levels: yellow (moderate), orange (severe), red (extreme)

### 🔧 Changed

- **File Structure Reorganization** - Better HACS compatibility
  - Moved custom component to standard `custom_components/met_alerts/` structure
  - Improved repository layout following HACS best practices
  - Updated manifest.json with all required fields

- **Entity Cleanup** - Automatic removal of old sensors when switching modes
  - Switching from legacy to array mode removes 4 legacy sensors
  - Switching from array to legacy mode removes array sensor
  - No more "unavailable" or "not provided" ghost entities
  - Clean entity registry after mode changes

- **Manifest Updates** - Enhanced metadata
  - Added `integration_type: "service"`
  - Added `issue_tracker` URL
  - Removed unnecessary `aiohttp` from requirements (built-in to HA)
  - Updated `iot_class` to standard format

- **README Enhancements** - Comprehensive documentation
  - Installation instructions for both HACS and manual
  - Mode comparison and selection guide
  - Dashboard card examples and usage
  - Troubleshooting section
  - API information and attribution

### 🐛 Fixed

- SSL certificate validation issues (via embedded icons, no external requests)
- Icon display reliability (embedded base64 vs external URLs)
- Entity state consistency across mode switches
- Coordinator initialization with test mode parameter

### 📚 Documentation

- [README.md](README.md) - Complete installation and configuration guide
- [CARD_EXAMPLES.md](CARD_EXAMPLES.md) - Dashboard card templates and examples
- [TEST_MODE.md](TEST_MODE.md) - Test mode usage and troubleshooting
- [CHANGELOG.md](CHANGELOG.md) - Version history (this file)

### 🔄 Migration Guide

#### Upgrading from v3.x

**If using Legacy Mode (4 sensors):**
- No action required
- All existing dashboards and automations continue to work
- Optionally switch to array mode for cleaner entity list

**If using Array Mode:**
- Entity IDs remain the same
- New unified schema fields added alongside existing fields
- Existing templates using original field names continue to work
- Optionally update templates to use unified schema for future compatibility

**Mode Switching:**
1. Go to **Settings** → **Devices & Services**
2. Find **Met Alerts** → Click **Configure**
3. Choose your preferred sensor mode
4. Old sensors are automatically removed
5. Dashboard cards will need updating to reference new entity IDs

### ⚠️ Breaking Changes

- **Array Mode sensor unique_id format changed** - Old array mode sensors (if any) will be recreated with new IDs
- **Icon URLs removed** - Icons now embedded as base64, no more external icon URLs in attributes
- **Minimum HA version** - Now requires Home Assistant 2023.8.0+

### 🙏 Credits

- **Original Author:** @kurtern84
- **Major Refactor & v4.0:** @jm-cook
- **Warning Icons:** Yr warning icons © 2015 by Yr/NRK, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Data Source:** MET Norway (api.met.no)

### 📋 Technical Details

- **Platforms:** `sensor`
- **Config Flow:** Yes (UI configuration)
- **IoT Class:** Cloud Polling
- **Update Interval:** 30 minutes
- **Languages:** English, Norwegian

---

## [3.0.0] - Previous Release

- Added UI configuration flow
- Introduced array mode option
- Basic icon support

## [2.x.x] - Legacy Versions

- YAML configuration only
- 4-sensor legacy mode
- Basic alert fetching

---

[4.0.0]: https://github.com/kurtern84/met_alerts/releases/tag/v4.0.0
[3.0.0]: https://github.com/kurtern84/met_alerts/releases/tag/v3.0.0
