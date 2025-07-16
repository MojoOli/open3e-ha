> [!NOTE]
> This integration is still in a beta state and under development. Any contribution is welcome.

# Open3e HomeAssistant Integration

Automatically connects to the Open3e server and handles automatic device/integration/entity setup based on configuration
sent by Open3e. Data is then automatically refreshed.

## Features

- Connects to Open3e via MQTT
- Automatic device discovery and entity setup
- Integrates sensors, climate controls, automations, etc.
- Automatic data refreshing
- Varies data refreshing interval based on integration and enabled entities
- German & English language support

## Supported devices

- [x] Vitocal
- [x] Vitoair (In-Progress)
- [ ] Vitodens
- [x] Vitocharge

I only own a Vitocal, so I would appreciate any contributions regarding the other devices.

If there are any features missing, which you would like to have, just make an issue on this repo.

## Installation

Install [Open3e](https://github.com/open3e/open3e/issues) on your device. You can either directly run it on the system, use a [HA Addon](https://github.com/flecke-m/ha-addons/tree/main/open3e), or run it in a [docker container](https://hub.docker.com/r/fleckem/open3e). Follow the setup provided by the specific option u chose.

Start the Open3e server with the default arguments. Only an MQTT connection to the broker and listen is necessary. Such a config (args
file) looks like this:

```
--can
can0
--mqtt
127.0.0.1:1883:open3e
--mqttformatstring
{device}_{ecuAddr:03X}_{didNumber}_{didName}
--listen
open3e/cmnd
--config
devices.json
```

Once the Open3e server is running and you have a connection to your MQTT broker in HA, you can add this repository as a custom repository in HACS. Install the integration
and you are good to go. Follow the wizard in HA.
