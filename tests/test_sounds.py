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
