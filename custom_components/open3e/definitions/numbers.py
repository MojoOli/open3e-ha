from dataclasses import dataclass

from homeassistant.components.number import NumberEntityDescription, NumberDeviceClass
from homeassistant.const import UnitOfTemperature

from .entity_description import Open3eEntityDescription
from .features import Features
from .program import Program
from ..const import VIESSMANN_TEMP_HEATING_MIN, VIESSMANN_TEMP_HEATING_MAX


@dataclass(frozen=True)
class Open3eNumberEntityDescription(
    Open3eEntityDescription, NumberEntityDescription
):
    """Default number entity description for open3e."""
    domain: str = "number"
    program: Program | None = None
    """Describes the key that is used"""


NUMBERS: tuple[Open3eNumberEntityDescription, ...] = (
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Reduced,
        key="circuit_1_reduced_temperature",
        translation_key="circuit_1_reduced_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Standard,
        key="circuit_1_standard_temperature",
        translation_key="circuit_1_standard_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Comfort,
        key="circuit_1_comfort_temperature",
        translation_key="circuit_1_comfort_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Reduced,
        key="circuit_2_reduced_temperature",
        translation_key="circuit_2_reduced_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Standard,
        key="circuit_2_standard_temperature",
        translation_key="circuit_2_standard_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Comfort,
        key="circuit_2_comfort_temperature",
        translation_key="circuit_2_comfort_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Reduced,
        key="circuit_3_reduced_temperature",
        translation_key="circuit_3_reduced_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Standard,
        key="circuit_3_standard_temperature",
        translation_key="circuit_3_standard_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Comfort,
        key="circuit_3_comfort_temperature",
        translation_key="circuit_3_comfort_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Reduced,
        key="circuit_4_reduced_temperature",
        translation_key="circuit_4_reduced_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Standard,
        key="circuit_4_standard_temperature",
        translation_key="circuit_4_standard_temperature",
        entity_registry_enabled_default=False
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        program=Program.Comfort,
        key="circuit_4_comfort_temperature",
        translation_key="circuit_4_comfort_temperature",
        entity_registry_enabled_default=False
    ),
)
