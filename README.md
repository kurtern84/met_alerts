# Met_Alerts
A plugin for Home Assistant that displays extreme weather warning from MetAlert's API  (Yr.no)



### Installation

Step 1:  Create a new folder for your custom component in Home Assistant's custom_components folder.

```
/Home-Assistant/_data/custom_components/met_alerts
```

Clone this repository:

```

git clone https://github.com/kurtern84/met_alerts.git
```

Edit configuration.yaml:

```
sensor:
  - platform: met_alerts
    name: Met Alerts
    latitude: 60.67659
    longitude: 10.81997
```

Updated Lovelace configuration

```
type: entities
title: MET Alerts
show_header_toggle: false
entities:
  - entity: sensor.met_alerts
    name: Event
  - type: attribute
    entity: sensor.met_alerts
    attribute: title
    name: Title
  - type: attribute
    entity: sensor.met_alerts
    attribute: description
    name: Description
  - type: attribute
    entity: sensor.met_alerts
    attribute: awareness_level
    name: Awareness Level
  - type: attribute
    entity: sensor.met_alerts
    attribute: certainty
    name: Certainty
  - type: attribute
    entity: sensor.met_alerts
    attribute: severity
    name: Severity
  - type: attribute
    entity: sensor.met_alerts
    attribute: instruction
    name: Instruction
  - type: attribute
    entity: sensor.met_alerts
    attribute: contact
    name: Contact
  - type: attribute
    entity: sensor.met_alerts
    attribute: area
    name: Area
  - type: attribute
    entity: sensor.met_alerts
    attribute: event_awareness_name
    name: Event Awareness Name
  - type: attribute
    entity: sensor.met_alerts
    attribute: consequences
    name: Consequences

```

Markdown cards for resources

```
type: markdown
title: Resources
content: >
  {% if state_attr('sensor.met_alerts', 'resources') %}
  {% for resource in state_attr('sensor.met_alerts', 'resources') %}
  - [{{ resource.description }}]({{ resource.uri }})
  {% endfor %}
  {% else %}
  No resources available.
  {% endif %}

```
