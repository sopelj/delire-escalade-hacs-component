"""Configure pytest."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (  # type: ignore[import-untyped]
    MockConfigEntry,
)

from custom_components.de_occupancy.api import DeOccupancyAPI
from custom_components.de_occupancy.const import CONF_GYMS, DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def _auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""


@pytest.fixture
def mock_api() -> DeOccupancyAPI:
    """Create a mocked Delire API instance."""
    mock_session = Mock()
    api = DeOccupancyAPI(mock_session)
    api.fetch_gym_info = AsyncMock(return_value={})  # type: ignore[method-assign]
    return api


async def setup_platform(
    hass: HomeAssistant,
    gyms: list[str],
    api: DeOccupancyAPI,
    config_entry: MockConfigEntry | None = None,
) -> MockConfigEntry:
    """Load the integration with the provided gym(s)."""
    if config_entry is None:
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data={CONF_GYMS: gyms},
        )

    await async_setup_component(hass, DOMAIN, {})
    config_entry.add_to_hass(hass)
    with patch("custom_components.de_occupancy.api.DeOccupancyAPI", lambda x: api):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
    return config_entry
