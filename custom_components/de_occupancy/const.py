from collections import namedtuple

Gym = namedtuple('Gym', 'id code name waitlist')

DOMAIN = "de_occupancy"
CONF_GYMS = 'gyms'
GYMS = {
    'beauport': Gym('beauport', 'BPT', 'Beauport', 'beauport'),
    'pierrebertrand': Gym('pierrebertrand', 'DPB', 'Pierre Bertrand', 'delire'),
    'stefoy': Gym('stefoy', 'DLE', 'Ste-Foy', 'delireste-foy'),
    'parc': Gym('parc', 'LCE', 'DÉLIRE Parc', 'parc'),
}
OCCUPANCY_API_URL = "https://www.delirescalade.com/web/wp-json/api/occupancy?skipcache=1&code={code}"
WAITLIST_API_URL = "https://api.waitwhile.com/v2/public/locations/{code}"
WAITLIST_JOIN_URL = "https://v2.waitwhile.com/lists/delire/join"
