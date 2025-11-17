from collections import defaultdict
from typing import Iterable, Dict, List

from custom_components.open3e import Open3eDataUpdateCoordinator
from custom_components.open3e.definitions.entity_description import Open3eEntityDescription
from custom_components.open3e.definitions.open3e_data import Open3eDataDevice


def map_devices_to_entities(
        coordinator: Open3eDataUpdateCoordinator,
        entities: Iterable[Open3eEntityDescription]
) -> Dict[Open3eDataDevice, List[Open3eEntityDescription]]:
    """
    Maps each device to a list of entities that match all their poll_data_features,
    required capabilities, and optional required_device.
    """
    result: Dict[Open3eDataDevice, List[Open3eEntityDescription]] = defaultdict(list)

    for device in coordinator.system_information.devices:
        device_feature_ids = {f.id for f in device.features}

        for entity in entities:
            # Skip if required_device is set and doesn't match
            if entity.required_device and entity.required_device.display_name != device.name:
                continue

            # Skip if poll_data_features are missing
            if entity.poll_data_features and not {f.id for f in entity.poll_data_features}.issubset(device_feature_ids):
                continue

            # Skip if required_capabilities are missing
            if entity.required_capabilities and not set(entity.required_capabilities).issubset(device.capabilities):
                continue

            # All checks passed
            result[device].append(entity)

    return result
