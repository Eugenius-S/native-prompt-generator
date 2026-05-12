from collections import Counter

from backend.engine import generator
from backend.engine import candidate_builder
from backend.forms import runtime_controls, user_profile as form_user_profile
from backend.prompt_service import _merged_form_state


def _aggregate_random_light_stats(mode: str, seeds: tuple[int, ...]) -> tuple[Counter[str], int, int]:
    state = _merged_form_state(
        {
            "mode": mode,
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "6",
            "antiRepeat": "hard",
        }
    )
    spicy_level = runtime_controls._effective_spicy_level(state)
    profile = form_user_profile._user_style_profile(state, spicy_level)
    scene_groups = Counter()
    bright_count = 0
    prompt_count = 0
    for seed in seeds:
        candidates = generator.generate_batch(
            20,
            seed=seed,
            identity_lock=False,
            persist_memory=False,
            use_recent_batch_rules=True,
            use_memory_rules=True,
            style_mode="random",
            user_profile=profile,
            mode=mode,
            spicy_level=spicy_level,
        )
        prompt_count += len(candidates)
        for candidate in candidates:
            group = candidate_builder._random_scene_group(candidate)
            scene_groups[group] += 1
            if group in {"urban_outdoor", "water", "nature", "outdoor"}:
                scene_groups["outdoor"] += 1
            bright_count += 1 if candidate_builder._is_random_bright_candidate(candidate) else 0
    return scene_groups, bright_count, prompt_count


def test_random_modes_favor_outdoors_and_sunlight() -> None:
    seeds = (71000111, 72000222, 73000333, 74000444, 75000555)

    for mode in ("women", "men", "couples"):
        scene_groups, bright_count, prompt_count = _aggregate_random_light_stats(mode, seeds)
        assert prompt_count == len(seeds) * 20
        assert scene_groups["outdoor"] >= 60
        assert scene_groups["water"] >= 15
        assert scene_groups["nature"] >= 15
        assert scene_groups["water"] + scene_groups["nature"] >= 35
        assert bright_count >= 65
