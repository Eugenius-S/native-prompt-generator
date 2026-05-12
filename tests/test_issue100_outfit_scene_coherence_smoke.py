from __future__ import annotations

import json
from pathlib import Path

from backend.engine import line_bank_loader, selectors


DATA_ROOT = Path(__file__).resolve().parents[1] / "backend" / "engine" / "data"
STYLING = json.loads((DATA_ROOT / "styling.json").read_text(encoding="utf-8"))
SETTING_ENGINE = json.loads((DATA_ROOT / "setting_engine.json").read_text(encoding="utf-8"))
OUTFITS = {item["id"]: item for item in STYLING["outfit_families"]}
BASE_SPACES = {item["id"]: item for item in SETTING_ENGINE["base_spaces"]}


def _matches(outfit_id: str, base_space_id: str, style_mode: str = "random") -> bool:
    predicate = selectors._base_space_outfit_predicate(OUTFITS[outfit_id], style_mode)
    return predicate(BASE_SPACES[base_space_id])


def test_issue100_blocks_wellness_and_public_elegant_mismatches() -> None:
    assert not _matches("shirt_trousers", "boutique_pilates_studio")
    assert not _matches("club_cami_wrap_skirt", "hybrid_hotel_lobby_lounge")
    assert not _matches("club_cami_wrap_skirt", "airport_lounge_evening")


def test_issue100_keeps_valid_scene_outfit_pairs() -> None:
    assert _matches("workout_top_leggings", "boutique_pilates_studio")
    assert _matches("blouse_trousers", "hotel_suite_sitting_area")
    assert _matches("club_cami_wrap_skirt", "cocktail_bar_booth", style_mode="nightlife")


def test_issue100_blocks_tailored_bodysuit_looks_in_pool_context() -> None:
    assert not _matches("blazer_bodysuit_set", "poolside_steps")


def test_issue100_blocks_shirt_trousers_in_sporty_training_scene() -> None:
    assert not _matches("shirt_trousers", "training_loft_window_bay")


def test_issue100_blocks_dressy_nightlife_outfit_in_lab_like_setting() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "satin wrap mini dress with bare shoulders",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_outfit_matches_scene(
        record,
        scene_family_id="urban_daylight",
        style_mode="random",
        scene_tags={"interior", "urban", "daylight"},
        setting_value="underground laboratory with metal tables, green light and cold floor mist",
    )


def test_issue100_blocks_lingerie_like_beach_outfit_without_swimwear() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "bralette with tiny denim shorts",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_outfit_matches_scene(
        record,
        scene_family_id="coastal_boardwalk",
        style_mode="random",
        scene_tags={"outdoor", "coastal", "beach", "daylight"},
        setting_value="pebbled beach curve with clear water and pale stones",
    )


def test_issue100_blocks_blazer_bodysuit_aquarium_mismatch() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "tailored blazer over an opaque bodysuit",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_outfit_matches_scene(
        record,
        scene_family_id="nightlife_neon",
        style_mode="random",
        scene_tags={"interior", "public_elegant", "night"},
        setting_value="aquarium tunnel with curved blue glass, water shimmer and soft marine glow",
    )


def test_issue100_blocks_club_bodysuit_in_private_dining_room() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "club bodysuit",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_outfit_matches_scene(
        record,
        scene_family_id="hospitality_suite",
        style_mode="random",
        scene_tags={"interior", "dining", "private"},
        setting_value="private dining room with white linen, tall window and evening candle glow",
    )


def test_issue100_blocks_lounge_shorts_on_fire_stair_landing() -> None:
    record = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "satin camisole with tiny lounge shorts",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_outfit_matches_scene(
        record,
        scene_family_id="urban_daylight",
        style_mode="random",
        scene_tags={"interior", "urban"},
        setting_value="apartment fire stair landing with metal steps, brick wall and soft cloudy light",
    )
