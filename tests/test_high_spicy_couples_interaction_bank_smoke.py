from __future__ import annotations

import json
from pathlib import Path

from backend.legacy_people import _couple_interaction_bank


ROOT = Path(__file__).resolve().parents[1]


def _load_records(path: Path, key: str) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return list(payload[key])


def test_live_couple_interaction_bank_promoted_from_research_drafts() -> None:
    live_ids = {
        item["id"] for item in _load_records(ROOT / "backend" / "engine" / "data" / "pose_bank.json", "couple_interactions")
    }
    draft_ids = {
        item["id"]
        for item in _load_records(
            ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "high_spicy_couples_interaction_seed.json",
            "couple_interactions",
        )
    }

    assert len(draft_ids) >= 16
    assert draft_ids <= live_ids


def test_runtime_couple_interaction_bank_contains_promoted_ids() -> None:
    runtime_ids = {item["id"] for item in _couple_interaction_bank()}
    draft_ids = {
        item["id"]
        for item in _load_records(
            ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "high_spicy_couples_interaction_seed.json",
            "couple_interactions",
        )
    }

    assert draft_ids <= runtime_ids


def test_runtime_couple_interaction_bank_preserves_low_spicy_block_flags() -> None:
    draft_blocked = {
        item["id"]
        for item in _load_records(
            ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "high_spicy_couples_interaction_seed.json",
            "couple_interactions",
        )
        if item.get("block_low_spicy")
    }
    runtime_blocked = {item["id"] for item in _couple_interaction_bank() if item.get("block_low_spicy")}

    assert draft_blocked <= runtime_blocked
