"""Home Assistant tests. Run: pytest tests_ha -o asyncio_mode=auto (needs pytest-homeassistant-custom-component)."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
