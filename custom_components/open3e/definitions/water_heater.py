from dataclasses import dataclass

from homeassistant.const import MAJOR_VERSION

from .entity_description import Open3eEntityDescription
from .features import Features, Feature

if MAJOR_VERSION >= 2025:
    from homeassistant.components.water_heater import WaterHeaterEntityDescription
else:
    from homeassistant.components.water_heater import WaterHeaterEntityEntityDescription as WaterHeaterEntityDescription


@dataclass(frozen=True)
class Open3eWaterHeaterEntityDescription(
    Open3eEntityDescription, WaterHeaterEntityDescription
):
    """Default climate entity description for open3e."""
    domain: str = "water_heater"
    temperature_feature: Feature | None = None
    temperature_target_feature: Feature | None = None
    state_feature: Feature | None = None
    efficiency_mode_feature: Feature | None = None


WATER_HEATER: tuple[Open3eWaterHeaterEntityDescription, ...] = (
    Open3eWaterHeaterEntityDescription(
        poll_data_features=[
            Features.Temperature.DomesticHotWater,
            Features.Temperature.DomesticHotWaterTarget,
            Features.State.DomesticHotWater,
            Features.State.DomesticHotWaterEfficiency
        ],
        temperature_feature=Features.Temperature.DomesticHotWater,
        temperature_target_feature=Features.Temperature.DomesticHotWaterTarget,
        state_feature=Features.State.DomesticHotWater,
        efficiency_mode_feature=Features.State.DomesticHotWaterEfficiency,
        key="water_heater",
        translation_key="water_heater"
    ),
)
