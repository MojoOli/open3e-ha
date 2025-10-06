from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from homeassistant.components.number import NumberEntityDescription, NumberDeviceClass
from homeassistant.const import UnitOfTemperature, UnitOfPower

from .buffer import Buffer
from .entity_description import Open3eEntityDescription
from .features import Features
from .hysteresis import Hysteresis
from .open3e_data import Open3eDataDevice
from .program import Program
from .smart_grid_temperature_offsets import SmartGridTemperatureOffsets
from .temperature_cooling import TemperatureCooling
from .. import Open3eDataUpdateCoordinator
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
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.ProgramsCircuit1],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=VIESSMANN_TEMP_HEATING_MIN,
        native_max_value=VIESSMANN_TEMP_HEATING_MAX,
        native_step=1,
        get_native_value=lambda data: data[Program.Reduced.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit1.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Normal.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit1.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Comfort.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit1.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Reduced.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit2.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Normal.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit2.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Comfort.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit2.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Reduced.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit3.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Normal.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit3.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Comfort.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit3.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Reduced.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit4.id,
            program=Program.Reduced,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Normal.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit4.id,
            program=Program.Normal,
            temperature=value,
            device=device
        ),
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
        get_native_value=lambda data: data[Program.Comfort.map_to_api()],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_program_temperature(
            set_programs_feature_id=Features.Temperature.ProgramsCircuit4.id,
            program=Program.Comfort,
            temperature=value,
            device=device
        ),
        key="circuit_4_comfort_temperature",
        translation_key="circuit_4_comfort_temperature",
        entity_registry_enabled_default=False
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
        key="heating_circuit_flow_setpoint_cooling",
        translation_key="heating_circuit_flow_setpoint_cooling"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1Hysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-chevron-up",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.On],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit1Hysteresis.id,
            hysteresis=Hysteresis.On,
            value=value,
            device=device
        ),
        key="heating_circuit_cooling_hysteresis_on",
        translation_key="heating_circuit_cooling_hysteresis_on"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.FlowCircuit1Hysteresis],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-lines",
        native_min_value=VIESSMANN_HYSTERESIS_MIN,
        native_max_value=VIESSMANN_HYSTERESIS_MAX,
        get_native_value=lambda data: data[Hysteresis.Off],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_hysteresis(
            feature_id=Features.Temperature.FlowCircuit1Hysteresis.id,
            hysteresis=Hysteresis.Off,
            value=value,
            device=device
        ),
        key="heating_circuit_cooling_hysteresis_off",
        translation_key="heating_circuit_cooling_hysteresis_off"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.Buffer],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=25,
        get_native_value=lambda data: data[Buffer.Min],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_buffer_temperature(
            feature_id=Features.Temperature.Buffer.id,
            buffer=Buffer.Min,
            value=value,
            device=device
        ),
        key="buffer_min_temperature",
        translation_key="buffer_min_temperature"
    ),
    Open3eNumberEntityDescription(
        poll_data_features=[Features.Temperature.Buffer],
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-high",
        native_min_value=25,
        native_max_value=75,
        get_native_value=lambda data: data[Buffer.Max],
        set_native_value=lambda value, device, coordinator: coordinator.async_set_buffer_temperature(
            feature_id=Features.Temperature.Buffer.id,
            buffer=Buffer.Max,
            value=value,
            device=device
        ),
        key="buffer_max_temperature",
        translation_key="buffer_max_temperature"
    ),
)
