"""Update coordinator for Mahlkönig X54."""

import asyncio
import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from mahlkoenig import Grinder
from mahlkoenig.exceptions import (
    MahlkoenigAuthenticationError,
    MahlkoenigConnectionError,
    MahlkoenigProtocolError,
)

_LOGGER = logging.getLogger(__name__)

CONF_SERIAL_NO = "serial_no"
CONF_SW_VERSION = "sw_version"
CONF_PRODUCT_NO = "product_no"

type MahlkonigConfigEntry = ConfigEntry["MahlkonigUpdateCoordinator"]


class MahlkonigUpdateCoordinator(DataUpdateCoordinator[None]):
    """Coordinator to fetch all relevant data from the grinder."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: MahlkonigConfigEntry,
        host: str,
        port: int,
        password: str,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=self.__class__.__name__,
            update_interval=timedelta(seconds=10),
        )
        session = async_get_clientsession(hass)

        self._entry = entry
        self._grinder = Grinder(host=host, port=port, password=password, session=session)

        self._last_recipe_update = datetime.min
        self._last_statistics_update = datetime.min
        self._last_wifi_info_update = datetime.min
        self._last_auto_sleep_update = datetime.min

        self._recipe_update_interval = timedelta(minutes=1)
        self._statistics_update_interval = timedelta(minutes=5)
        self._wifi_info_update_interval = timedelta(minutes=1)
        self._auto_sleep_update_interval = timedelta(minutes=1)

    @property
    def grinder(self) -> Grinder:
        """Return the grinder client."""
        return self._grinder

    @property
    def available(self) -> bool:
        """Return True if the grinder is currently connected."""
        return self._grinder.connected

    @property
    def serial_no(self) -> str | None:
        """Serial number — live machine_info preferred, fallback to entry.data."""
        info = self._grinder.machine_info
        if info is not None:
            return info.serial_no
        return self._entry.data.get(CONF_SERIAL_NO)

    @property
    def sw_version(self) -> str | None:
        """Software version — live machine_info preferred, fallback to entry.data."""
        info = self._grinder.machine_info
        if info is not None:
            return info.sw_version
        return self._entry.data.get(CONF_SW_VERSION)

    @property
    def product_no(self) -> str | None:
        """Product number — live machine_info preferred, fallback to entry.data."""
        info = self._grinder.machine_info
        if info is not None:
            return info.product_no
        return self._entry.data.get(CONF_PRODUCT_NO)

    @property
    def has_device_info(self) -> bool:
        """Return True if we have at least a serial number for entity setup."""
        return self.serial_no is not None

    def _persist_machine_info(self) -> None:
        """Mirror live machine_info into entry.data so it survives reboots."""
        info = self._grinder.machine_info
        if info is None:
            return
        new_data = {
            **self._entry.data,
            CONF_SERIAL_NO: info.serial_no,
            CONF_SW_VERSION: info.sw_version,
            CONF_PRODUCT_NO: info.product_no,
        }
        if new_data != dict(self._entry.data):
            self.hass.config_entries.async_update_entry(self._entry, data=new_data)

    async def _async_setup(self):
        """Set up the coordinator.

        Tries to populate cached state by talking to the grinder. If the grinder
        is offline and we already have device metadata in entry.data from a
        previous successful connect, we let setup succeed and rely on the
        background poll loop to reconnect later.
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

                self._persist_machine_info()

                now = datetime.now()
                self._last_recipe_update = now
                self._last_statistics_update = now
                self._last_wifi_info_update = now
                self._last_auto_sleep_update = now

        except MahlkoenigAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except (MahlkoenigConnectionError, asyncio.TimeoutError) as err:
            await self._grinder.close()
            if self.has_device_info:
                _LOGGER.debug(
                    "Grinder offline at setup; entities will use cached data: %s",
                    err,
                )
                return
            raise ConfigEntryNotReady("Cannot connect to grinder") from err

    async def _async_update_data(self) -> None:
        """Fetch the latest data from the grinder.

        Connection failures are expected (the grinder sleeps when not in use)
        and are handled silently — the coordinator stays in a successful state
        and entities keep their last value.
        """
        try:
            async with asyncio.timeout(10):
                if not self._grinder.connected:
                    await self._grinder.connect()
                await self._grinder.request_machine_info()
                await self._grinder.request_system_status()

                self._persist_machine_info()

                now = datetime.now()
                if (
                    now - self._last_auto_sleep_update
                ) >= self._auto_sleep_update_interval:
                    _LOGGER.debug("fetching auto sleep time")
                    await self._grinder.request_auto_sleep_time()
                    self._last_auto_sleep_update = now

                if (now - self._last_recipe_update) >= self._recipe_update_interval:
                    _LOGGER.debug("fetching recipe_updates")
                    await self._grinder.request_recipe_list()
                    self._last_recipe_update = now

                if (
                    now - self._last_statistics_update
                ) >= self._statistics_update_interval:
                    _LOGGER.debug("fetching statistics")
                    await self._grinder.request_statistics()
                    self._last_statistics_update = now

                if (
                    now - self._last_wifi_info_update
                ) >= self._wifi_info_update_interval:
                    _LOGGER.debug("fetching wifi settings")
                    await self._grinder.request_wifi_info()
                    self._last_wifi_info_update = now

        except MahlkoenigAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except (MahlkoenigConnectionError, asyncio.TimeoutError) as err:
            # Expected — grinder is asleep. Keep last-known state, no warnings.
            _LOGGER.debug("Grinder unreachable: %s", err)
            await self._grinder.close()
        except MahlkoenigProtocolError as err:
            raise UpdateFailed("Unknown message from grinder") from err
        except Exception as err:
            _LOGGER.debug("Unknown grinder error", exc_info=True)
            await self._grinder.close()
            raise UpdateFailed("Unknown grinder error") from err

        return None
