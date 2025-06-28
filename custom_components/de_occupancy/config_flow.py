"""Add Config Flow."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .const import CONF_GYMS, CONFIG_VERSION, DOMAIN, GYM_LIST, GYMS

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult
    from homeassistant.helpers.selector import SelectOptionDict

GYM_OPTIONS = cast(
    "list[SelectOptionDict]",
    [{"value": g.id, "label": g.name} for g in GYMS.values()],
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow."""

    VERSION = CONFIG_VERSION

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """First step for users."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors: dict[str, str] = {}
        if user_input:
            return self.async_create_entry(title="Delire Gyms", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_GYMS, default=GYM_LIST): vol.All(
                    SelectSelector(SelectSelectorConfig(options=GYM_LIST, multiple=True)),
                    vol.Length(min=1),
                ),
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
                    vol.Required(CONF_GYMS, default=config_entry.data[CONF_GYMS]): vol.All(
                        SelectSelector(SelectSelectorConfig(options=GYM_LIST, multiple=True)),
                        vol.Length(min=1),
                    ),
                },
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, str]) -> ConfigFlowResult:
        """Forward from import flow from old YAML."""
        return await self.async_step_user(user_input)
