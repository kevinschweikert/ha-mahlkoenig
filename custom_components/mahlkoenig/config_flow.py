"""Config flow for Mahlkönig X54 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from mahlkoenig import Grinder, MahlkoenigAuthenticationError, MahlkoenigConnectionError

from .const import DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=9998): int,
    }
)


class MahlkonigConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mahlkönig X54."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._host: str | None = None
        self._port: int | None = None
        self._device_name: str | None = None
        self._serial_number: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]

            try:
                async with Grinder(
                    host=self._host,
                    port=self._port,
                    session=async_get_clientsession(self.hass),
                ) as grinder:
                    await grinder.request_machine_info()
                    self._serial_number = grinder.machine_info.serial_no

                    if self._serial_number:
                        await self.async_set_unique_id(self._serial_number)
                        self._abort_if_unique_id_configured(
                            updates={CONF_HOST: self._host, CONF_PORT: self._port}
                        )

                    return self.async_create_entry(
                        title=f"Mahlkönig X54 ({self._host})", data=user_input
                    )

            except MahlkoenigAuthenticationError as err:
                raise ConfigEntryAuthFailed from err
            except MahlkoenigConnectionError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle a discovered device."""
        self._serial_number = discovery_info.properties.get("sn")
        self._device_name = discovery_info.hostname.removesuffix(".local.")
        self._host = discovery_info.host
        self._port = discovery_info.port

        title = (
            f"Mahlkönig X54 {self._serial_number}"
            if self._serial_number
            else f"Mahlkönig X54 ({self._host})"
        )

        self.context["title_placeholders"] = {"name": title}

        # Use serial number as unique_id if available
        if self._serial_number:
            await self.async_set_unique_id(self._serial_number)
            self._abort_if_unique_id_configured(
                updates={CONF_HOST: self._host, CONF_PORT: self._port}
            )

        return await self.async_step_confirm_discovery()

    async def async_step_confirm_discovery(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle discovery confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Create configuration with discovered host and port
            data = {
                CONF_HOST: self._host,
                CONF_PORT: self._port,
            }

            try:
                async with Grinder(
                    host=self._host,
                    port=self._port,
                    session=async_get_clientsession(self.hass),
                ):
                    pass
            except MahlkoenigConnectionError:
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="confirm_discovery",
                    description_placeholders={
                        "name": self._device_name,
                        "host": self._host,
                        "port": self._port,
                    },
                    errors=errors,
                )

            title = self.context.get("title_placeholders", {}).get(
                "name", f"Mahlkönig X54 ({self._host})"
            )
            return self.async_create_entry(title=title, data=data)

        # Show a confirmation dialog to the user
        self._set_confirm_only()

        return self.async_show_form(
            step_id="confirm_discovery",
            description_placeholders={
                "name": self._device_name,
                "host": self._host,
                "port": self._port,
            },
            errors=errors,
        )
