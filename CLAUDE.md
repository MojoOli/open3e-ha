# open3e-ha

Home Assistant custom integration (`custom_components/open3e`, domain `open3e`) for Viessmann E3 devices — Vitocal,
Vitoair, Vitodens, Vitocharge. It never talks to the hardware directly: it sends commands over **MQTT** to an
[Open3e](https://github.com/open3e/open3e) server running in listen mode, which turns them into UDS requests on the
CAN bus and publishes the answers back to MQTT.

## Data flow

```
HA entity ──► coordinator ──► Open3eMqttClient ──► Open3eCommandGate ──► <mqtt_cmnd>  (default open3e/cmnd)
                                                                              │
                                                              open3e server (UDS over CAN)
                                                                              │
HA entity ◄── MQTT subscription per feature topic ◄──────────── <mqtt_topic>/<didName>  (default open3e/...)
```

1. **Setup** (`coordinator._async_setup`): wait for `<topic>/LWT` == `online` → publish `{"mode":"system"}` → server
   answers on `<topic>/system` with every ECU (`id` = CAN tx address, `name`, serial, versions, and a `features` list of
   `{id, topic}` — one per DID it knows). Device type is matched by substring: `HPMU`→Vitocal, `VCU`→Vitoair,
   `HMU`→Vitodens, `EMCU`→Vitocharge (`definitions/devices.py`). Unknown ECUs are dropped.
2. **Capability probe** (`api.__set_devices_capabilities`): reads the DIDs in `capability/capability.py`; a value other
   than the "unavailable" sentinel adds the `Capability` (e.g. `Circuit2`) to the device.
3. **Entity creation** (`util.map_devices_to_entities`): a description is created for a device only if
   `required_device` matches, **all** `poll_data_features` IDs are in the device's feature list, and all
   `required_capabilities` were detected.
4. **Polling**: entities register their features with the coordinator (`on_entity_added`). Every 5 s the coordinator
   sends one `{"mode":"read-json","addr":<ecu>,"data":[ids]}` per device for features whose `refresh_interval` has
   elapsed. The shortest interval among entities sharing a feature wins.
5. **Updates are push, not coordinator-driven**: each entity subscribes to its feature topics; `_handle_coordinator_update`
   is a deliberate no-op. Raw payload lands in `self.data[feature_id]` → `async_on_data()`.
6. **Writes**: platform → `description.set_*` lambda → `coordinator.async_set_*` → `api.async_set_*` →
   `{"mode":"write","addr":<ecu>,"data":[["<did>" or "<did>.<SubField>", "<json-encoded value>"]]}`, then
   `async_refresh_feature` re-reads the DID after 2 s.

## Layout

- `__init__.py` — setup/unload, config-entry migration (VERSION 3; unique IDs `open3e_<slug(name_serial_key)>`).
- `api.py` — all MQTT I/O. One `async_set_*` per write type. `coordinator.py` mirrors each with a thin wrapper.
- `command_gate.py` — single lock + 0.25 s spacing for **every** outgoing command; paused on HA stop/unload.
- `entity.py` — `Open3eEntity` base (subscriptions, entity_id/unique_id, device link).
- `<platform>.py` — thin HA platform classes. Logic belongs in `definitions/`, not here.
- `definitions/features.py` — `Features.<Group>.<Name> = Feature(id=<DID>, refresh_interval=<s|None>)`.
- `definitions/<platform>s.py` — the `SENSORS` / `NUMBERS` / ... tuples of entity descriptions.
- `definitions/subfeatures/` — enums + parsers for complex/enum payloads, and API mapping (`to_api`, `map_to_api`).
- `capability/capability.py` — runtime hardware detection.
- `translations/en.json`, `de.json` — every user-facing string.

## Dev environment

Runs in the devcontainer (`.devcontainer.json`, Python 3.14 image; HA `2026.6.4` needs ≥ 3.14). Everything uses the
project venv at `./.venv`, created by the `postCreateCommand`.

- `scripts/setup` — install `requirements.txt` into `.venv`.
- `scripts/develop` — run HA with `config/` and `custom_components/` on `PYTHONPATH`, debug logging. UI on port 8123.
- `scripts/test` — stdlib `unittest` over `tests/` (install `requirements_test.txt` first). CI runs the same plus
  hassfest and HACS validation.
- No linter is configured in the repo. Ruff is the formatter in the editor; don't reformat files you didn't touch.
- HA in the devcontainer needs the MQTT integration pointed at a broker that a dev Open3e instance publishes to.
  Real hardware is on the other end — see Safety.

If `.venv/bin/hass` fails with "required file not found", the venv was created at a different mount path. Delete
`.venv` and re-run `python3 -m venv .venv && scripts/setup`.

## Rules

- **Data-driven.** New entities = a `Feature` + an entity description (+ subfeature parser if needed) + translations.
  Only touch platform classes, `api.py` or `coordinator.py` when a genuinely new write shape is needed.
- **Define the feature first** in `features.py`; never use a bare DID number in a description. The same DID may appear
  under several names (e.g. 268 for Vitocal `Flow` and Vitodens `FlowTemperatureSensor`) — that's intentional.
- **Always extend the `Open3e*EntityDescription` subclasses.** Set `required_device` when a DID means different things
  on different devices; set `required_capabilities` for optional hardware (circuits 2–4, rooms, Fan2). If unsure
  whether a capability or device restriction applies, **ask** — don't guess.
- **`key` == `translation_key`**, snake_case, and present in **both** `en.json` and `de.json` under
  `entity.<platform>.<key>.name`. English sentence case ("Flow temperature"); German standard nouns
  ("Vorlauftemperatur").
- **Never change an existing `key`.** It is part of the unique ID and entity ID — renaming orphans users' entities and
  history. If it must change, add a migration in `__init__.py` and bump `VERSION` in `config_flow.py`.
- **Unavailable sentinels:** `VIESSMANN_UNAVAILABLE_VALUE` (-3276.8) and `VITODENS_UNAVAILABLE_VALUE` (127) in
  `const.py`. Filter them in `available` or the retriever; never surface them as real readings.
- **Parsers must tolerate old and new Open3e formats** (plain value vs. `{"ID":..,"Text":..}` enum vs. complex dict) and
  return `None` on bad input instead of raising. Follow `subfeatures/domestic_hot_water_status.py`.
- **Upstream field names are copied verbatim**, typos included: DID 533 uses `"Acutual"`; the ventilation-level write
  depends on it. Don't "fix" these.
- **Typing:** strict hints (`list[Feature] | None`). Naming: PascalCase classes, snake_case functions/keys,
  UPPER_SNAKE constants, `__name` for private members, `_name` for protected.

## Safety: this drives real heating hardware

- **All outgoing traffic goes through `Open3eCommandGate`.** Never call `mqtt.async_publish` to the command topic
  directly. The Open3e server's UDS stack handles one request at a time; bursts or requests during shutdown wedge it
  ("Global request timeout") until the Open3e container is restarted.
- Keep `refresh_interval` as long as the value allows (multiples of 5 s; 5 s only for fast-changing temperatures,
  300 s for setpoints, `None` for write-only features). Every polled DID is CAN bus load.
- Don't send writes to the real device to "test" something without the user's go-ahead. Writes change heat pump
  behaviour (modes, setpoints, heater power, DHW).
- Clamp `number` entities to the ranges in `const.py` / the device's real limits.

## Upstream reference (open3e)

DID definitions live in `src/open3e/Open3Edatapoints.py` (general) plus per-device overlays
`Open3EdatapointsVcal.py`, `Vdens`, `Vair`, `Vx3`; enums in `Open3Eenums.py`. Each DID is a codec:
`O3EComplexType(len, "Name", [subfields...])` → JSON dict keyed by subfield names; `O3EEnum` → `{"ID": n, "Text": ".."}`;
`O3EInt16(..., scale)` / `O3EByteVal` → bare number. The `/check-datapoints` skill walks through comparing these with
`features.py`.

## Workflows

- `/add-entity` — add a sensor/number/select/... for a DID end to end.
- `/check-datapoints` — diff the integration against upstream Open3e datapoints and fix changed payload shapes.
