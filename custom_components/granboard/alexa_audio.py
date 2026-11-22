"""Convert clips so Amazon Echo / Alexa Media Player can play them.

Alexa will not play a normal media_player.play_media stream ("Direct music
streaming isn't supported"). Short clips work as SSML <audio> through
notify.alexa_media (type: tts) if the file is a public HTTPS MP3 at 48 kbps
and 16000 / 22050 / 24000 Hz, no longer than 240 seconds.

The converted files are cached under /config/www/granboard/sounds/.alexa_cache/
(a hidden folder, skipped by Sound Theme discovery).
"""

from __future__ import annotations

import hashlib
import logging
import subprocess
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

ALEXA_CACHE_DIR = ".alexa_cache"
ALEXA_MAX_SECONDS = 240
ALEXA_BITRATE = "48k"
ALEXA_RATE = "24000"
ALEXA_PLATFORM = "alexa_media"
FFMPEG_TIMEOUT_S = 30

# ffmpeg: mono MP3, 48 kbps, 24 kHz, trim to 240 s (Alexa SSML <audio> limits).
FFMPEG_ARGS = (
    "-t",
    str(ALEXA_MAX_SECONDS),
    "-vn",
    "-ac",
    "1",
    "-codec:a",
    "libmp3lame",
    "-b:a",
    ALEXA_BITRATE,
    "-ar",
    ALEXA_RATE,
)


def alexa_ssml(url: str) -> str:
    """SSML audio tag. The URL is quoted with single quotes."""
    safe = url.replace("'", "%27")
    return "<audio src='" + safe + "'/>"


def cache_key(source: str, mtime_ns: int | None) -> str:
    payload = f"{source}|{mtime_ns or 0}"
    return hashlib.sha256(payload.encode()).hexdigest()[:24]


def cache_dir(sounds_root: Path) -> Path:
    return sounds_root / ALEXA_CACHE_DIR


def cache_path(sounds_root: Path, source: str, mtime_ns: int | None) -> Path:
    return cache_dir(sounds_root) / f"{cache_key(source, mtime_ns)}.mp3"


def ffmpeg_command(binary: str, src: str, dest: Path) -> list[str]:
    return [binary, "-y", "-i", src, *FFMPEG_ARGS, str(dest)]


def convert_clip(binary: str, src: str | Path, dest: Path) -> bool:
    """Run ffmpeg into dest. Returns True if a non-empty MP3 was written."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ffmpeg_command(binary, str(src), dest)
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=FFMPEG_TIMEOUT_S, check=False)
    except (OSError, subprocess.TimeoutExpired) as err:
        _LOGGER.warning("Granboard Alexa ffmpeg failed to start: %s", err)
        return False
    if result.returncode != 0 or not dest.is_file() or dest.stat().st_size == 0:
        err = (result.stderr or b"").decode("utf-8", "replace")[-500:]
        _LOGGER.warning("Granboard Alexa ffmpeg failed (%s): %s", result.returncode, err)
        if dest.exists() and dest.stat().st_size == 0:
            dest.unlink(missing_ok=True)
        return False
    return True


def prepare_cached_clip(binary: str, src: str | Path, sounds_root: Path) -> Path | None:
    """Return a cached Alexa-format MP3, converting when the source is new or changed."""
    source = str(src)
    path = Path(source)
    mtime_ns = None
    if path.is_file():
        mtime_ns = path.stat().st_mtime_ns
        source = str(path.resolve())
    dest = cache_path(sounds_root, source, mtime_ns)
    if dest.is_file() and dest.stat().st_size > 0:
        if mtime_ns is None or not path.is_file() or dest.stat().st_mtime_ns >= mtime_ns:
            return dest
    if convert_clip(binary, src, dest):
        return dest
    return None


def public_cache_url(base_url: str, filename: str) -> str:
    base = base_url.rstrip("/")
    return f"{base}/local/granboard/sounds/{ALEXA_CACHE_DIR}/{filename}"


def local_www_path(www_root: Path, url: str) -> Path | None:
    """Map /local/... or a full URL ending in /local/... to a file under www."""
    marker = "/local/"
    if marker not in url:
        return None
    rel = url.split(marker, 1)[1].split("?", 1)[0]
    if not rel or ".." in rel.split("/"):
        return None
    path = (www_root / rel).resolve()
    try:
        path.relative_to(www_root.resolve())
    except ValueError:
        return None
    return path


def use_alexa_audio(platform: str | None, option: bool) -> bool:
    """Alexa Media Player always uses the converted path; the option forces it for others."""
    if (platform or "") == ALEXA_PLATFORM:
        return True
    return bool(option)
