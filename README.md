![GitHub release (latest by date)](https://img.shields.io/github/v/release/MojoOli/open3e-ha?style=flat-square)
![Issues open](https://img.shields.io/github/stars/MojoOli/open3e-ha?style=flat-square&color=orange&label=Stars)
![commit_activity](https://img.shields.io/github/issues/MojoOli/open3e-ha?color=green&label=Issues&style=flat-square)
# Open3e HomeAssistant Integration

Automatic recognition of Viessmann devices via the Open3e Server and setup of available entities.

<img height="500" src="https://github.com/user-attachments/assets/02e14d18-757c-44f6-b413-0be74dcbb31a" /> <img height="500" src="https://github.com/user-attachments/assets/d7a38dbe-61e5-464e-a2fa-b4a120a3cfff" />

#### Supported Devices

- [x] Vitocal
- [x] Vitoair
- [x] Vitodens
- [x] Vitocharge

## Installation

**This integration needs the Open3e sever in order to communicate with the devices. So make sure its installed and running in listen mode.**

<details>
<summary>Open3e Server Installation Instructions</summary>

There are various ways to run the Open3e server that communicates with this integration. The preferred way is the [HA Addon](https://github.com/flecke-m/ha-addons/tree/main/open3e).

1. Install the HA Addon
2. Make sure your Open3e server runs in listen mode and is connected to MQTT (can all be configured in the config file). 
3. Proceed with installing this integration via the button below.
</details>


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MojoOli&repository=open3e-ha&category=integration)

## Features

- Connects to Open3e via MQTT
- Automatic device discovery and entity setup
- Integrates sensors, climate controls, automations, etc.
- Automatic data refreshing
- Varies data refreshing interval based on integration and enabled entities
- German & English language support
