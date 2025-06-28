"""Test Sensor entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import entity_registry as er

from custom_components.de_occupancy.const import GYMS

from .conftest import setup_platform

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from custom_components.de_occupancy.api import DeOccupancyAPI


STE_FOY_SENSOR_ID = "sensor.ste_foy_occupancy"

async def test_setup_sensors(
    hass: HomeAssistant,
    mock_api: DeOccupancyAPI,
) -> None:
    """Initialize and test sensors."""
    assert len(hass.states.async_all()) == 0

    mock_api.fetch_gym_info.return_value = {
        'percent': 45,
        'wait_eta': 60,
        "friendly_wait_eta": "1min",
        'waiting': 3,
        'count': 150,
    }
    await setup_platform(hass, ["stefoy"], mock_api)
    assert len(hass.states.async_all()) == 1

    # Ste-Foy Sensor
    ste_foy_state = hass.states.get(STE_FOY_SENSOR_ID)
    assert ste_foy_state is not None
    assert ste_foy_state.attributes == {
        'friendly_name': 'Ste-Foy Occupancy',
        'icon': 'mdi:account',
        'count': 150,
       'friendly_wait_eta': '1min',
       'gym': 'Ste-Foy',
       'percent': 45,
       'unit_of_measurement': '%',
       'wait_eta': 60,
       'waiting': 3
    }
    assert ste_foy_state.state == "45"

