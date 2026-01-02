from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from homeassistant.components.number import NumberEntityDescription, NumberDeviceClass
from homeassistant.const import UnitOfTemperature, UnitOfPower, PERCENTAGE

from custom_components.open3e.definitions.subfeatures.buffer import Buffer
from custom_components.open3e.definitions.subfeatures.hysteresis import Hysteresis
from custom_components.open3e.definitions.subfeatures.program import Program
from custom_components.open3e.definitions.subfeatures.smart_grid_temperature_offsets import SmartGridTemperatureOffsets
from custom_components.open3e.definitions.subfeatures.temperature_cooling import TemperatureCooling
from .devices import Open3eDevices
from .entity_description import Open3eEntityDescription
from .features import Features
from .open3e_data import Open3eDataDevice
from .subfeatures.dhw_hysteresis import DhwHysteresis
from .subfeatures.heating_curve import HeatingCurve
from .. import Open3eDataUpdateCoordinator
from ..capability.capability import Capability
from ..const import VIESSMANN_TEMP_HEATING_MIN, VIESSMANN_TEMP_HEATING_MAX, VIESSMANN_POWER_MAX_WATT_ELECTRICAL_HEATER, \
    VIESSMANN_POWER_MIN_WATT_ELECTRICAL_HEATER, VIESSMANN_POWER_WATT_ELECTRICAL_HEATER_STEP, \
    VIESSMANN_SMART_GRID_TEMP_MIN, VIESSMANN_SMART_GRID_TEMP_MAX, VIESSMANN_HYSTERESIS_MIN, VIESSMANN_HYSTERESIS_MAX


@dataclass(frozen=True)
class Open3eNumberEntityDescription(
    Open3eEntityDescription, NumberEntityDescription
):
    """Default number entity description for open3e."""
    domain: str = "number"
    get_native_value: Callable[[Any], float] = None
    set_native_value: Callable[[float, Open3eDataDevice, Open3eDataUpdateCoordinator], Awaitable[None]] = None


NUMBERS: tuple[Open3eNumberEntityDescription, ...] = (

    ###############
    ### VITOCAL ###
    ###############

    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit1.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_1_reduced_temperature",
        translation_key="circuit_1_reduced_temperature",
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit1.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_1_standard_temperature",
        translation_key="circuit_1_standard_temperature",
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit1.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_1_comfort_temperature",
        translation_key="circuit_1_comfort_temperature",
        required_capabilities=[Capability.Circuit1],
        required_device=Open3eDevices.Vitocal
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit2.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_2_reduced_temperature",
        translation_key="circuit_2_reduced_temperature",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit2.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_2_standard_temperature",
        translation_key="circuit_2_standard_temperature",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit2.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_2_comfort_temperature",
        translation_key="circuit_2_comfort_temperature",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit3.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_3_reduced_temperature",
        translation_key="circuit_3_reduced_temperature",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit3.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_3_standard_temperature",
        translation_key="circuit_3_standard_temperature",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit3.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_3_comfort_temperature",
        translation_key="circuit_3_comfort_temperature",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit4.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_4_reduced_temperature",
        translation_key="circuit_4_reduced_temperature",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit4.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_4_standard_temperature",
        translation_key="circuit_4_standard_temperature",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_heating()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit4.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_4_comfort_temperature",
        translation_key="circuit_4_comfort_temperature",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit1.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_1_reduced_cooling",
        translation_key="circuit_1_reduced_cooling",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit1.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_1_standard_cooling",
        translation_key="circuit_1_standard_cooling",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit1.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_1_comfort_cooling",
        translation_key="circuit_1_comfort_cooling",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit2.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_2_reduced_cooling",
        translation_key="circuit_2_reduced_cooling",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit2.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_2_standard_cooling",
        translation_key="circuit_2_standard_cooling",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit2],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit2.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_2_comfort_cooling",
        translation_key="circuit_2_comfort_cooling",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit3.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_3_reduced_cooling",
        translation_key="circuit_3_reduced_cooling",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit3.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_3_standard_cooling",
        translation_key="circuit_3_standard_cooling",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit3],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit3.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_3_comfort_cooling",
        translation_key="circuit_3_comfort_cooling",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit4.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
        key="circuit_4_reduced_cooling",
        translation_key="circuit_4_reduced_cooling",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Normal.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit4.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
        key="circuit_4_standard_cooling",
        translation_key="circuit_4_standard_cooling",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.CoolingProgramsCircuit4],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Comfort.map_to_api_cooling()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature_cooling(
            set_programs_feature_id=Features.Temperature.CoolingProgramsCircuit4.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_4_comfort_cooling",
        translation_key="circuit_4_comfort_cooling",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Power.MaxElectricalHeater],
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        native_min_value=VIESSMANN_POWER_MIN_WATT_ELECTRICAL_HEATER,
        native_max_value=VIESSMANN_POWER_MAX_WATT_ELECTRICAL_HEATER,
        native_step=VIESSMANN_POWER_WATT_ELECTRICAL_HEATER_STEP,
        get_native_value=lambda data: data,
        set_native_value=lambda value, device, coordinator: coordinator.async_set_max_power_electrical_heater(
            feature_id=Features.Power.MaxElectricalHeater.id,
            max_power=value,
            device=device
        ),
        key="heater_max_power",
        translation_key="heater_max_power"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.SmartGridTemperatureOffsets],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_SMART_GRID_TEMP_MIN,
        native_max_value=VIESSMANN_SMART_GRID_TEMP_MAX,
        get_native_value=lambda data: data[SmartGridTemperatureOffsets.IncreaseRoomTemperatureHeating],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_smart_grid_temperature_offset(
            feature_id=Features.Temperature.SmartGridTemperatureOffsets.id,
            offset=SmartGridTemperatureOffsets.IncreaseRoomTemperatureHeating,
            value=value,
            device=device
        ),
        key="smartgrid_increase_heating_room_temperature",
        translation_key="smartgrid_increase_heating_room_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.SmartGridTemperatureOffsets],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-down",
        native_min_value=VIESSMANN_SMART_GRID_TEMP_MIN,
        native_max_value=VIESSMANN_SMART_GRID_TEMP_MAX,
        get_native_value=lambda data: data[SmartGridTemperatureOffsets.DecreaseRoomTemperatureCooling],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_smart_grid_temperature_offset(
            feature_id=Features.Temperature.SmartGridTemperatureOffsets.id,
            offset=SmartGridTemperatureOffsets.DecreaseRoomTemperatureCooling,
            value=value,
            device=device
        ),
        key="smartgrid_decrease_cooling_room_temperature",
        translation_key="smartgrid_decrease_cooling_room_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.SmartGridTemperatureOffsets],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_SMART_GRID_TEMP_MIN,
        native_max_value=VIESSMANN_SMART_GRID_TEMP_MAX,
        get_native_value=lambda data: data[SmartGridTemperatureOffsets.IncreaseBufferTemperatureHeating],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_smart_grid_temperature_offset(
            feature_id=Features.Temperature.SmartGridTemperatureOffsets.id,
            offset=SmartGridTemperatureOffsets.IncreaseBufferTemperatureHeating,
            value=value,
            device=device
        ),
        key="smartgrid_increase_heating_buffer_temperature",
        translation_key="smartgrid_increase_heating_buffer_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.SmartGridTemperatureOffsets],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-down",
        native_min_value=VIESSMANN_SMART_GRID_TEMP_MIN,
        native_max_value=VIESSMANN_SMART_GRID_TEMP_MAX,
        get_native_value=lambda data: data[SmartGridTemperatureOffsets.DecreaseBufferTemperatureCooling],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_smart_grid_temperature_offset(
            feature_id=Features.Temperature.SmartGridTemperatureOffsets.id,
            offset=SmartGridTemperatureOffsets.DecreaseBufferTemperatureCooling,
            value=value,
            device=device
        ),
        key="smartgrid_decrease_cooling_buffer_temperature",
        translation_key="smartgrid_decrease_cooling_buffer_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.SmartGridTemperatureOffsets],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_SMART_GRID_TEMP_MIN,
        native_max_value=VIESSMANN_SMART_GRID_TEMP_MAX,
        get_native_value=lambda data: data[SmartGridTemperatureOffsets.IncreaseDHWTemperature],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_smart_grid_temperature_offset(
            feature_id=Features.Temperature.SmartGridTemperatureOffsets.id,
            offset=SmartGridTemperatureOffsets.IncreaseDHWTemperature,
            value=value,
            device=device
        ),
        key="smartgrid_increase_dhw_temperature",
        translation_key="smartgrid_increase_dhw_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1Cooling],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=25,
        get_native_value=lambda data: data[TemperatureCooling.EffectiveSetTemperature],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_temperature_cooling(
            feature_id=Features.Temperature.FlowCircuit1Cooling.id,
            value=value,
            device=device
        ),
        key="heating_circuit_1_flow_setpoint_cooling",
        translation_key="heating_circuit_1_flow_setpoint_cooling",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit2Cooling],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=25,
        get_native_value=lambda data: data[TemperatureCooling.EffectiveSetTemperature],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_temperature_cooling(
            feature_id=Features.Temperature.FlowCircuit2Cooling.id,
            value=value,
            device=device
        ),
        key="heating_circuit_2_flow_setpoint_cooling",
        translation_key="heating_circuit_2_flow_setpoint_cooling",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit3Cooling],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=25,
        get_native_value=lambda data: data[TemperatureCooling.EffectiveSetTemperature],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_temperature_cooling(
            feature_id=Features.Temperature.FlowCircuit3Cooling.id,
            value=value,
            device=device
        ),
        key="heating_circuit_3_flow_setpoint_cooling",
        translation_key="heating_circuit_3_flow_setpoint_cooling",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit4Cooling],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=25,
        get_native_value=lambda data: data[TemperatureCooling.EffectiveSetTemperature],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_temperature_cooling(
            feature_id=Features.Temperature.FlowCircuit4Cooling.id,
            value=value,
            device=device
        ),
        key="heating_circuit_4_flow_setpoint_cooling",
        translation_key="heating_circuit_4_flow_setpoint_cooling",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.On],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit1CoolingHysteresis.id,
            hysteresis=Hysteresis.On,
            value=value,
            device=device
        ),
        key="heating_circuit_1_cooling_hysteresis_on",
        translation_key="heating_circuit_1_cooling_hysteresis_on",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit2CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.On],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit2CoolingHysteresis.id,
            hysteresis=Hysteresis.On,
            value=value,
            device=device
        ),
        key="heating_circuit_2_cooling_hysteresis_on",
        translation_key="heating_circuit_2_cooling_hysteresis_on",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit3CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.On],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit3CoolingHysteresis.id,
            hysteresis=Hysteresis.On,
            value=value,
            device=device
        ),
        key="heating_circuit_3_cooling_hysteresis_on",
        translation_key="heating_circuit_3_cooling_hysteresis_on",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit4CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.On],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit4CoolingHysteresis.id,
            hysteresis=Hysteresis.On,
            value=value,
            device=device
        ),
        key="heating_circuit_4_cooling_hysteresis_on",
        translation_key="heating_circuit_4_cooling_hysteresis_on",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-lines",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.Off],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit1CoolingHysteresis.id,
            hysteresis=Hysteresis.Off,
            value=value,
            device=device
        ),
        key="heating_circuit_1_cooling_hysteresis_off",
        translation_key="heating_circuit_1_cooling_hysteresis_off",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit2CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-lines",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.Off],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit2CoolingHysteresis.id,
            hysteresis=Hysteresis.Off,
            value=value,
            device=device
        ),
        key="heating_circuit_2_cooling_hysteresis_off",
        translation_key="heating_circuit_2_cooling_hysteresis_off",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit3CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-lines",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.Off],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit3CoolingHysteresis.id,
            hysteresis=Hysteresis.Off,
            value=value,
            device=device
        ),
        key="heating_circuit_3_cooling_hysteresis_off",
        translation_key="heating_circuit_3_cooling_hysteresis_off",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit4CoolingHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-lines",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.Off],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit4CoolingHysteresis.id,
            hysteresis=Hysteresis.Off,
            value=value,
            device=device
        ),
        key="heating_circuit_4_cooling_hysteresis_off",
        translation_key="heating_circuit_4_cooling_hysteresis_off",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.BufferMinMax],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=25,
        get_native_value=lambda data: data[Buffer.Min],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_buffer_temperature(
            feature_id=Features.Temperature.BufferMinMax.id,
            buffer=Buffer.Min,
            value=value,
            device=device
        ),
        key="buffer_min_temperature",
        translation_key="buffer_min_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.BufferMinMax],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-high",
        native_min_value=25,
        native_max_value=75,
        get_native_value=lambda data: data[Buffer.Max],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_buffer_temperature(
            feature_id=Features.Temperature.BufferMinMax.id,
            buffer=Buffer.Max,
            value=value,
            device=device
        ),
        key="buffer_max_temperature",
        translation_key="buffer_max_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.CircuitFrostProtection],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:snowflake-melt",
        native_min_value=-9,
        native_max_value=3,
        get_native_value=lambda data: data["Temperature"],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_frost_protection_temperature(
            feature_id=Features.State.CircuitFrostProtection.id,
            value=value,
            device=device
        ),
        key="frost_protection_temperature",
        translation_key="frost_protection_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit1HeatingCurve],
        icon="mdi:slope-uphill",
        native_min_value=0.2,
        native_max_value=3.5,
        native_step=0.1,
        get_native_value=lambda data: data[HeatingCurve.Gradient],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit1HeatingCurve.id,
            heating_curve=HeatingCurve.Gradient,
            value=value,
            device=device
        ),
        key="circuit_1_heating_curve_slope",
        translation_key="circuit_1_heating_curve_slope",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit2HeatingCurve],
        icon="mdi:slope-uphill",
        native_min_value=0.2,
        native_max_value=3.5,
        native_step=0.1,
        get_native_value=lambda data: data[HeatingCurve.Gradient],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit2HeatingCurve.id,
            heating_curve=HeatingCurve.Gradient,
            value=value,
            device=device
        ),
        key="circuit_2_heating_curve_slope",
        translation_key="circuit_2_heating_curve_slope",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit3HeatingCurve],
        icon="mdi:slope-uphill",
        native_min_value=0.2,
        native_max_value=3.5,
        native_step=0.1,
        get_native_value=lambda data: data[HeatingCurve.Gradient],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit3HeatingCurve.id,
            heating_curve=HeatingCurve.Gradient,
            value=value,
            device=device
        ),
        key="circuit_3_heating_curve_slope",
        translation_key="circuit_3_heating_curve_slope",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit4HeatingCurve],
        icon="mdi:slope-uphill",
        native_min_value=0.2,
        native_max_value=3.5,
        native_step=0.1,
        get_native_value=lambda data: data[HeatingCurve.Gradient],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit4HeatingCurve.id,
            heating_curve=HeatingCurve.Gradient,
            value=value,
            device=device
        ),
        key="circuit_4_heating_curve_slope",
        translation_key="circuit_4_heating_curve_slope",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit1HeatingCurve],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:plus-minus-variant",
        native_min_value=-13,
        native_max_value=40,
        native_step=1,
        get_native_value=lambda data: data[HeatingCurve.Level],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit1HeatingCurve.id,
            heating_curve=HeatingCurve.Level,
            value=value,
            device=device
        ),
        key="circuit_1_heating_curve_level",
        translation_key="circuit_1_heating_curve_level",
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit2HeatingCurve],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:plus-minus-variant",
        native_min_value=-13,
        native_max_value=40,
        native_step=1,
        get_native_value=lambda data: data[HeatingCurve.Level],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit2HeatingCurve.id,
            heating_curve=HeatingCurve.Level,
            value=value,
            device=device
        ),
        key="circuit_2_heating_curve_level",
        translation_key="circuit_2_heating_curve_level",
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit3HeatingCurve],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:plus-minus-variant",
        native_min_value=-13,
        native_max_value=40,
        native_step=1,
        get_native_value=lambda data: data[HeatingCurve.Level],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit3HeatingCurve.id,
            heating_curve=HeatingCurve.Level,
            value=value,
            device=device
        ),
        key="circuit_3_heating_curve_level",
        translation_key="circuit_3_heating_curve_level",
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.FlowCircuit4HeatingCurve],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:plus-minus-variant",
        native_min_value=-13,
        native_max_value=40,
        native_step=1,
        get_native_value=lambda data: data[HeatingCurve.Level],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_heating_curve(
            feature_id=Features.State.FlowCircuit4HeatingCurve.id,
            heating_curve=HeatingCurve.Level,
            value=value,
            device=device
        ),
        key="circuit_4_heating_curve_level",
        translation_key="circuit_4_heating_curve_level",
        required_capabilities=[Capability.Circuit4]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=0,
        native_max_value=10,
        native_step=1,
        get_native_value=lambda data: data[DhwHysteresis.On],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_dhw_hysteresis(
            feature_id=Features.Temperature.DomesticHotWaterHysteresis.id,
            hysteresis=DhwHysteresis.On,
            value=value,
            device=device
        ),
        key="dhw_hysteresis_on",
        translation_key="dhw_hysteresis_on"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.DomesticHotWaterHysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-down",
        native_min_value=0,
        native_max_value=10,
        native_step=1,
        get_native_value=lambda data: data[DhwHysteresis.Off],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_dhw_hysteresis(
            feature_id=Features.Temperature.DomesticHotWaterHysteresis.id,
            hysteresis=DhwHysteresis.Off,
            value=value,
            device=device
        ),
        key="dhw_hysteresis_off",
        translation_key="dhw_hysteresis_off"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Speed.Circuit1Pump],
        native_unit_of_measurement=PERCENTAGE,
        device_class=NumberDeviceClass.SPEED,
        icon="mdi:pump",
        native_min_value=20,
        native_max_value=100,
        native_step=1,
        get_native_value=lambda data: data["Setpoint"],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_circuit_pump_speed(
            feature_id=Features.Speed.Circuit1Pump.id,
            speed=value,
            device=device
        ),
        key="circuit_1_pump_speed",
        translation_key="circuit_1_pump_speed",
        required_device=Open3eDevices.Vitocal,
        required_capabilities=[Capability.Circuit1]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Speed.Circuit2Pump],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pump",
        native_min_value=20,
        native_max_value=100,
        native_step=1,
        get_native_value=lambda data: data["Setpoint"],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_circuit_pump_speed(
            feature_id=Features.Speed.Circuit2Pump.id,
            value=value,
            device=device
        ),
        key="circuit_2_pump_speed",
        translation_key="circuit_2_pump_speed",
        required_device=Open3eDevices.Vitocal,
        required_capabilities=[Capability.Circuit2]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Speed.Circuit3Pump],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pump",
        native_min_value=20,
        native_max_value=100,
        native_step=1,
        get_native_value=lambda data: data["Setpoint"],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_circuit_pump_speed(
            feature_id=Features.Speed.Circuit3Pump.id,
            value=value,
            device=device
        ),
        key="circuit_3_pump_speed",
        translation_key="circuit_3_pump_speed",
        required_device=Open3eDevices.Vitocal,
        required_capabilities=[Capability.Circuit3]
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Speed.Circuit4Pump],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:pump",
        native_min_value=20,
        native_max_value=100,
        native_step=1,
        get_native_value=lambda data: data["Setpoint"],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_circuit_pump_speed(
            feature_id=Features.Speed.Circuit4Pump.id,
            value=value,
            device=device
        ),
        key="circuit_4_pump_speed",
        translation_key="circuit_4_pump_speed",
        required_device=Open3eDevices.Vitocal,
        required_capabilities=[Capability.Circuit4]
    ),
    
    ##################
    ### Vitocharge ###
    ##################
    Open3eNumberEntityDescription(
        poll_data_features=[Features.State.BackUpBox],
        native_unit_of_measurement=PERCENTAGE,
        device_class=NumberDeviceClass.BATTERY,
        icon="mdi:battery",
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        get_native_value=lambda data: data["DischargeLimit"],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_backup_box_discharge_limit_percentage(
            feature_id=Features.State.BackUpBox.id,
            backup_box_discharge_limit_percentage=value,
            device=device
        ),
        key="backup_box_discharge_limit_percentage",
        translation_key="backup_box_discharge_limit_percentage",
        required_device=Open3eDevices.Vitocharge,
    ),
)
