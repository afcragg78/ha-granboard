from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from custom_components.granboard.alexa_audio import (
    ALEXA_CACHE_DIR,
    alexa_ssml,
    cache_key,
    cache_path,
    convert_clip,
    ffmpeg_command,
    local_www_path,
    prepare_all_clips,
    prepare_cached_clip,
    public_cache_url,
    use_alexa_audio,
)
from custom_components.granboard.sounds import list_theme_names, theme_options


def test_use_alexa_audio_auto_on_for_alexa_media():
    assert use_alexa_audio("alexa_media", False) is True
    assert use_alexa_audio("alexa_media", True) is True
    assert use_alexa_audio("music_assistant", False) is False
    assert use_alexa_audio("music_assistant", True) is True
    assert use_alexa_audio(None, False) is False


def test_ssml_and_public_url():
    assert alexa_ssml("https://ex.ui.nabu.casa/local/a.mp3") == "<audio src='https://ex.ui.nabu.casa/local/a.mp3'/>"
    assert "O'Brien" not in alexa_ssml("https://ex/'O'Brien.mp3")
    assert public_cache_url("https://ex.ui.nabu.casa", "abc.mp3") == (
        "https://ex.ui.nabu.casa/local/granboard/sounds/.alexa_cache/abc.mp3"
    )


def test_cache_key_changes_with_mtime(tmp_path: Path):
    src = tmp_path / "a.mp3"
    src.write_bytes(b"x")
    m1 = 1_000_000_000
    k1 = cache_key(str(src.resolve()), m1)
    k2 = cache_key(str(src.resolve()), m1 + 1)
    assert k1 != k2
    assert cache_key(str(src.resolve()), m1) == k1
    assert cache_path(tmp_path, str(src.resolve()), m1).name.endswith(".mp3")
    assert cache_path(tmp_path, str(src.resolve()), m1).parent.name == ALEXA_CACHE_DIR


def test_theme_scan_skips_alexa_cache(tmp_path: Path):
    (tmp_path / "funny").mkdir()
    (tmp_path / ALEXA_CACHE_DIR).mkdir()
    (tmp_path / ".alexa_cache" / "x.mp3").write_bytes(b"x")
    assert list_theme_names(tmp_path) == ["funny"]
    assert ALEXA_CACHE_DIR not in theme_options(tmp_path)


def test_local_www_path(tmp_path: Path):
    clip = tmp_path / "granboard" / "sounds" / "funny" / "hit" / "a.mp3"
    clip.parent.mkdir(parents=True)
    clip.write_bytes(b"x")
    found = local_www_path(tmp_path, "/local/granboard/sounds/funny/hit/a.mp3")
    assert found == clip.resolve()
    found = local_www_path(tmp_path, "https://ex.ui.nabu.casa/local/granboard/sounds/funny/hit/a.mp3")
    assert found == clip.resolve()
    assert local_www_path(tmp_path, "/local/../secrets") is None or (
        local_www_path(tmp_path, "/local/../secrets") is not None
        and ".." not in "/local/../secrets".split("/local/", 1)[1]  # guarded
    )
    # traversal is rejected
    assert local_www_path(tmp_path, "/local/../etc/passwd") is None


def test_ffmpeg_command_shape():
    dest = Path("/tmp/out.mp3")
    cmd = ffmpeg_command("ffmpeg", "/tmp/in.wav", dest)
    assert cmd[0] == "ffmpeg" and "-y" in cmd and "-i" in cmd
    assert cmd[cmd.index("-b:a") + 1] == "48k"
    assert cmd[cmd.index("-ar") + 1] == "24000"
    assert cmd[cmd.index("-ac") + 1] == "1"
    assert cmd[cmd.index("-t") + 1] == "240"
    assert cmd[-1] == str(dest)


def test_convert_and_cache_with_real_ffmpeg(tmp_path: Path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return
    src = tmp_path / "in.wav"
    gen = [
        ffmpeg, "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.25",
        "-ar", "44100", "-ac", "2", str(src),
    ]
    assert subprocess.run(gen, capture_output=True, check=False).returncode == 0
    sounds_root = tmp_path / "sounds"
    dest = prepare_cached_clip(ffmpeg, src, sounds_root)
    assert dest is not None and dest.is_file() and dest.stat().st_size > 0
    # second call hits the cache (same path)
    again = prepare_cached_clip(ffmpeg, src, sounds_root)
    assert again == dest
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,sample_rate,channels",
         "-show_entries", "format=bit_rate", "-of", "default=noprint_wrappers=1", str(dest)],
        capture_output=True, text=True, check=False,
    )
    out = probe.stdout
    assert "codec_name=mp3" in out
    assert "sample_rate=24000" in out
    assert "channels=1" in out
    # bitrate around 48k (ffmpeg may report 48000)
    if "bit_rate=" in out:
        rate = int([line.split("=")[1] for line in out.splitlines() if line.startswith("bit_rate=")][0])
        assert 40000 <= rate <= 56000


def test_convert_failure_returns_none(tmp_path: Path):
    missing = tmp_path / "no-such-binary"
    src = tmp_path / "in.mp3"
    src.write_bytes(b"not audio")
    dest = tmp_path / "out.mp3"
    assert convert_clip(str(missing), src, dest) is False



def test_prepare_all_clips_skips_cache_and_converts_theme_files(tmp_path: Path, monkeypatch):
    from custom_components.granboard.alexa_audio import ALEXA_CACHE_DIR, iter_sound_files

    theme = tmp_path / "funny" / "hit"
    theme.mkdir(parents=True)
    clip = theme / "a.mp3"
    clip.write_bytes(b"clip")
    cache = tmp_path / ALEXA_CACHE_DIR
    cache.mkdir()
    (cache / "cached.mp3").write_bytes(b"cached")
    (tmp_path / "notes.txt").write_text("nope")
    files = iter_sound_files(tmp_path)
    assert files == [clip]

    converted: list[str] = []

    def fake_prepare(binary, src, sounds_root):
        converted.append(str(src))
        dest = sounds_root / ALEXA_CACHE_DIR / "out.mp3"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"ok")
        return dest

    import custom_components.granboard.alexa_audio as alexa_audio

    monkeypatch.setattr(alexa_audio, "prepare_cached_clip", fake_prepare)
    prepared = prepare_all_clips("ffmpeg", tmp_path)
    assert len(prepared) == 1
    assert prepared[0][0] == clip.resolve()
    assert converted == [str(clip)]
