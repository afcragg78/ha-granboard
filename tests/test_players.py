from __future__ import annotations

import pytest

from custom_components.granboard.players import (
    HELPER_COLORS,
    HELPER_PLAYERS,
    PlayerDirectory,
    ProfileError,
    initials_from_name,
    is_guest_name,
)


def test_initials_and_guest():
    assert initials_from_name("Andrew") == "AN"
    assert initials_from_name("Andrew Cragg") == "AC"
    assert initials_from_name("  ") == "?"
    assert is_guest_name("Guest") and is_guest_name("guest")
    assert not is_guest_name("Andrew")


def test_add_update_archive_and_resolve():
    d = PlayerDirectory()
    andrew = d.add_player("Andrew", color="red")
    assert andrew.initials == "AN" and andrew.color == "#ff0000"
    sam = d.add_player("Sam", color="#00f5ff", initials="S", avatar="/local/sam.jpg")
    assert sam.initials == "S" and sam.avatar.endswith("sam.jpg")
    with pytest.raises(ProfileError, match="already exists"):
        d.add_player("andrew")
    with pytest.raises(ProfileError, match="Guest"):
        d.add_player("Guest")
    d.update_player(andrew.id, name="Andy", color="cyan")
    assert d.get(andrew.id).name == "Andy" and d.get(andrew.id).color == "#00ffff"
    # Resolve by id, by name, and a one-night Guest.
    resolved = d.resolve_players([andrew.id, "Sam", "Guest"], ["red", "blue", "green"])
    assert resolved[0]["profile_id"] == andrew.id and resolved[0]["name"] == "Andy"
    assert resolved[1]["profile_id"] == sam.id
    assert resolved[2]["profile_id"] is None and resolved[2]["name"] == "Guest"
    d.remove_player(sam.id)
    assert d.get(sam.id).archived is True
    assert d.active_count() == 1
    with pytest.raises(ProfileError, match="removed"):
        d.resolve_players([sam.id])


def test_set_lineup_used_when_players_omitted():
    d = PlayerDirectory()
    andrew = d.add_player("Andrew", color="red")
    d.set_lineup([andrew.id, "Guest"], [None, "blue"])
    public = d.lineup_public()
    assert public[0]["player_id"] == andrew.id and public[0]["guest"] is False
    assert public[1]["name"] == "Guest" and public[1]["guest"] is True
    resolved = d.resolve_players(None)
    assert [p["name"] for p in resolved] == ["Andrew", "Guest"]
    assert resolved[1]["profile_id"] is None
    # An empty name list still starts a default player, but omitted uses the lineup.
    defaulted = d.resolve_players([])
    assert defaulted[0]["name"] == "Player 1"


def test_seed_from_helper_skips_guest():
    class State:
        def __init__(self, value):
            self.state = value

    class States:
        def __init__(self, mapping):
            self._mapping = mapping

        def get(self, entity_id):
            return self._mapping.get(entity_id)

    d = PlayerDirectory()
    states = States(
        {
            HELPER_PLAYERS: State("Andrew, Guest"),
            HELPER_COLORS: State("red, blue, green, yellow"),
        }
    )
    assert d.seed_from_states(states) is True
    assert [p.name for p in d.active()] == ["Andrew"]
    assert d.active()[0].color == "#ff0000"
    assert not d.seed_from_states(states)
    lineup = d.lineup_public()
    assert [slot["name"] for slot in lineup] == ["Andrew", "Guest"]
    assert lineup[1]["guest"] is True and lineup[1]["color"] == "#0000ff"


def test_dump_and_load_round_trip():
    d = PlayerDirectory()
    d.add_player("Andrew", color="red")
    d.set_lineup(["Andrew", "Guest"])
    loaded = PlayerDirectory.load(d.dump())
    assert loaded.active()[0].name == "Andrew"
    assert loaded.lineup_public()[1]["guest"] is True
    assert PlayerDirectory.load(None).active_count() == 0
