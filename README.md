# Home Assistant Mahlkönig X54 integration

A Home Assistant integration for the Mahlkönig X54 all-round grinder via its WebSocket API.

## Features

- Fetches machine data
  - Serial & product numbers
  - Firmware version & build number
  - Network details (Hostname / IP / MAC)
  - Disk / burr lifetime
- Shows live grinder status
  - Grind running / idle
  - Current grind timer
  - Active menu & error codes
- Reads usage statistics
  - Total shots & grind time
  - Per-recipe counters
  - Motor-on, standby & total on-time
- Controls settings
  - Change the auto-sleep time preset (3 min, 5 min, 10 min, 20 min, 30 min)

(Actual grind-start / dose control is not exposed by the X54 API and is therefore out of scope for this integration.)

## Installation

### Installation via HACS

1. Add this repository as a custom repository to HACS:

[![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kevinschweikert&repository=ha-mahlkoenig&category=Integration)

2. Use HACS to install the integration.
3. Restart Home Assistant.
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mahlkoenig)

### Manual Installation

1. Download the integration files from the GitHub repository.
2. Place the integration folder in the custom_components directory of Home Assistant.
3. Restart Home Assistant.
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mahlkoenig)

## Debugging

It is possible to show the info and debug logs for the Pi-hole V6 integration, to do this you need to enable logging in the configuration.yaml, example below:

```
logger:
  default: warning
  logs:
    # Log for mahlkoenig integation
    custom_components.mahlkoenig: debug
```

Logs do not remove sensitive information so careful what you share, check what you are about to share and blank identifying information.
