"""Tests for Wattwächter integration options."""

import pytest
import voluptuous as vol

from custom_components.wattwaechter_gen1.config_flow import OPTIONS_SCHEMA
from custom_components.wattwaechter_gen1.const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


def test_polling_interval_default() -> None:
    """The default polling interval is two seconds."""
    assert OPTIONS_SCHEMA({})[CONF_SCAN_INTERVAL] == DEFAULT_SCAN_INTERVAL == 2


@pytest.mark.parametrize(
    "scan_interval", [MIN_SCAN_INTERVAL, 5, 30, MAX_SCAN_INTERVAL]
)
def test_polling_interval_accepts_valid_values(scan_interval: int) -> None:
    """Valid whole-second polling intervals are accepted."""
    assert OPTIONS_SCHEMA({CONF_SCAN_INTERVAL: scan_interval}) == {
        CONF_SCAN_INTERVAL: scan_interval
    }


@pytest.mark.parametrize("scan_interval", [0, 1, MAX_SCAN_INTERVAL + 1])
def test_polling_interval_rejects_invalid_values(scan_interval: int) -> None:
    """Polling faster than two seconds or excessively slowly is rejected."""
    with pytest.raises(vol.Invalid):
        OPTIONS_SCHEMA({CONF_SCAN_INTERVAL: scan_interval})
