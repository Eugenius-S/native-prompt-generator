from __future__ import annotations

import json
from pathlib import Path

from backend.prompt_service import (
    HIGH_SPICY_WOMEN_OUTFIT_IDS,
    HIGH_SPICY_WOMEN_POSE_IDS,
    HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS,
    HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS,
    LOW_SPICY_UNSAFE_POSE_IDS,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_ids(path: Path, key: str) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {item["id"] for item in payload[key]}


def _load_blocked_pose_ids(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {item["id"] for item in payload["pose_families"] if item.get("block_low_spicy")}


def test_live_pose_bank_promoted_from_research_drafts() -> None:
    live_ids = _load_ids(ROOT / "backend" / "engine" / "data" / "pose_bank.json", "pose_families")
    draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "high_spicy_boudoir_pose_seed.json",
        "pose_families",
    )

    assert draft_ids <= live_ids


def test_live_outfit_bank_promoted_from_research_drafts() -> None:
    live_ids = _load_ids(ROOT / "backend" / "engine" / "data" / "styling.json", "outfit_families")
    draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "styling" / "high_spicy_boudoir_outfit_seed.json",
        "outfit_families",
    )

    assert draft_ids <= live_ids


def test_prompt_service_constants_cover_research_ids() -> None:
    pose_draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "high_spicy_boudoir_pose_seed.json",
        "pose_families",
    )
    outfit_draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "styling" / "high_spicy_boudoir_outfit_seed.json",
        "outfit_families",
    )
    blocked_pose_ids = _load_blocked_pose_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "high_spicy_boudoir_pose_seed.json"
    )
    reveal_outfit_ids = {
        item["id"]
        for item in json.loads(
            (ROOT / "backend" / "engine" / "data" / "drafts" / "styling" / "high_spicy_boudoir_outfit_seed.json").read_text(
                encoding="utf-8"
            )
        )["outfit_families"]
        if item["lane"] == "revealing"
    }
    pushing_outfit_ids = {
        item["id"]
        for item in json.loads(
            (ROOT / "backend" / "engine" / "data" / "drafts" / "styling" / "high_spicy_boudoir_outfit_seed.json").read_text(
                encoding="utf-8"
            )
        )["outfit_families"]
        if item["lane"] == "pushing_it"
    }

    assert pose_draft_ids <= HIGH_SPICY_WOMEN_POSE_IDS
    assert blocked_pose_ids <= LOW_SPICY_UNSAFE_POSE_IDS
    assert reveal_outfit_ids <= HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS
    assert pushing_outfit_ids <= HIGH_SPICY_WOMEN_PUSHING_IT_OUTFIT_IDS
    assert outfit_draft_ids <= HIGH_SPICY_WOMEN_OUTFIT_IDS
