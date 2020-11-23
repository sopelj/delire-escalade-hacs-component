from enum import Enum

DOMAIN = "de_occupancy"
CONF_GYMS = 'gyms'
GYMS = {
    'BPT': 'Beauport',
    'DPB': 'Pierre Bertrand',
    'DLE': 'Ste-Foy',
}
OCCUPANCY_API_URL = "https://www.delirescalade.com/web/wp-json/api/occupancy?skipcache=1&code={code}"
