"""Setup the actual sensors."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal

import voluptuous as vol
from aiohttp import ClientError
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EMPTY_DATA, DeOccupancyAPI
from .const import CONF_GYMS, DOMAIN, GYM_ID, GYMS, Gym

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .api import GymDataDict

    class StateAttrDict(GymDataDict):
        """Full state dict."""

        gym: str

    from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


_LOGGER = logging.getLogger(__name__)

# Time between updating data from API
SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_GYMS): vol.All(cv.ensure_list, list(GYMS)),
    },
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Entities."""
    if config_entry.entry_id is None:
        raise ValueError("Missing config entry ID")

    config = hass.data[DOMAIN][config_entry.entry_id]
    if config_entry.options:
        config.update(config_entry.options)

    session = async_get_clientsession(hass)
    api = DeOccupancyAPI(session)
    sensors = [DeOccupancySensor(gym_code, api) for gym_code in config[CONF_GYMS]]
    async_add_entities(sensors, update_before_add=True)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up Entities."""
    session = async_get_clientsession(hass)
    api = DeOccupancyAPI(session)
    sensors = [DeOccupancySensor(gym_code, api) for gym_code in config[CONF_GYMS]]
    async_add_entities(sensors, update_before_add=True)


class DeOccupancySensor(SensorEntity):
    """Occupancy sensor for gym."""

    def __init__(self, gym: GYM_ID, api: DeOccupancyAPI) -> None:
        """Set up the sensor."""
        self.gym: Gym = GYMS[gym]
        self._api = api
        self._state = None
        self._available = True
        self._attr_translation_key = "occupancy"
        self._attr_available = True
        self._attr_name = f"{self.gym.name} Occupancy"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_extra_state_attributes = {"gym": self.gym.name} | EMPTY_DATA
        super().__init__()

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self) -> str | None:
        """Icon for sensor."""
        if not self.available:
            return "mdi:account-question-outline"
        if self.state == 0:
            return "mdi:account-outline"
        if self.state >= 100:
            return "mdi:account-multiple-remove"
        if self.state >= 50:
            return "mdi:account-multiple"
        return "mdi:account"

    async def fetch_new_attrs(self) -> GymDataDict | Literal[False]:
        """Fetch data from APIs based on gym and occupancy."""
        try:
            return await self._api.fetch_gym_info(self.gym.code, self.gym.wait_list)
        except ClientError:
            self._attr_available = False
            _LOGGER.exception("Error retrieving data from DE API.")
            return False

    async def async_update(self) -> None:
        """Perform update."""
        new_data: GymDataDict = EMPTY_DATA
        if (7 <= datetime.now().hour <= 22) and (updated_values := await self.fetch_new_attrs()):
            new_data = updated_values

        # set values
        self._attr_available = True
        self._attr_extra_state_attributes = new_data | {"gym": self.gym.name}
        self._state = min(round(new_data["percent"]), 100)  # type: ignore[assignment]
