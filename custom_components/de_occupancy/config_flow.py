"""Add Config Flow for Ember Mug."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .const import CONF_GYMS, CONFIG_VERSION, DOMAIN, GYMS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for Ember Mug."""

    VERSION = CONFIG_VERSION

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """First step for users."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        if user_input:
            return self.async_create_entry(title="Delire Gyms", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_GYMS): vol.All(cv.ensure_list, list(GYMS), default=list(GYMS)),
            },
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle reconfiguration."""
        errors: dict[str, str] = {}
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"],
        )
        if not config_entry:
            return self.async_abort(reason="invalid")

        if user_input is not None:
            return self.async_update_reload_and_abort(
                config_entry,
                unique_id=config_entry.unique_id,
                data={**config_entry.data, **user_input},
                reason="reconfigure_successful",
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_GYMS): vol.All(
                        cv.ensure_list,
                        list(GYMS),
                        default=config_entry.data[CONF_GYMS],
                    ),
                },
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, str]) -> ConfigFlowResult:
        """Forward from import flow from old YAML."""
        return await self.async_step_user(user_input)
