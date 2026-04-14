from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def sample_ipos_records() -> dict[str, list[dict[str, str]]]:
    return json.loads((ROOT / "data/samples/ipos.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def sample_opportunities_records() -> dict[str, list[dict[str, str]]]:
    return json.loads((ROOT / "data/samples/opportunities.json").read_text(encoding="utf-8"))
