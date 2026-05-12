import json
from collections import Counter
from pathlib import Path

from backend import prompt_service
from backend.services import batch_selection
from backend.prompt_service import _merged_form_state, generate_run

MEMORY_PATH = Path("backend/engine/runtime/memory.json")


def _cheap_flat_light_candidate(candidate: dict) -> bool:
    scene_family_id = candidate.get("scene_family_id")
    treatment_id = candidate.get("photo_treatment_id")
    lighting_id = candidate.get("lighting_family_id")
    if scene_family_id not in {"residential_luxury", "hospitality_suite", "culture_bookish", "garden_conservatory"}:
        return False
    if treatment_id == "casual_indoor_selfie" and lighting_id in {"clean_daylight", "soft_overcast", "warm_interior"}:
        return True
    if treatment_id == "clean_commercial" and lighting_id in {"soft_overcast", "warm_interior"}:
        return True
    return False


def _collect_random_quality_stats(mode: str, seeds: tuple[int, ...]) -> Counter[str]:
    stats = Counter()
    original_memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))

    try:
        for seed in seeds:
            MEMORY_PATH.write_text(json.dumps(original_memory, ensure_ascii=False, indent=2), encoding="utf-8")
            original_randint = prompt_service.random.randint
            original_batch_selection_randint = batch_selection.random.randint
            prompt_service.random.randint = lambda _low, _high, chosen=seed: chosen
            batch_selection.random.randint = lambda _low, _high, chosen=seed: chosen
            try:
                state = _merged_form_state(
                    {
                        "mode": mode,
                        "batchSize": 20,
                        "debugMode": "on",
                        "styleMode": "random",
                        "spicyLevel": "random",
                        "antiRepeat": "hard",
                    }
                )
                run = generate_run(state)
            finally:
                prompt_service.random.randint = original_randint
                batch_selection.random.randint = original_batch_selection_randint

            for prompt in run["prompts"]:
                candidate = prompt["candidate"]
                if candidate.get("scene_family_id") in {
                    "residential_luxury",
                    "hospitality_suite",
                    "culture_bookish",
                    "creative_gallery",
                    "grooming_bath",
                    "wellness_spa",
                }:
                    stats["interior"] += 1
                if candidate.get("lighting_family_id") in {"soft_overcast", "warm_interior", "practical_lamp", "moody_darkness"} or candidate.get("photo_treatment_id") in {
                    "analog_35mm",
                    "documentary_still",
                    "casual_indoor_selfie",
                    "mirror_selfie",
                }:
                    stats["muted"] += 1
                if _cheap_flat_light_candidate(candidate):
                    stats["cheap_light"] += 1
                stats["total"] += 1
    finally:
        MEMORY_PATH.write_text(json.dumps(original_memory, ensure_ascii=False, indent=2), encoding="utf-8")

    return stats


def test_random_mode_limits_interior_muted_and_cheap_light_overload() -> None:
    seeds = (71000111, 72000222, 73000333, 74000444, 75000555)

    for mode in ("women", "men", "couples"):
        stats = _collect_random_quality_stats(mode, seeds)
        assert stats["total"] == len(seeds) * 20
        assert stats["interior"] <= 40
        assert stats["cheap_light"] <= 6
