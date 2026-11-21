"""Import the pure modules without loading Home Assistant."""

from __future__ import annotations

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "granboard"

if "custom_components.granboard" not in sys.modules:
    parent = sys.modules.get("custom_components")
    if parent is None:
        parent = types.ModuleType("custom_components")
        parent.__path__ = [str(ROOT / "custom_components")]  # type: ignore[attr-defined]
        sys.modules["custom_components"] = parent
    package = types.ModuleType("custom_components.granboard")
    package.__path__ = [str(INTEGRATION)]  # type: ignore[attr-defined]
    package.__package__ = "custom_components.granboard"
    sys.modules["custom_components.granboard"] = package
