"""Setup sensor platform."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
import logging
from typing import TypedDict

from aiohttp import ClientError, ClientSession
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import PERCENTAGE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import CONF_GYMS, GYMS, OCCUPANCY_API_URL, WAITLIST_API_URL, Gym

_LOGGER = logging.getLogger(__name__)

# Time between updating data from API
SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_GYMS): vol.All(cv.ensure_list, list(GYMS)),
    },
)

DEFAULT_ATTRS_VALUES = {
    "count": 0,
    "percent": 0,
    "waiting": 0,
    "wait_eta": 0,
    "friendly_wait_eta": "",
}


class StateAttrDict(TypedDict):
    """State Attribute data."""

    count: int
    percent: int
    waiting: int
    wait_eta: int
    friendly_wait_eta: str


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    sensors = [DeOccupancySensor(gym_code) for gym_code in config[CONF_GYMS]]
    async_add_entities(sensors, update_before_add=True)


def format_seconds(seconds: int) -> str:
    """Format seconds for display."""
    minutes = seconds // 60 % 60
    hours = seconds // 60 // 60
    output = []
    if hours:
        output.append(f'{hours} hour{"" if hours == 1 else "s"}')
    if minutes:
        output.append(f"{minutes}min")
    return " ".join(output) or "0min"


class DeOccupancySensor(Entity):
    """Occupancy sensor for gyn."""

    def __init__(self, gym: str) -> None:
        """Set up the sensor."""
        self.gym: Gym = GYMS[gym]
        self._state = None
        self._available = True
        self._attr_available = True
        self._attr_name = f"{self.gym.name} Occupancy"
        self._attr_unique_id = f"de_{self.gym.id}_occupancy"
        self._attr_unit_of_measurement = PERCENTAGE
        self._attr_extra_state_attributes: StateAttrDict = {
            "gym": self.gym.name,
        } | DEFAULT_ATTRS_VALUES
        super().__init__()

    @property
    def state(self) -> int | None:
        """State value."""
        return self._state

    @property
    def icon(self) -> str | None:
        """Icon for sensor."""
        if self.available is False:
            return "mdi:account-question-outline"
        if self.state == 0:
            return "mdi:account-outline"
        if self.state >= 100:
            return "mdi:account-multiple-remove"
        if self.state >= 50:
            return "mdi:account-multiple"
        return "mdi:account"

    async def fetch_new_attrs(self) -> dict[str, str | int]:
        """Fetch data from APIs based on gym and occupancy."""
        try:
            async with ClientSession() as session:
                async with session.get(
                    OCCUPANCY_API_URL.format(code=self.gym.code),
                ) as response:
                    data = await response.json()

                if data["percent"] >= 90:
                    # Only check the wait-list if over 95%
                    async with session.get(
                        WAITLIST_API_URL.format(code=self.gym.wait_list),
                    ) as response:
                        wait_list_data = await response.json()
                    data.update(
                        waiting=wait_list_data[
                            "numWaiting"
                        ],  # number of people on wait list
                        wait_eta=wait_list_data["wait"],  # ETA in seconds
                        friendly_wait_eta=format_seconds(wait_list_data["wait"]),
                    )
                return data

        except ClientError:
            self._available = False
            _LOGGER.exception("Error retrieving data from DE API.")
            return {}

    async def async_update(self) -> None:
        """Perform update."""
        if 7 <= datetime.now().hour <= 22:
            # Only fetch when open
            new_values = await self.fetch_new_attrs()
        else:
            new_values = DEFAULT_ATTRS_VALUES

        # set values
        self._available = True
        self._attr_extra_state_attributes.update(new_values)
        self._state = (
            100 if (percent := round(new_values["percent"])) >= 100 else percent
        )
