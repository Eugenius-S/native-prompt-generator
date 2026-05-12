import json
from collections import Counter
from pathlib import Path

from backend import prompt_service
from backend.prompt_service import _merged_form_state, generate_run


POSE_BANK = json.loads((Path("backend/engine/data/pose_bank.json")).read_text(encoding="utf-8"))
POSE_GROUPS = {item["id"]: item.get("group", "unknown") for item in POSE_BANK["pose_families"]}


def _random_pose_group_stats(mode: str, seed: int) -> Counter[str]:
    original_randint = prompt_service.random.randint
    prompt_service.random.randint = lambda _low, _high, chosen=seed: chosen
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

    groups = Counter(POSE_GROUPS[item["candidate"]["pose_family_id"]] for item in run["prompts"])
    assert len(run["prompts"]) == 20
    return groups


def test_random_modes_keep_seated_and_lying_poses_visible() -> None:
    seeds = (71000111, 72000222, 73000333, 74000444, 75000555)

    for mode in ("women", "men", "couples"):
        for seed in seeds:
            groups = _random_pose_group_stats(mode, seed)
            standing_like = groups["standing"] + groups["movement"]
            lowered = groups["lying"] + groups["kneeling"]
            assert standing_like >= 10
            assert groups["seated"] >= 2
            assert lowered >= 1
            assert lowered <= 5
