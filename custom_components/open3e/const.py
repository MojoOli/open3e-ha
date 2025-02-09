"""Constants for open3e."""

DOMAIN = "open3e"

MQTT_CMD_KEY = "mqtt_cmnd"
MQTT_CMD_DEFAULT = "open3e/cmnd"
MQTT_CONFIG_TOPIC = "open3e/config"
MQTT_CONFIG_PAYLOAD = '{"mode":"config"}'

VIESSMANN_TEMP_HEATING_MIN = 3
VIESSMANN_TEMP_HEATING_MAX = 37