"""Constants."""

from homeassistant.const import Platform

DOMAIN = "mahlkoenig"  # has to be the same as parent directory name and match the name in manifest.json
PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
]  # delegates to each <PLATFORM>.py
