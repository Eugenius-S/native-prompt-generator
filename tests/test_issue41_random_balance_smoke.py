from collections import Counter

from backend.engine import candidate_builder
from backend.prompt_service import _merged_form_state, generate_run


def _random_run_stats(mode: str) -> tuple[Counter[str], int, int]:
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
    result = generate_run(state)
    prompts = result["prompts"]
    assert len(prompts) == 20
    candidates = [prompt["candidate"] for prompt in prompts]
    scene_groups = Counter()
    for candidate in candidates:
        group = candidate_builder._random_scene_group(candidate)
        scene_groups[group] += 1
        if group in {"urban_outdoor", "water", "nature", "outdoor"}:
            scene_groups["outdoor"] += 1
    bright_count = sum(1 for candidate in candidates if candidate_builder._is_random_bright_candidate(candidate))
    findings_count = sum(len(prompt.get("findings", [])) for prompt in prompts)
    return scene_groups, bright_count, findings_count


def test_random_modes_keep_scene_and_light_balance():
    for mode in ("women", "men", "couples"):
        scene_groups, bright_count, findings_count = _random_run_stats(mode)
        assert findings_count == 0
        assert scene_groups["outdoor"] > scene_groups["indoor"]
        assert scene_groups["outdoor"] >= 12
        assert scene_groups["indoor"] <= 8
        assert scene_groups["water"] >= 3
        assert scene_groups["nature"] >= 3
        assert bright_count >= 13
