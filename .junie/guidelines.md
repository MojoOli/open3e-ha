### Project Introduction: Open3e Home Assistant Integration

The `open3e-ha` project is a Home Assistant (HA) integration for Viessmann heating systems (Vitocal, Vitoair, Vitodens,
Vitocharge). It communicates with the **Open3e server** via **MQTT**. Instead of hardcoding entities for each device,
the project uses a **data-driven architecture** where entities are dynamically discovered and instantiated based on
the "Features" and "Capabilities" supported by the specific connected hardware.

---

### Junie Guidelines & Rules

#### 1. Code Style and Structure

- **Data-Driven Definitions:** Avoid adding logic to `sensor.py`, `number.py`, etc. Most entity logic (data retrieval,
  validation, and transformations) should be placed in `custom_components/open3e/definitions/`.
- **Entity Descriptions:** Always use or extend the custom `Open3eEntityDescription` subclasses (e.g.,
  `Open3eSensorEntityDescription`, `Open3eNumberEntityDescription`). These classes bridge HA entity properties with
  Open3e features.
- **Typing:** Use Python type hints strictly (e.g., `list[Feature] | None`).
- **Translations:** All user-facing strings (entity names, step descriptions) must be in
  `custom_components/open3e/translations/` (`en.json` and `de.json`). Use translation keys in code.

#### 2. Key Components Usage

- **Features (`definitions/features.py`):** This is the source of truth for Open3e Feature IDs. Always define a new
  feature here first before using it in an entity description.
- **Capabilities (`capability/capability.py`):** Use this to define optional hardware features (e.g., `Circuit2`,
  `Fan2`). Capabilities are detected at runtime by checking if a specific Feature ID returns a valid value.
    - **Ask the User:** If you are unsure whether a capability check is required for a specific feature, or which device
      a feature belongs to, always ask the user for clarification.
- **Entity Matching (`util.py`):** The `map_devices_to_entities` function automatically filters which entities to create
  based on `poll_data_features`, `required_device`, and `required_capabilities` defined in the entity description.

#### 3. Implementation Patterns

- **Data Retrievers:** For simple sensors, use `data_retriever` (a callable) within the entity description to parse the
  incoming MQTT JSON payload.
- **Derived Sensors:** Use `Open3eDerivedSensor` when a value depends on multiple Open3e features (e.g., COP
  calculation).
- **MQTT Communication:** Use the `Open3eMqttClient` in `api.py` for all outgoing commands. It handles the specific
  JSON/raw payload formatting required by Open3e.
- **Availability:** Many Viessmann values indicate "unavailable" with specific constants (e.g., `0x7FFF` / `3276.7`).
  Use `VIESSMANN_UNAVAILABLE_VALUE` or `VITODENS_UNAVAILABLE_VALUE` from `const.py` to handle these in the `available`
  property or data filters.

#### 4. File Organization

- `definitions/`: Houses all entity descriptions categorized by platform (sensors, numbers, switches, etc.).
- `definitions/subfeatures/`: Contains logic for complex data types or enums (e.g., HVAC modes, heating curves).
- `capability/`: Logic for runtime hardware discovery.
- `api.py`: The MQTT interface layer.
- `coordinator.py`: Manages the global state and refresh intervals for polled features.

#### 5. Naming Conventions and Casing

- **Classes:** Use `PascalCase` (e.g., `Open3eSensor`, `Open3eEntityDescription`).
- **Variables & Functions:** Use `snake_case` (e.g., `async_setup_entry`, `poll_data_features`).
- **Constants:** Use `UPPER_SNAKE_CASE` (e.g., `VIESSMANN_UNAVAILABLE_VALUE`, `DOMAIN`).
- **Private Members:** Prefix with double underscores `__` for strict privacy (e.g., `self.__mqtt_topics`).
- **Protected Members:** Prefix with single underscore `_` (e.g., `self._attr_native_value`).
- **Translation Keys:** Use `snake_case` in JSON files (e.g., `"flow_temperature"`). Nested structure follows HA
  standards: `entity.<platform>.<key>.name`.
- **Translations Content:**
    - **English (`en.json`):** Use sentence case (e.g., `"Flow temperature"`). Only the first word is capitalized.
    - **German (`de.json`):** Follow standard German capitalization rules (e.g., `"Vorlauftemperatur"`,
      `"Energieverbrauch Heizung heute"`).
- **Entity Keys:** Use `snake_case` for `EntityDescription.key` (e.g., `key="flow_temperature"`). These keys MUST match
  the translation keys in the translation files.
- **Feature Names:** Defined as attributes in `Features` class using `PascalCase` (e.g., `Features.Temperature.Flow`).

#### 6. Adding New Entities (Example)

When adding a new entity, follow these steps using the data structure from
[`Open3Edatapoints.py`](https://github.com/open3e/open3e/blob/develop/src/open3e/Open3Edatapoints.py):

1. **Define the Feature (`features.py`):**
   ```python
   class Features:
       class Temperature:
           MyNewSensor = Feature(id=123, refresh_interval=30)
   ```
2. **Define the Entity Description (`definitions/sensors.py` or `numbers.py`):**
   If the MQTT JSON is `{"Actual": 21.5, "Minimum": 15.0, ...}`, use `SensorDataRetriever.ACTUAL`.
   ```python
   Open3eSensorEntityDescription(
       poll_data_features=[Features.Temperature.MyNewSensor],
       device_class=SensorDeviceClass.TEMPERATURE,
       key="my_new_sensor",
       translation_key="my_new_sensor",
       native_unit_of_measurement=UnitOfTemperature.CELSIUS,
       state_class=SensorStateClass.MEASUREMENT,
       data_retriever=SensorDataRetriever.ACTUAL,
       required_device=Open3eDevices.Vitocal,
       required_capabilities=[Capability.Circuit1] # Optional: only create if Capability.Circuit1 is detected
   )
   ```
3. **Add Translations (`translations/en.json`):**
   ```json
   "entity": {
     "sensor": {
       "my_new_sensor": { "name": "My new sensor" }
     }
   }
   ```

**Skill Tip:** Always check the JSON structure in `Open3Edatapoints.py`. This file can be found in the
[open3e repository](https://github.com/open3e/open3e) specifically at
[Open3Edatapoints.py](https://github.com/open3e/open3e/blob/develop/src/open3e/Open3Edatapoints.py).
For example, if a datapoint returns a complex
JSON like `{"Day": 1, "Month": 3, "Year": 2024}`, you may need a custom `data_retriever` lambda or a subfeature class
to parse it.
