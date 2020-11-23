from collections import namedtuple

Gym = namedtuple('Gym', 'id code name')

DOMAIN = "de_occupancy"
CONF_GYMS = 'gyms'
GYMS = {
    'beauport': Gym('beauport', 'BPT', 'Beauport'),
    'pierrebertrand': Gym('pierrebertrand', 'DPB', 'Pierre Bertrand'),
    'stefoy': Gym('stefoy', 'DLE', 'Ste-Foy'),
}
OCCUPANCY_API_URL = "https://www.delirescalade.com/web/wp-json/api/occupancy?skipcache=1&code={code}"
