import logging
import asyncio
from datetime import timedelta, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from mahlkoenig import Grinder
from mahlkoenig.exceptions import (
    MahlkoenigAuthenticationError,
    MahlkoenigConnectionError,
    MahlkoenigProtocolError,
)

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

        self._last_recipe_update = datetime.min
        self._last_statistics_update = datetime.min
        self._last_wifi_info_update = datetime.min

        # Update intervals for different data types (in seconds)
        self._recipe_update_interval = timedelta(minutes=1)
        self._statistics_update_interval = timedelta(minutes=5)
        self._wifi_info_update_interval = timedelta(minutes=1)

    @property
    def grinder(self) -> Grinder:
        """Return the grinder client."""
        return self._grinder

    @property
    def available(self) -> bool:
        """Return True if the grinder is connected."""
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
                await self._grinder.connect()

                await self._grinder.request_machine_info()
                await self._grinder.request_wifi_info()
                await self._grinder.request_system_status()
                await self._grinder.request_auto_sleep_time()
                await self._grinder.request_recipe_list()
                await self._grinder.request_statistics()

                now = datetime.now()
                self._last_recipe_update = now
                self._last_statistics_update = now
                self._last_wifi_info_update = now
                self._last_auto_sleep_update = now

        except MahlkoenigAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except MahlkoenigConnectionError as err:
            raise UpdateFailed("Init: Error getting device data of Grinder") from err

    async def _async_update_data(self) -> None:
        """Fetch the latest values status from the video matrix."""

        try:
            async with asyncio.timeout(10):
                if not self._grinder.connected:
                    await self._grinder.connect()
                await self._grinder.request_machine_info()
                await self._grinder.request_system_status()
                await self._grinder.request_auto_sleep_time()

                now = datetime.now()
                if (now - self._last_recipe_update) >= self._recipe_update_interval:
                    await self._grinder.request_recipe_list()
                    self._last_recipe_update = now

                if (
                    now - self._last_statistics_update
                ) >= self._statistics_update_interval:
                    await self._grinder.request_statistics()
                    self._last_statistics_update = now

                if (
                    now - self._last_wifi_info_update
                ) >= self._wifi_info_update_interval:
                    await self._grinder.request_recipe_list()
                    self._last_wifi_info_update = now

        except MahlkoenigAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except (MahlkoenigConnectionError, asyncio.TimeoutError) as err:
            await self._grinder.close()
            raise UpdateFailed("Cannot connect to grinder") from err
        except MahlkoenigProtocolError as err:
            raise UpdateFailed("Unknown message from grinder") from err
        except Exception as err:
            _LOGGER.debug("Unknown grinder error", exc_info=True)
            await self._grinder.close()
            raise UpdateFailed("Unknown grinder error") from err

        return None
