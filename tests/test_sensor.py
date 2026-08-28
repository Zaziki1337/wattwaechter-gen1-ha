"""Tests for dynamic Wattwächter sensor discovery."""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfFrequency, UnitOfPower

from custom_components.wattwaechter_gen1.sensor import (
    _leaf_paths,
    _metadata_for,
    _name_for,
    _slugify,
    _value_at,
)


def test_leaf_paths_flattens_sensor_data() -> None:
    """Every scalar measurement becomes a sensor and Time is ignored."""
    data = {
        "Time": "2026-08-28T12:00:00",
        "SML": {"Total_in": 123.4, "Power_curr": 456},
    }

    assert list(_leaf_paths(data)) == [
        ("SML", "Total_in"),
        ("SML", "Power_curr"),
    ]
    assert _value_at(data, ("SML", "Power_curr")) == 456


def test_real_wattwaechter_payload() -> None:
    """All fields observed on a real Gen1 device are discovered."""
    data = {
        "Time": "2026-08-28T12:24:29",
        "eHZ": {
            "ID": "0a01454d480000e72e33",
            "meter_import_total": 10144.8,
            "meter_export_total": 122.0,
            "net_frequency": 50.0,
            "actual_power": 2572,
            "current_l1": 9.41,
            "voltage_l1": 229.0,
            "eff_power_l1": 2135,
            "current_l2": 2.40,
            "voltage_l2": 231.5,
            "eff_power_l2": 398,
            "current_l3": 0.41,
            "voltage_l3": 232.6,
            "eff_power_l3": 34,
            "phase_l1_l2": 120,
            "phase_l1_l3": 239,
            "phase_l1": 352,
            "phase_l2": 317,
            "phase_l3": 297,
        },
    }

    paths = list(_leaf_paths(data))

    assert len(paths) == 19
    assert ("eHZ", "ID") in paths
    assert ("eHZ", "actual_power") in paths
    assert ("eHZ", "phase_l3") in paths


def test_metadata_for_common_measurements() -> None:
    """Known Wattwächter fields receive energy dashboard metadata."""
    energy = _metadata_for(("SML", "Total_in"), 123.4)
    power = _metadata_for(("SML", "Power_curr"), 456)

    assert energy.device_class is SensorDeviceClass.ENERGY
    assert energy.unit == UnitOfEnergy.KILO_WATT_HOUR
    assert energy.state_class is SensorStateClass.TOTAL_INCREASING
    assert power.device_class is SensorDeviceClass.POWER
    assert power.unit == UnitOfPower.WATT
    assert power.state_class is SensorStateClass.MEASUREMENT


def test_metadata_for_exact_ehz_fields() -> None:
    """The real Gen1 script fields use explicit metadata and translations."""
    frequency = _metadata_for(("eHZ", "net_frequency"), 50.0)
    phase_angle = _metadata_for(("eHZ", "phase_l1_l2"), 120)
    meter_id = _metadata_for(("eHZ", "ID"), "0a01454d480000e72e33")

    assert frequency.device_class is SensorDeviceClass.FREQUENCY
    assert frequency.unit == UnitOfFrequency.HERTZ
    assert phase_angle.unit == "°"
    assert meter_id.icon == "mdi:identifier"


def test_sensor_name_uses_tasmota_field_name() -> None:
    """Each sensor keeps the distinct name found in StatusSNS."""
    assert _name_for(("eHZ", "meter_import_total")) == "meter_import_total"
    assert _name_for(("eHZ", "actual_power")) == "actual_power"
    assert _name_for(("eHZ", "current_l1")) == "current_l1"


def test_text_values_do_not_receive_numeric_metadata() -> None:
    """Tasmota timestamps containing 'total' are not treated as energy."""
    metadata = _metadata_for(("ENERGY", "TotalStartTime"), "2026-08-28T12:00:00")

    assert metadata.device_class is None
    assert metadata.unit is None
    assert metadata.state_class is None


def test_slugify_obis_code() -> None:
    """OBIS-like field names produce stable unique-id fragments."""
    assert _slugify("1-0:16.7.0") == "1_0_16_7_0"
