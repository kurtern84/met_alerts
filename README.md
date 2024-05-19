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
