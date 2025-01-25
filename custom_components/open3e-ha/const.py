"""Constants for open3e-ha."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "open3e-ha"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

MQTT_CMD = "mqtt_cmnd"
MQTT_CMD_DEFAULT = "open3e/cmnd"
MQTT_CONFIG_TOPIC = "open3e/config"