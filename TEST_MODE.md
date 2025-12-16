# Test Mode for Met Alerts

## Overview
When there are no active weather warnings in Norway (or for testing dashboard configurations), you can enable **Test Mode** to inject fake weather alerts into your Met Alerts integration.

## Features
Test Mode injects **2 fake weather alerts** for a fictional location called "Testville":

1. **Orange Wind Warning**
   - Awareness Level: Orange (Moderate)
   - Event: Strong gale/storm
   - Valid: December 16-17, 2025
   - Description: Wind gusts up to 35 m/s in coastal areas

2. **Red Rain Warning**
   - Awareness Level: Red (Severe)
   - Event: Extreme rainfall
   - Valid: December 17-18, 2025
   - Description: 150-200mm rainfall in 24 hours, flooding expected

## How to Enable Test Mode

### For New Integrations
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for and select **Met Alerts**
4. Fill in your coordinates (lat/lon) and preferences
5. **Check the "Test Mode" checkbox** at the bottom of the form
6. Click **Submit**

### For Existing Integrations
1. Go to **Settings** → **Devices & Services**
2. Find your **Met Alerts** integration
3. Click the three-dot menu (⋮) and select **Configure**
4. **Check the "Test Mode" checkbox** at the bottom of the form
5. Click **Submit**
6. The integration will reload with the test alerts

## Verification

After enabling test mode, verify the alerts are working:

### Using Developer Tools
1. Go to **Developer Tools** → **States**
2. Find your sensor (e.g., `sensor.met_alerts`)
3. For **Array Mode**: You should see `state: 2` and an `alerts` attribute with 2 items
4. For **Legacy Mode**: You should see alerts in the first two sensors

### In Logs
1. Go to **Settings** → **System** → **Logs**
2. Look for messages like:
   ```
   Test mode: Injected 2 fake alerts for Testville (Orange Wind + Red Rain)
   Found 2 alert(s) in response
   ```

## Using Test Alerts with Dashboard Cards

Once test mode is enabled, you can test all the dashboard card configurations from [CARD_EXAMPLES.md](CARD_EXAMPLES.md):

- The fake alerts will appear in your cards
- You can iterate through both warnings
- Icons will show (orange triangle for wind, red triangle for rain)
- All alert attributes are populated (title, description, instructions, consequences, etc.)

## Disabling Test Mode

To disable test mode and return to real weather data:

1. Go to **Settings** → **Devices & Services**
2. Find your **Met Alerts** integration
3. Click the three-dot menu (⋮) and select **Configure**
4. **Uncheck the "Test Mode" checkbox**
5. Click **Submit**

## Technical Details

- Test mode does **not** require specific coordinates
- Works with any lat/lon configuration
- Test alerts are injected **after** the real API call
- If there are real alerts, test alerts are **added** to them (not replaced)
- Test alerts use proper GeoJSON structure matching Met.no API format
- All standard alert attributes are included (awareness_level, severity, certainty, etc.)

## Troubleshooting

**Q: I enabled test mode but don't see any alerts**
- Check that you're using the correct sensor entity name
- Verify the sensor mode (Array vs Legacy) matches your dashboard configuration
- Check Home Assistant logs for error messages
- Try reloading the integration

**Q: Can I change the test alert content?**
- Yes! Edit the test alert data in `custom_components/met_alerts/sensor.py`
- Look for the `if self.test_mode:` block in the `_async_update_data` method
- Modify the `test_features` list with your custom alert data

**Q: Does test mode affect real alerts?**
- No, test alerts are **added** to any existing real alerts
- Real API calls still happen normally
- If Norway has active warnings, you'll see both real + test alerts

## Use Cases

Test mode is perfect for:
- ✅ Testing dashboard card configurations
- ✅ Development and debugging
- ✅ Taking screenshots for documentation
- ✅ Training users on what alerts look like
- ✅ Testing automations and notifications
- ✅ When Norway has no active weather warnings (rare but it happens!)
