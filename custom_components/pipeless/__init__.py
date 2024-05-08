"""
The Pipeless Agents integration.
"""

from __future__ import annotations

import logging
import multiprocessing
import subprocess

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# PLATFORMS: list[Platform] = [Platform.CAMERA]
PLATFORMS: list[Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pipeless Agents from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Forward config entries creation to the config_flow
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    stream_source = entry.data.get("stream_source")
    pipeless_endpoint = entry.data.get("pipeless_endpoint")

    async def on_hass_start(event):
        """Handler for Home Assistant startup."""
        # Run FFmpeg process in a separate process
        multiprocessing.Process(
            target=run_ffmpeg, args=(stream_source, pipeless_endpoint)
        ).start()

    # Register event listener for Home Assistant startup
    hass.bus.async_listen_once("homeassistant_start", on_hass_start)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def run_ffmpeg(stream_source, remote_endpoint):
    """Run FFmpeg process to push the stream to the remote source."""
    _LOGGER.info(f"Streaming from {stream_source} to {remote_endpoint}")
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        stream_source,
        "-c:v",
        "copy",
        "-f",
        "mpegts",
        remote_endpoint,
    ]

    # Launch FFmpeg process
    process = subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    # Wait for FFmpeg process to complete
    stdout, stderr = process.communicate()

    # Check if FFmpeg process failed
    return_code = process.returncode
    if return_code != 0:
        _LOGGER.error("FFmpeg process failed with return code %d", return_code)
        _LOGGER.error("FFmpeg output: %s", stdout.strip())
        _LOGGER.error("FFmpeg error: %s", stderr.strip())
