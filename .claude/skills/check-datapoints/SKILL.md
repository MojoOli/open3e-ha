---
name: check-datapoints
description: Cross-check the open3e integration's features and parsers against the latest upstream Open3e datapoint definitions and fix payload-shape changes. Use when the user asks to sync with upstream Open3e, after an Open3e release, or when entities show wrong/unavailable values or parse errors after an Open3e update.
---

# Check integration against upstream Open3e datapoints

## 1. Fetch upstream

```
https://raw.githubusercontent.com/open3e/open3e/refs/heads/master/src/open3e/Open3Edatapoints.py
https://raw.githubusercontent.com/open3e/open3e/refs/heads/master/src/open3e/Open3Eenums.py
```

Plus the device overlays relevant to the question: `Open3EdatapointsVcal.py` (Vitocal), `Vdens` (Vitodens),
`Vair` (Vitoair), `Vx3`. An overlay entry replaces the general one; `None` means unchanged.

## 2. Compare

For every `Feature(id=...)` in `custom_components/open3e/definitions/features.py`, find the upstream DID and check:

- **Codec changed** — e.g. `O3EInt16`/`O3EByteVal` → `O3EEnum` (payload becomes `{"ID":..,"Text":..}`) or
  → `O3EComplexType` (payload becomes a dict).
- **Subfield renamed/added/removed** — compare against the keys used by retrievers, `get_native_value` lambdas,
  write `sub_feature=` arguments in `api.py`, and `capability.py` `path=`.
- **Enum IDs/texts changed** — compare `Open3Eenums.py` with the maps in `definitions/subfeatures/`.
- **Access changed** (`ro`/`rw`) for anything the integration writes.
- **DID removed** for a device — entities silently stop being created; flag it to the user.

Upstream typos are real field names (`"Acutual"` on DID 533). Match them exactly.

## 3. Fix, staying backward compatible

Users run older Open3e versions. Parsers must accept **both** old and new shapes:

```python
def get_my_feature_value(data: Any) -> MyEnum | None:
    try:
        if isinstance(data, str) and data.strip().startswith("{"):
            payload = json_loads(data)
            raw_id = payload.get("ID") if payload.get("ID") is not None else payload.get("State", {}).get("ID")
            if raw_id is None:
                return None
            value = int(raw_id)
        else:
            value = int(data)          # legacy plain value
        return MY_MAP.get(value)
    except (TypeError, ValueError, KeyError):
        return None
```

- Put the parser in `definitions/subfeatures/` and use it as `data_retriever`.
- Binary sensors moving to a complex type: `POWERSTATE_COMPLEX` or a custom `data_transform`.
- Never rename entity `key`s as part of a sync.

## 4. Report and verify

- Summarise for the user: what changed upstream, what was adapted, what was only flagged.
- `scripts/test`, then `scripts/develop` and check the HA log for parse errors.
