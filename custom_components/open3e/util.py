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
    Returns a defaultdict mapping each device to a list of entities
    that fully match all their poll_data_features.

    Args:
        coordinator: The Open3eDataUpdateCoordinator instance.
        entities: Iterable of Open3eEntityDescription to match against devices.

    Returns:
        Dict mapping each Open3eDataDevice to a list of matching entities.
    """
    result: Dict[Open3eDataDevice, List[Open3eEntityDescription]] = defaultdict(list)

    for device in coordinator.system_information.devices:
        device_feature_ids = {feature.id for feature in device.features}

        for entity in entities:
            if entity.poll_data_features:
                entity_feature_ids = {f.id for f in entity.poll_data_features}

                # Check that all poll_data_features of sensor exist in device features
                if entity_feature_ids.issubset(device_feature_ids):
                    # If required_device is set, only include if the names match
                    if entity.required_device is None or entity.required_device.display_name == device.name:
                        result[device].append(entity)

    return result
