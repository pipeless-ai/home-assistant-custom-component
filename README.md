# Pipeless Agents for Home Assistant

This integration allows you to add computer vision in an easy way to your cameras to perform actions in real-time.

It integrates using webhooks with Home Assistant in order to invoke actions.

## Requirements

To use this integration you must have FFmpeg installed in your system.

TODO: use a container instead

## Installation

Easiest install is via [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=blakeblackshear&repository=home-assistant-custom-component&category=integration)

`HACS -> Integrations -> Explore & Add Repositories -> Pipeless Agents`

### Advanced

For manual installation for advanced users, copy `custom_components/pipeless` to
your `custom_components` folder in Home Assistant.

Please visit the [main Pipeless Agents documentation](https://docs-agents.pipeless.ai/) for full installation instructions of this integration.

## Known Issues

- [ ] Adding more than one camera per user fails. This is probably due to how the FFmpeg process is created. If some Home Assistant expert knows a better way of running it please let us know.
- [ ] Sometimes adding a config entry results in a config entry duplication.
