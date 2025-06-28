"""Test component setup."""

from unittest.mock import patch

import pytest
from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData

from custom_components.de_occupancy.const import CONF_GYMS, DOMAIN


def patch_async_setup_entry(return_value=True):
    """Patch async setup entry to return True."""
    return patch(
        "custom_components.de_occupancy.async_setup_entry",
        return_value=return_value,
    )


async def test_step_import(hass: HomeAssistant) -> None:
    """Test importing old config."""
    with patch_async_setup_entry():
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={CONF_GYMS: ["levis"]},
        )
        await hass.async_block_till_done()
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["result"].state == ConfigEntryState.LOADED


async def test_step_user(hass: HomeAssistant) -> None:
    """Test adding new config."""
    with patch_async_setup_entry():
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={},
        )
        await hass.async_block_till_done()
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

    # Try submitting without a gym selected
    with patch_async_setup_entry(), pytest.raises(InvalidData):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_GYMS: []},
        )

    await hass.async_block_till_done()
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Submit with a gym selected
    with patch_async_setup_entry():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_GYMS: ["levis"]},
        )

    await hass.async_block_till_done()
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["result"].state == ConfigEntryState.LOADED
