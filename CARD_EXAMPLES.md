# Dashboard Card Examples for Met Alerts

This document provides ready-to-use dashboard card configurations for displaying MET Norway weather alerts in your Home Assistant UI.

## Table of Contents
- [How It Works](#how-it-works)
- [Visual Alert Icons](#visual-alert-icons)
- [Array Mode Setup](#array-mode-setup)
- [Basic Cards](#basic-cards)
- [Advanced Cards](#advanced-cards)
- [Automations](#automations)

---

## How It Works

Met Alerts integration offers two sensor modes:

### Array Mode (Recommended)
- **Single sensor** with all alerts as an attribute array
- Entity ID: `sensor.met_alerts` (or your custom name)
- State: Number of active alerts or "No Alert"
- All alert details available in the `alerts` attribute

### Legacy Mode
- **Four separate sensors** (sensor, sensor_2, sensor_3, sensor_4)
- Each shows one alert
- For backward compatibility

**This guide focuses on Array Mode** - it's simpler and more flexible!

---

## Visual Alert Icons

The sensors automatically display warning icons from Yr.no (NRK) based on the most severe alert:

The icons are displayed automatically in entity cards via the `entity_picture` property. No configuration needed!

**Available icon types:**
- Avalanches (yellow, orange, red)
- Flood (yellow, orange, red)
- Forest Fire (yellow, orange, red)
- Ice (yellow, orange, red)
- Rain (yellow, orange, red)
- Snow (yellow, orange, red)
- Wind (yellow, orange, red)

---

## Array Mode Setup

To use array mode, configure the integration with:
- **Sensor Mode**: Array (recommended)

You'll get a single sensor entity (e.g., `sensor.met_alerts`) that contains:
- **State**: Number of active alerts (or "No Alert")
- **Attribute `alerts`**: Array of all alert details

---

## Basic Cards

### 1. Minimal Status Card

Shows current alert status with automatic icon:

```yaml
type: entities
title: Weather Alerts
entities:
  - entity: sensor.met_alerts
    name: Active Alerts
    secondary_info: last-changed
```

### 2. Compact Alert List

Quick overview of all alerts:

```yaml
type: markdown
title: Active Weather Alerts
content: |
  {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
  {% if alerts and alerts|length > 0 %}
    {% for alert in alerts %}
  **{{ alert.title }}**
  {{ alert.awareness_level_color|upper }} - {{ alert.description[:100] }}...
  Valid: {{ alert.starttime }} to {{ alert.endtime }}
  ---
    {% endfor %}
  {% else %}
  ✅ No active weather alerts
  {% endif %}
```

### 3. Alert Count Badge

Simple numerical display:

```yaml
type: entity
entity: sensor.met_alerts
name: Weather Alerts
icon: mdi:alert
```

### 4. Glance Card (Status Overview)

```yaml
type: glance
title: Weather Alert Status
entities:
  - entity: sensor.met_alerts
    name: Active Alerts
columns: 1
```

---

## Advanced Cards

### 5. Detailed Alert Display

Shows all alert information with full formatting:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Weather Alert Summary
    entities:
      - entity: sensor.met_alerts
        name: Alert Status
        secondary_info: last-changed
  - type: conditional
    conditions:
      - entity: sensor.met_alerts
        state_not: "No Alert"
    card:
      type: markdown
      title: ⚠️ Active Weather Warnings
      content: |
        {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
        {% for alert in alerts %}
        ### {{ alert.title }}
        
        **Severity**: {{ alert.awareness_level_color|upper }}
        
        **Type**: {{ alert.event_awareness_name }}
        
        **Valid Period**: {{ alert.starttime }} to {{ alert.endtime }}
        
        #### Description
        {{ alert.description }}
        
        {% if alert.instruction %}
        #### Instructions
        {{ alert.instruction }}
        {% endif %}
        
        {% if alert.consequences %}
        #### Consequences
        {{ alert.consequences }}
        {% endif %}
        
        {% if alert.area %}
        **Area**: {{ alert.area }}
        {% endif %}
        
        **Certainty**: {{ alert.certainty }} | **Severity**: {{ alert.severity }}
        
        {% if alert.resources %}
        [📍 View Alert Map]({{ alert.resources[0].uri }})
        {% endif %}
        
        ---
        {% endfor %}
```

### 6. Severity-Based Color Card

Conditional card that only shows for higher severity alerts:

```yaml
type: conditional
conditions:
  - entity: sensor.met_alerts
    state_not: "No Alert"
card:
  type: markdown
  title: Important Weather Alerts
  content: |
    {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
    {% for alert in alerts %}
      {% if 'orange' in alert.awareness_level_color|lower or 'red' in alert.awareness_level_color|lower %}
    ## ⚠️ {{ alert.title }}
    
    **{{ alert.awareness_level_color|upper }} ALERT**
    
    {{ alert.description }}
    
    **Valid until**: {{ alert.endtime }}
    
    {% if alert.instruction %}
    **Action Required**: {{ alert.instruction }}
    {% endif %}
    
    ---
      {% endif %}
    {% endfor %}
```

### 7. Specific Alert Type Filter

Show only certain types of alerts (e.g., wind warnings):

```yaml
type: markdown
title: Wind Warnings
content: |
  {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
  {% set wind_alerts = alerts | selectattr('event_awareness_name', 'search', 'wind|gale', ignorecase=True) | list %}
  {% if wind_alerts|length > 0 %}
    {% for alert in wind_alerts %}
  **{{ alert.title }}**
  {{ alert.description }}
  Valid: {{ alert.starttime }} to {{ alert.endtime }}
  ---
    {% endfor %}
  {% else %}
  ✅ No active wind warnings
  {% endif %}
```

### 8. Custom Icon Display

Access and display the alert icon in custom cards:

```yaml
type: markdown
content: |
  {% set icon_url = state_attr('sensor.met_alerts', 'entity_picture') %}
  {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
  
  {% if icon_url %}
  <div style="text-align: center;">
    <img src="{{ icon_url }}" width="64" height="64" alt="Alert icon">
    <h3>{{ states('sensor.met_alerts') }} Active Alert(s)</h3>
  </div>
  {% endif %}
  
  {% if alerts and alerts|length > 0 %}
    {% for alert in alerts %}
  **{{ alert.title }}** - {{ alert.awareness_level_color }}
    {% endfor %}
  {% else %}
  ✅ No active weather alerts
  {% endif %}
```

### 9. Multi-Column Layout

Display alerts in a grid:

```yaml
type: grid
cards:
  - type: entity
    entity: sensor.met_alerts
    name: Total Alerts
    icon: mdi:weather-lightning
  - type: markdown
    content: |
      {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
      **Types:**
      {% for alert in alerts %}
      • {{ alert.event_awareness_name }}
      {% endfor %}
  - type: markdown
    content: |
      {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
      **Severity:**
      {% for alert in alerts %}
      • {{ alert.awareness_level_color }}
      {% endfor %}
columns: 3
```

### 10. Time-Based Alert List

Shows when each alert starts and ends:

```yaml
type: markdown
title: Alert Timeline
content: |
  {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
  {% if alerts and alerts|length > 0 %}
  | Alert | Start | End |
  |-------|-------|-----|
    {% for alert in alerts %}
  | {{ alert.event_awareness_name }} | {{ alert.starttime }} | {{ alert.endtime }} |
    {% endfor %}
  {% else %}
  No active alerts
  {% endif %}
```

---

## Automations

### 1. New Alert Notification

Get notified when a new weather alert is issued:

```yaml
automation:
  - alias: "Weather Alert Notification"
    trigger:
      - platform: state
        entity_id: sensor.met_alerts
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state != 'No Alert' }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⚠️ Weather Alert"
          message: |
            {{ states('sensor.met_alerts') }} active alert(s)
            
            {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
            {% if alerts and alerts|length > 0 %}
            {{ alerts[0].title }}: {{ alerts[0].description[:100] }}...
            {% endif %}
          data:
            {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
            {% if alerts and alerts|length > 0 and alerts[0].resources %}
            url: "{{ alerts[0].resources[0].uri }}"
            {% endif %}
            tag: met_alert
            importance: high
```

### 2. High Severity Alert

Only notify for orange and red alerts:

```yaml
automation:
  - alias: "Severe Weather Alert"
    trigger:
      - platform: state
        entity_id: sensor.met_alerts
    condition:
      - condition: template
        value_template: |
          {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
          {% if alerts %}
            {{ alerts | selectattr('awareness_level_color', 'search', 'orange|red', ignorecase=True) | list | length > 0 }}
          {% else %}
            false
          {% endif %}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚨 SEVERE WEATHER ALERT"
          message: |
            {% set alerts = state_attr('sensor.met_alerts', 'alerts') %}
            {% set severe = alerts | selectattr('awareness_level_color', 'search', 'orange|red', ignorecase=True) | list %}
            {{ severe[0].awareness_level_color|upper }}: {{ severe[0].title }}
            
            {{ severe[0].description }}
          data:
            importance: max
            priority: high
```

### 3. Alert Cleared Notification

Get notified when alerts are cleared:

```yaml
automation:
  - alias: "Weather Alert Cleared"
    trigger:
      - platform: state
        entity_id: sensor.met_alerts
        to: "No Alert"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "✅ Weather Alert Cleared"
          message: "All weather alerts have been cleared for your area."
          data:
            tag: met_alert
```

---

## Tips & Tricks

### Working with Alert Arrays

The `alerts` attribute is an array. Here's how to work with it:

```jinja2
{# Get all alerts #}
{% set alerts = state_attr('sensor.met_alerts', 'alerts') %}

{# Count alerts #}
{{ alerts | length }}

{# Get first alert #}
{{ alerts[0].title }}

{# Filter by severity #}
{% set red_alerts = alerts | selectattr('awareness_level_color', 'search', 'red', ignorecase=True) | list %}

{# Filter by type #}
{% set wind_alerts = alerts | selectattr('event_awareness_name', 'search', 'wind', ignorecase=True) | list %}

{# Sort by severity (highest first) #}
{% set sorted_alerts = alerts | sort(attribute='awareness_level_numeric', reverse=True) %}
```

### Available Alert Attributes

Each alert in the array has these attributes:
- `title` - Alert title
- `starttime` - When the alert begins
- `endtime` - When the alert ends
- `description` - Full alert description
- `awareness_level` - Full level string (e.g., "2; yellow; moderate")
- `awareness_level_numeric` - Numeric level (1-4)
- `awareness_level_color` - Color code (yellow, orange, red)
- `certainty` - Certainty level
- `severity` - Severity level
- `instruction` - What to do
- `contact` - Contact information
- `resources` - Array of related resources/maps
- `area` - Affected area
- `event_awareness_name` - Type of alert (wind, rain, etc.)
- `consequences` - Potential consequences

### Icon URLs

The `entity_picture` attribute contains a base64-encoded SVG data URL that works offline:

```yaml
{% set icon = state_attr('sensor.met_alerts', 'entity_picture') %}
<img src="{{ icon }}" width="48" height="48">
```

---

## Benefits

✅ **Single sensor** - All alerts in one place with array mode  
✅ **Automatic icons** - Warning level icons display automatically  
✅ **Flexible filtering** - Use Jinja2 templates to show exactly what you need  
✅ **Offline operation** - Icons are embedded, no external dependencies  
✅ **Real-time updates** - Fetches alerts every 30 minutes  
✅ **Rich data** - Complete alert information including instructions and consequences

---

## Need Help?

- Check the [README](README.md) for configuration options
- See [FRONTEND_EXAMPLES.md](FRONTEND_EXAMPLES.md) for more display ideas
- Report issues on GitHub

**Note**: Replace `sensor.met_alerts` with your actual entity ID if you customized the name during setup.
