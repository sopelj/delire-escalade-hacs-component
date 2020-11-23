from datetime import timedelta
import logging
from typing import Any, Callable, Dict, Optional

from aiohttp import ClientError, ClientSession
from homeassistant import config_entries, core
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from .const import CONF_GYMS, OCCUPANCY_API_URL, Gym

_LOGGER = logging.getLogger(__name__)

# Time between updating data from API
SCAN_INTERVAL = timedelta(minutes=10)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_GYMS): vol.All(cv.ensure_list, cv.enum(Gym)),
    }
)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """
    Set up the sensor platform
    """
    sensors = [DeOccupancySensor(gym) for gym in config[CONF_GYMS]]
    async_add_entities(sensors, update_before_add=True)


class DeOccupancySensor(Entity):
    def __init__(self, gym: str) -> None:
        super().__init__()
        self.gym = gym
        self.attrs: Dict[str, Any] = {'location': self.gym}
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        return self.gym

    @property
    def unique_id(self) -> str:
        return self.gym

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    async def async_update(self):
        try:
            async with ClientSession() as session:
                async with session.get(OCCUPANCY_API_URL.format(code=self.gym)) as response:
                    data = await response.json()
                    self.attrs['count'] = data['count']
                    self.attrs['percent'] = data['percent']
                    self._state = f"{data['percent']:.2f}%"
                    self._available = True
        except ClientError:
            self._available = False
            _LOGGER.exception("Error retrieving data from DE API.")
