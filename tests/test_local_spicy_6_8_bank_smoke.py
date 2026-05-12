from __future__ import annotations

import json
from pathlib import Path

from backend.legacy_people import _couple_interaction_bank, _male_styling_bank
from backend.prompt_service import (
    HIGH_SPICY_WOMEN_OUTFIT_IDS,
    HIGH_SPICY_WOMEN_POSE_IDS,
    HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS,
    LOW_SPICY_UNSAFE_POSE_IDS,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_payload(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_ids(path: Path, key: str) -> set[str]:
    return {item["id"] for item in _load_payload(path)[key]}


def test_local_spicy_live_pose_bank_promoted() -> None:
    live_ids = _load_ids(ROOT / "backend" / "engine" / "data" / "pose_bank.json", "pose_families")
    draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "spicy_6_8_local_women_pose_seed.json",
        "pose_families",
    )

    assert draft_ids <= live_ids


def test_local_spicy_live_outfit_bank_promoted() -> None:
    live_ids = _load_ids(ROOT / "backend" / "engine" / "data" / "styling.json", "outfit_families")
    draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "styling" / "spicy_6_8_local_women_outfit_seed.json",
        "outfit_families",
    )

    assert draft_ids <= live_ids


def test_local_spicy_couple_interactions_promoted_and_runtime_visible() -> None:
    live_ids = _load_ids(ROOT / "backend" / "engine" / "data" / "pose_bank.json", "couple_interactions")
    draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "spicy_6_8_local_couples_interaction_seed.json",
        "couple_interactions",
    )
    runtime_ids = {item["id"] for item in _couple_interaction_bank()}

    assert draft_ids <= live_ids
    assert draft_ids <= runtime_ids


def test_local_spicy_constants_cover_promoted_women_ids() -> None:
    pose_payload = _load_payload(
        ROOT / "backend" / "engine" / "data" / "drafts" / "pose_bank" / "spicy_6_8_local_women_pose_seed.json"
    )
    outfit_payload = _load_payload(
        ROOT / "backend" / "engine" / "data" / "drafts" / "styling" / "spicy_6_8_local_women_outfit_seed.json"
    )

    pose_ids = {item["id"] for item in pose_payload["pose_families"]}
    blocked_pose_ids = {item["id"] for item in pose_payload["pose_families"] if item.get("block_low_spicy")}
    reveal_outfit_ids = {item["id"] for item in outfit_payload["outfit_families"] if item.get("lane") == "revealing"}

    assert pose_ids <= HIGH_SPICY_WOMEN_POSE_IDS
    assert blocked_pose_ids <= LOW_SPICY_UNSAFE_POSE_IDS
    assert reveal_outfit_ids <= HIGH_SPICY_WOMEN_REVEALING_OUTFIT_IDS
    assert reveal_outfit_ids <= HIGH_SPICY_WOMEN_OUTFIT_IDS


def test_local_spicy_male_outfits_reach_runtime_styling_bank() -> None:
    draft_ids = _load_ids(
        ROOT / "backend" / "engine" / "data" / "drafts" / "styling" / "spicy_6_8_local_couples_outfit_seed.json",
        "outfit_families",
    )
    runtime_ids = {item["id"] for item in _male_styling_bank()["outfit_families"]}

    assert draft_ids <= runtime_ids
