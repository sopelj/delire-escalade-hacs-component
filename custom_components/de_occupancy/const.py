"""Constants for integration."""

from __future__ import annotations

from typing import Literal, NamedTuple

type GYM_ID = Literal["pierrebertrand", "stefoy", "parc", "levis"]
type DELIRE_CODE = Literal["DPB", "DLE", "LCE", "DEL"]
type WAITLIST_CODE = Literal["delire", "delireste-foy", "parc", "levis"]


class Gym(NamedTuple):
    """Per Gym data."""

    id: GYM_ID
    name: str
    code: DELIRE_CODE
    wait_list: WAITLIST_CODE


DOMAIN = "de_occupancy"
CONF_GYMS = "gyms"
CONFIG_VERSION = 1

GYMS: dict[GYM_ID, Gym] = {
    "pierrebertrand": Gym("pierrebertrand", "Pierre Bertrand", "DPB", "delire"),
    "stefoy": Gym("stefoy", "Ste-Foy", "DLE", "delireste-foy"),
    "parc": Gym("parc", "DÉLIRE Parc", "LCE", "parc"),
    "levis": Gym("levis", "DÉLIRE Lévis", "DEL", "levis"),
}
GYM_LIST: list[str] = list(GYMS)
OCCUPANCY_API_URL = "https://www.delirescalade.com/web/wp-json/api/occupancy?skipcache=1&code={code}"
WAITLIST_API_URL = "https://api.waitwhile.com/v2/public/locations/{code}"
WAITLIST_JOIN_URL = "https://v2.waitwhile.com/lists/delire/join"
