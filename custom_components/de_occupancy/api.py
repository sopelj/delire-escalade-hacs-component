"""Basic API for isolating logic from Home Assistant component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import DELIRE_CODE, OCCUPANCY_API_URL, WAITLIST_API_URL, WAITLIST_CODE

if TYPE_CHECKING:
    from typing import TypedDict

    from aiohttp import ClientSession

    class DelireApiResponse(TypedDict):
        """Delire API response."""

        percent: int
        count: int
        gym: str

    class WaitlistApiResponse(TypedDict):
        """Waitlist API response."""

        numWaiting: int
        wait: int  # ETA in seconds

    class GymDataDict(TypedDict):
        """All gym data."""

        count: int
        percent: int
        waiting: int
        wait_eta: int
        friendly_wait_eta: str


EMPTY_DATA: GymDataDict = {
    "count": 0,
    "percent": 0,
    "waiting": 0,
    "wait_eta": 0,
    "friendly_wait_eta": "",
}


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


class DeOccupancyAPI:
    """API object for sharing sessions and isolating code.."""

    def __init__(self, session: ClientSession) -> None:
        """Initialize the API object and store the session."""
        self._session = session

    async def fetch_gym_info(self, delire: DELIRE_CODE, waitlist: WAITLIST_CODE) -> GymDataDict:
        """Fetch new information by codes."""
        async with self._session.get(
            OCCUPANCY_API_URL.format(code=delire),
        ) as response:
            resp: DelireApiResponse = await response.json()

        data = EMPTY_DATA | {"percent": resp["percent"], "count": resp["count"]}
        if resp["percent"] >= 90:
            # Only check the wait-list if over 95%
            async with self._session.get(
                WAITLIST_API_URL.format(code=waitlist),
            ) as response:
                wait_list_data: WaitlistApiResponse = await response.json()
            data |= {
                "waiting": wait_list_data["numWaiting"],
                "wait_eta": wait_list_data["wait"],
                "friendly_wait_eta": format_seconds(wait_list_data["wait"]),
            }
        return data
