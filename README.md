Disclaimer: This integration is still in an early alpha state and under heavy development, so do not expect a
finished/full working integration. Any contribution is welcome.

# Open3e HomeAssistant Integration

Automatically connects to the Open3e server and handles automatic device/integration/entity setup based on configuration
sent by Open3e. Data is then automatically refreshed.

## Features

- Connects to Open3e via MQTT
- Automatic device/entity setup
- Integrates sensors, climate controls, automations, etc.
- Automatic data refreshing
- Varies data refreshing interval based on integration and enabled entities
- German & English language support

## Supported devices

- [x] Vitocal (Partially)
- [ ] Vitoair
- [ ] Vitodens
- [ ] Vitocharge

I only own a Vitocal, so I would appreciate any contributions regarding the other devices.

## Installation

Note: This integration will be added to HACS later down the line. Until then follow the installation below

You will need the [Open3e config Fork](https://github.com/MojoOli/open3e-config/tree/develop) (hoping to add it to the
official repo in the future). Make sure to get the develop branch as only that branch has the changes. Once installed,
the Open3e server sends a config json on the `[open3e-mqtt-topic]/config` topic.

Once the Open3e server is running, either a new HomeAssistant instance can be setup for a local
development environment (more information can be
found [here](https://github.com/ludeeus/integration_blueprint?tab=readme-ov-file#how)) or the files in the
`custom_component` folder can be moved to the config folder of HomeAssistant.

After that, you can just add the integration to your HomeAssistant instance. Follow the wizard in HA.