---
name: add-entity
description: Add a new Home Assistant entity (sensor, binary sensor, number, select, switch, climate, water heater, fan) for an Open3e DID to the open3e integration. Use when the user asks to add/expose/support a datapoint, value, setting or DID number.
---

# Add an entity for an Open3e DID

## 1. Pin down the DID

- Get the DID number and target device (Vitocal / Vitoair / Vitodens / Vitocharge) from the user.
- Look it up upstream: `Open3Edatapoints.py`, and the device overlay (`Open3EdatapointsVcal.py`, `Vdens`, `Vair`,
  `Vx3`) — the overlay wins if it redefines the DID.
  Raw: `https://raw.githubusercontent.com/open3e/open3e/refs/heads/master/src/open3e/<file>`
- Note: codec type, subfield names (copy verbatim, typos included), unit, scale, `acc` (`ro` → read-only entity,
  `rw` → number/select/switch possible).
- Check `definitions/features.py` — the DID may already exist under another name or device.
- Decide whether it is optional hardware (circuit 2–4, room sensor, second fan). If unclear, **ask the user**.

## 2. Feature (`definitions/features.py`)

```python
MyThing = Feature(id=1234, refresh_interval=30)   # 5 fast temps, 30 typical, 300 setpoints, None write-only
```

## 3. Payload parsing

Payload is the raw MQTT string. Pick the retriever by codec:

| Codec | Payload | Use |
|---|---|---|
| `O3EComplexType` | `{"Actual": 21.5, ...}` | `SensorDataRetriever.ACTUAL` etc., or a new lambda for other fields |
| `O3EEnum` | `{"ID": 1, "Text": "On"}` | new parser in `definitions/subfeatures/<name>.py` |
| `O3EInt*` / `O3EByteVal` | `21.5` | `SensorDataRetriever.RAW` |

Enum/complex parsers: copy the shape of `subfeatures/domestic_hot_water_status.py` — accept the legacy plain value
and the JSON form, return `None` on any error.

## 4. Entity description (`definitions/<platform>s.py`)

Add to the platform tuple (`SENSORS`, `NUMBERS`, ...), near related entries:

```python
Open3eSensorEntityDescription(
    poll_data_features=[Features.Temperature.MyThing],
    device_class=SensorDeviceClass.TEMPERATURE,
    key="my_thing",
    translation_key="my_thing",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
    data_retriever=SensorDataRetriever.ACTUAL,
    required_device=Open3eDevices.Vitocal,
    required_capabilities=[Capability.Circuit2],   # only for optional hardware
),
```

- Numbers: `get_native_value` gets the **parsed** JSON (`json_loads` already applied), `set_native_value` is
  `lambda value, device, coordinator: coordinator.async_set_<x>(...)`. Set min/max/step from `const.py` or the device's
  real limits.
- Writes reuse an existing `coordinator.async_set_*` whenever the payload shape matches (`<did>` plain value or
  `<did>.<SubField>`). Only if none fits: add `api.async_set_<x>` (built with `__write_json_payload`, sent through
  `__async_publish_command`) **and** the matching coordinator wrapper ending in `self.async_refresh_feature(...)`.
- Derived values from several DIDs → `DERIVED_SENSORS` with `data_retrievers` + `compute_value`.

## 5. Translations

Add `entity.<platform>.<key>.name` to **both** `translations/en.json` (sentence case) and `translations/de.json`.
Select/enum states go under `state`. Add an icon in `icons.json` if similar entities have one.

## 6. Verify

- `scripts/test` passes.
- Run `scripts/develop`, check the log for errors from `custom_components.open3e`, and confirm the entity appears and
  shows a plausible value (not -3276.8 / 127).
- Don't trigger writes against the real device without the user's OK.
