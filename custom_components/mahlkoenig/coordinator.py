import logging
import asyncio
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from mahlkoenig import Grinder

_LOGGER = logging.getLogger(__name__)

type MahlkonigConfigEntry = ConfigEntry[MahlkonigUpdateCoordinator]


class MahlkonigUpdateCoordinator(DataUpdateCoordinator[None]):
    """Coordinator to fetch all relevant data from my sensor."""

    def __init__(self, hass: HomeAssistant, host: str, port: int):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=self.__class__.__name__,
            update_interval=timedelta(seconds=10),  # Adjust as needed
        )
        session = async_get_clientsession(hass)

        self._grinder = Grinder(host=host, port=port, session=session)

    @property
    def grinder(self) -> Grinder:
        return self._grinder

    @property
    def available(self) -> bool:
        return self._grinder.connected

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        try:
            async with asyncio.timeout(10):
                await self.grinder.connect()
                await self.grinder.request_machine_info()
                await self.grinder.request_wifi_info()
                await self.grinder.request_system_status()
                await self.grinder.request_auto_sleep_time()
                await self.grinder.request_recipe_list()
                await self.grinder.request_statistics()
        except Exception as e:
            _LOGGER.error(e)
            raise UpdateFailed("Init: Error getting device data of Grinder") from e

    async def _async_update_data(self) -> None:
        """Fetch the latest values status from the video matrix."""

        try:
            async with asyncio.timeout(10):
                if not self._grinder.connected:
                    await self._grinder.connect()
                await self._grinder.request_machine_info()
        except Exception as e:
            _LOGGER.error(e)
            await self._grinder.close()
            raise UpdateFailed("Update: Error getting device data of Grinder") from e

        return
