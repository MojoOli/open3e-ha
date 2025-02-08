from dataclasses import dataclass

from homeassistant.helpers.entity import EntityDescription

from .features import Feature
from .open3e_data import Open3eDataConfig


@dataclass(frozen=True)
class Open3eEntityDescription(EntityDescription):
    """Generic entity description for Open3e devices."""
    domain: str = "generic"
    poll_data_features: list[Feature] | None = None
    """Defines which features should be polled on a regular basis."""

    def has_features(self, config: Open3eDataConfig):
        has_features = True

        if self.poll_data_features:
            for feature_id in map(lambda feature: feature.id, self.poll_data_features):
                has_id_feature = False

                for device in config.devices:
                    if feature_id in map(lambda entity: entity.id, device.features):
                        has_id_feature = True
                        break

                has_features = has_features and has_id_feature

                if not has_features:
                    break

        return has_features
