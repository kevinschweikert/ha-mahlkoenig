# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-25

### Added

- This CHANGELOG
- New `Connected` binary sensor (diagnostic) exposing the live WebSocket connection state to the grinder
- Translation for errors and fields

### Changed

- The integration now treats the grinder being offline as the normal state. Cached sensor values (statistics, recipe data, configuration) remain available with their last-known value while the grinder sleeps; they no longer flap to "unavailable" between coffees. `Grinder running` and `Active Menu` are still unavailable while the grinder is disconnected.
- Setup no longer fails when the grinder is offline at Home Assistant startup, provided the device has connected at least once before. Device serial number, software version, and product number are persisted to the config entry on the first successful connect so entities can be re-created across reboots without a live connection. (Fixes #1)
- Connection errors during polling are now logged at debug level only — no more warnings every cycle while the grinder sleeps.
- Zeroconf-discovered grinders are now probed with an empty password first; the password prompt only appears if the grinder actually rejects the connection.
- Recipe sensors are now always created for slots 1–4 regardless of whether the grinder responded during setup.
- The grinder connection is now closed when the config entry is unloaded.
- Sensor entity descriptions use Home Assistant's built-in `entity_registry_enabled_default` field instead of a custom `enabled` attribute.

### Fixed

- Coordinator now calls `request_wifi_info()` for wifi updates (was incorrectly calling `request_recipe_list()`).
- Auto sleep time is now polled at most once per minute instead of on every coordinator tick.
- Authentication failures during initial config flow setup now surface as an `invalid_auth` form error instead of raising `ConfigEntryAuthFailed`, which would crash setup.
- Recipe-based sensors no longer raise `KeyError` when a recipe disappears from the device; they return `None` instead.
- Typo: `"Diplay controller failed"` → `"Display controller failed"`.

### Removed

- Stale copy-paste docstrings across `sensor.py`, `select.py`, `binary_sensor.py`, and `coordinator.py`.
- Redundant availability check in `async_setup_entry` (unreachable, since `_async_setup` already raises `ConfigEntryNotReady` on failure).
- No-op `@dataclass` decorator on `MahlkonigEntity`.
