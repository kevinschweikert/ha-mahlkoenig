# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Coordinator now calls `request_wifi_info()` for wifi updates (was incorrectly calling `request_recipe_list()`).
- Auto sleep time is now polled at most once per minute instead of on every coordinator tick.
- Authentication failures during initial config flow setup now surface as an `invalid_auth` form error instead of raising `ConfigEntryAuthFailed`, which would crash setup.
- Recipe-based sensors no longer raise `KeyError` when a recipe disappears from the device; they return `None` instead.
- Typo: `"Diplay controller failed"` → `"Display controller failed"`.

### Changed

- The grinder connection is now closed when the config entry is unloaded.
- Sensor entity descriptions use Home Assistant's built-in `entity_registry_enabled_default` field instead of a custom `enabled` attribute.

### Removed

- Stale "Video Matrix" copy-paste docstrings across `sensor.py`, `select.py`, `binary_sensor.py`, and `coordinator.py`.
- Redundant availability check in `async_setup_entry` (unreachable, since `_async_setup` already raises `ConfigEntryNotReady` on failure).
- No-op `@dataclass` decorator on `MahlkonigEntity`.
