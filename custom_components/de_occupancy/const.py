"""Constants for integration."""
from __future__ import annotations

from typing import NamedTuple


class Gym(NamedTuple):
    """Per Gym data."""

    id: str
    code: str
    name: str
    wait_list: str


DOMAIN = "de_occupancy"
CONF_GYMS = "gyms"
GYMS = {
    "beauport": Gym("beauport", "BPT", "Beauport", "beauport"),
    "pierrebertrand": Gym("pierrebertrand", "DPB", "Pierre Bertrand", "delire"),
    "stefoy": Gym("stefoy", "DLE", "Ste-Foy", "delireste-foy"),
    "parc": Gym("parc", "LCE", "DÉLIRE Parc", "parc"),
    "levis": Gym("levis", "DEL", "DÉLIRE Lévis", "levis"),
}
OCCUPANCY_API_URL = (
    "https://www.delirescalade.com/web/wp-json/api/occupancy?skipcache=1&code={code}"
)
WAITLIST_API_URL = "https://api.waitwhile.com/v2/public/locations/{code}"
WAITLIST_JOIN_URL = "https://v2.waitwhile.com/lists/delire/join"
