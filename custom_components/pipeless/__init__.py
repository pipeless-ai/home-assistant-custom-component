"""
The Pipeless Agents integration.
"""

from __future__ import annotations

import logging
import multiprocessing
import os
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

    stream_source = entry.data.get("stream_source")
    pipeless_endpoint = entry.data.get("pipeless_endpoint")

    async def on_hass_start(event):
        """Handler for Home Assistant startup."""
        # Run FFmpeg process in a separate process
        p = multiprocessing.Process(
            target=run_ffmpeg, args=(stream_source, pipeless_endpoint)
        )
        p.start()
        updated_data = dict(entry.data)  # Copy the current data to update it
        updated_data.update({"ffmpeg_pid": p.pid})
        hass.config_entries.async_update_entry(entry, data=updated_data)

    # Register event listener for Home Assistant startup
    hass.bus.async_listen_once("homeassistant_start", on_hass_start)
    # Run the process after adding a config entry
    await on_hass_start(None)

    return True


async def async_unload_entry(hass, entry):
    """Handle removal of an entry."""
    # kill the ffmpeg process that we started when the entry is removed
    try:
        pid = entry.data.get("ffmpeg_pid")
        os.kill(pid, 9)  # Send SIGKILL signal to the process
    except OSError as e:
        _LOGGER.error(f"Failed to stop ffmpeg process: {e}")
        return False

    # Return True if unloading was successful, False otherwise.
    return True


def run_ffmpeg(stream_source, remote_endpoint):
    """Run FFmpeg process to push the stream to the remote source."""
    _LOGGER.info(f"Streaming from {stream_source} to {remote_endpoint}")
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        stream_source,
        "-x264-params",
        "crf=23:ref=0:bframes=0:keyint=60:min-keyint=60:scenecut=0",  # We need to remove Bframes in order to allow webrtc reading. Also keyint params try to minimize keyframes impact
        "-fflags",
        "nobuffer",
        "-flags",
        "low_delay",
        "-c:v",
        "libx264",  # Re-encode so that the multimedia server is able to serve most protocols. VP9 could be a better alterntive for faster transmission and removing keyframes
        "-an",  # Disable audio forward
        "-f",
        "flv",
        "-filter:v",
        "fps=5",  # Decrease to 1 FPS as it is not normal to require more in home automation
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
        print(stderr.strip())
        _LOGGER.error("FFmpeg process failed with return code %d", return_code)
        _LOGGER.error("FFmpeg output: %s", stdout.strip())
        _LOGGER.error("FFmpeg error: %s", stderr.strip())
