from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "custom_components" / "granboard" / "manifest.json").read_text())


def test_manifest_basics():
    assert MANIFEST["domain"] == "granboard"
    assert MANIFEST["version"] == "0.6.0"
    assert MANIFEST["config_flow"] is True
    assert "bluetooth" in MANIFEST["dependencies"]


def test_bluetooth_matchers_are_safe():
    # Core rejects a local_name matcher with * or [ in the first three characters.
    for matcher in MANIFEST["bluetooth"]:
        name = matcher.get("local_name")
        if name:
            assert not any(c in name[:3] for c in "*[")
    uuids = {m.get("service_uuid") for m in MANIFEST["bluetooth"]}
    assert "442f1570-8a00-9a28-cbe1-e1d4212d53eb" in uuids


def test_translations_match():
    base = ROOT / "custom_components" / "granboard"
    assert json.loads((base / "strings.json").read_text()) == json.loads((base / "translations" / "en.json").read_text())
