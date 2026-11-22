from __future__ import annotations

from custom_components.granboard.protocol import parse_segment
from custom_components.granboard.sounds import SOUND_KEYS, pick_sound, volume_level

ALL = {k: f"/local/granboard/sounds/{k}.mp3" for k in SOUND_KEYS}


def hit(seg):
    return parse_segment(seg).as_dict()


def test_specific_hit_sounds():
    assert pick_sound(ALL, hit("S5")) == "single"
    assert pick_sound(ALL, hit("D5")) == "double"
    assert pick_sound(ALL, hit("T5")) == "triple"
    assert pick_sound(ALL, hit("T20")) == "triple_20"
    assert pick_sound(ALL, hit("SB")) == "outer_bull"
    assert pick_sound(ALL, hit("DB")) == "inner_bull"


def test_fallbacks_and_empty():
    assert pick_sound({"hit": "/x.mp3"}, hit("T20")) == "hit"
    assert pick_sound({"triple": "/x.mp3"}, hit("T20")) == "triple"
    assert pick_sound({}, hit("T20")) is None
    assert pick_sound({"single": "  "}, hit("S1")) is None


def test_awards_beat_hits_by_priority():
    awards = [{"type": "ton"}, {"type": "ton_80"}]
    assert pick_sound(ALL, hit("T20"), awards) == "ton_80"
    assert pick_sound(ALL, hit("D20"), [{"type": "checkout"}, {"type": "winner"}]) == "winner"
    assert pick_sound({"checkout": "/c.mp3", "single": "/s.mp3"}, hit("D20"), [{"type": "checkout"}, {"type": "winner"}]) == "checkout"
    assert pick_sound(ALL, hit("S1"), [{"type": "bust"}]) == "bust"
    # bullseye award uses the bull hit sounds
    assert pick_sound(ALL, hit("DB"), [{"type": "bullseye", "score": 50}]) == "inner_bull"


def test_events():
    assert pick_sound(ALL, event="next_player") == "next_player"
    assert pick_sound(ALL, event="game_start") == "game_start"


def test_volume_is_capped_at_60_percent():
    assert volume_level(None) is None and volume_level("") is None and volume_level(-1) is None
    assert volume_level(40) == 0.4
    assert volume_level(100) == 0.6


from pathlib import Path
import random

from custom_components.granboard.sounds import (
    DEFAULT_THEME,
    THEME_OFF,
    clip_url,
    list_clips,
    list_theme_names,
    pick_sound_clip,
    theme_options,
)


def _clip(root: Path, theme: str, key: str, name: str) -> Path:
    folder = root / theme / key
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_bytes(b"x")
    return path


def test_list_themes_and_options(tmp_path: Path):
    (tmp_path / "funny").mkdir()
    (tmp_path / "Default Pack").mkdir()
    (tmp_path / ".hidden").mkdir()
    (tmp_path / "Off").mkdir()
    (tmp_path / "readme.txt").write_text("nope")
    assert list_theme_names(tmp_path) == ["Default Pack", "funny"]
    assert list_theme_names(tmp_path / "missing") == []
    assert theme_options(tmp_path) == [THEME_OFF, "Default Pack", "funny"]
    assert theme_options(tmp_path, "retired") == [THEME_OFF, "Default Pack", "funny", "retired"]


def test_list_clips_filters_extensions(tmp_path: Path):
    _clip(tmp_path, "funny", "ton_80", "a.mp3")
    _clip(tmp_path, "funny", "ton_80", "b.wav")
    _clip(tmp_path, "funny", "ton_80", "c.ogg")
    _clip(tmp_path, "funny", "ton_80", "skip.txt")
    _clip(tmp_path, "funny", "ton_80", ".hidden.mp3")
    names = [path.name for path in list_clips(tmp_path, "funny", "ton_80")]
    assert names == ["a.mp3", "b.wav", "c.ogg"]
    assert list_clips(tmp_path, "funny", "hit") == []
    assert list_clips(tmp_path, "../funny", "ton_80") == []


def test_theme_clip_beats_default_and_configured(tmp_path: Path):
    _clip(tmp_path, "funny", "triple_20", "theme.mp3")
    _clip(tmp_path, "default", "triple_20", "default.mp3")
    sounds = {"triple_20": "/local/granboard/sounds/manual.mp3", "hit": "/h.mp3"}
    picked = pick_sound_clip(tmp_path, "funny", sounds, hit=hit("T20"), rng=random.Random(0))
    assert picked == ("triple_20", clip_url("funny", "triple_20", "theme.mp3"), "funny")


def test_falls_back_default_then_configured_then_key_chain(tmp_path: Path):
    sounds = {"triple_20": "/t20.mp3", "triple": "/t.mp3", "hit": "/h.mp3"}
    # empty funny/triple_20 -> default/triple_20
    _clip(tmp_path, "default", "triple_20", "d.mp3")
    picked = pick_sound_clip(tmp_path, "funny", sounds, hit=hit("T20"))
    assert picked == ("triple_20", clip_url("default", "triple_20", "d.mp3"), "default")

    # no folders for T20 -> configured triple_20
    empty = tmp_path / "empty"
    empty.mkdir()
    picked = pick_sound_clip(empty, "funny", sounds, hit=hit("T20"))
    assert picked == ("triple_20", "/t20.mp3", None)

    # no T20 anywhere -> key fallback uses funny/triple
    other = tmp_path / "other"
    _clip(other, "funny", "triple", "t.mp3")
    picked = pick_sound_clip(other, "funny", {"hit": "/h.mp3"}, hit=hit("T20"))
    assert picked == ("triple", clip_url("funny", "triple", "t.mp3"), "funny")

    # Off ignores folders and uses Configure + key chain
    picked = pick_sound_clip(tmp_path, THEME_OFF, {"hit": "/h.mp3"}, hit=hit("T20"))
    assert picked == ("hit", "/h.mp3", None)
    assert pick_sound_clip(tmp_path, THEME_OFF, {}, hit=hit("T20")) is None


def test_awards_and_events_use_same_priority(tmp_path: Path):
    _clip(tmp_path, "funny", "ton", "ton.mp3")
    _clip(tmp_path, "funny", "ton_80", "180.mp3")
    _clip(tmp_path, "funny", "triple_20", "t20.mp3")
    picked = pick_sound_clip(
        tmp_path, "funny", {}, hit=hit("T20"), awards=[{"type": "ton"}, {"type": "ton_80"}]
    )
    assert picked[0] == "ton_80" and picked[2] == "funny"
    picked = pick_sound_clip(tmp_path, "funny", {}, event="game_start")
    assert picked is None
    _clip(tmp_path, "default", "game_start", "go.ogg")
    picked = pick_sound_clip(tmp_path, "funny", {}, event="game_start")
    assert picked == ("game_start", clip_url("default", "game_start", "go.ogg"), "default")


def test_random_choice_stays_in_folder(tmp_path: Path):
    names = [f"clip{i}.mp3" for i in range(5)]
    for name in names:
        _clip(tmp_path, "funny", "hit", name)
    rng = random.Random(1)
    seen = {pick_sound_clip(tmp_path, "funny", {}, hit=hit("S1"), rng=rng)[1] for _ in range(30)}
    expected = {clip_url("funny", "hit", name) for name in names}
    assert seen <= expected
    assert len(seen) > 1
