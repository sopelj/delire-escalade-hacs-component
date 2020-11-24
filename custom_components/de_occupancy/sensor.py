from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Dict, Optional

from aiohttp import ClientError, ClientSession
from homeassistant import config_entries, core
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
        vol.Required(CONF_GYMS): vol.All(cv.ensure_list, list(GYMS.keys())),
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
    sensors = [DeOccupancySensor(gym_code) for gym_code in config[CONF_GYMS]]
    async_add_entities(sensors, update_before_add=True)


class DeOccupancySensor(Entity):
    def __init__(self, gym: str) -> None:
        super().__init__()
        self.gym: Gym = GYMS[gym]
        self.attrs: Dict[str, Any] = {}
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        return f'{self.gym.name} Occupancy'

    @property
    def unique_id(self) -> str:
        return f'de_{self.gym.id}_occupancy'

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def unit_of_measurement(self):
        return PERCENTAGE

    @property
    def icon(self) -> Optional[str]:
        if self.available is False:
            return 'mdi:account-question-outline'
        if self.state == 0:
            return 'mdi:account-outline'
        if self.state >= 100:
            return 'mdi:account-multiple-remove'
        if self.state >= 50:
            return 'mdi:account-multiple'
        return 'mdi:account'

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    async def fetch_new_attrs(self):
        try:
            async with ClientSession() as session:
                async with session.get(OCCUPANCY_API_URL.format(code=self.gym.code)) as response:
                    data = await response.json()
                
                if data['percent'] >= 95:
                    # Only check the waitlist if over 95%
                    async with session.get(WAITLIST_API_URL.format(code=self.gym.waitlist)) as response:
                        waitlist_data = await response.json()
                    data['waiting'] = waitlist_data['numWaiting']  # number on waitlist
                    data['wait_eta'] = waitlist_data['wait']  # seconds

        except ClientError:
            self._available = False
            _LOGGER.exception("Error retrieving data from DE API.")
            return {}

    async def async_update(self) -> None:
        attrs = {'count': 0, 'percent': 0, 'waiting': 0, 'wait_eta': 0, 'gym': self.gym.name}
        if 8 <= datetime.now().hour <= 22:
            # Only fetch when open
            attrs.update(await self.fetch_new_attrs())
        
        # set values
        self.attrs = attrs
        self._state = 100 if (percent := round(attrs['percent'])) >= 100 else percent
        self._available = True
