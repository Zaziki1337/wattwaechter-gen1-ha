"""Tests for the Wattwächter Tasmota client helpers."""

import pytest

from custom_components.wattwaechter_gen1.api import normalize_host


@pytest.mark.parametrize(
    ("raw_host", "expected"),
    [
        ("192.168.1.42", "192.168.1.42"),
        ("wattwaechter.local", "wattwaechter.local"),
        ("http://wattwaechter.local/", "wattwaechter.local"),
        ("192.168.1.42:8080", "192.168.1.42:8080"),
    ],
)
def test_normalize_host(raw_host: str, expected: str) -> None:
    """Hosts accepted by the config flow are normalized consistently."""
    assert normalize_host(raw_host) == expected


@pytest.mark.parametrize(
    "raw_host",
    ["", "http://wattwaechter.local/api", "wattwaechter.local?cmnd=Status"],
)
def test_normalize_host_rejects_non_hosts(raw_host: str) -> None:
    """Paths and query strings must not become part of the device URL."""
    with pytest.raises(ValueError):
        normalize_host(raw_host)

