from __future__ import annotations

from collections import Counter
from functools import lru_cache

from backend.prompt_service import _merged_form_state, generate_run


@lru_cache(maxsize=None)
def _framing_counts(control: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for seed in range(12):
        form = _merged_form_state(
            {
                "mode": "women",
                "batchSize": 8,
                "styleMode": "random",
                "poseFramingControl": control,
                "seed": str(seed),
                "debugMode": "on",
                "antiRepeat": "hard",
                "validationMode": "strict",
            }
        )
        run = generate_run(form)
        for item in run["prompts"]:
            counts[item["candidate"]["camera_framing_id"]] += 1
    return counts


def test_issue107_random_no_longer_emits_face_only_portraits() -> None:
    counts = _framing_counts("random")
    assert counts["face_only"] == 0


def test_issue107_more_portraits_stays_chest_up_not_face_only() -> None:
    counts = _framing_counts("more_portraits")
    assert counts["face_only"] == 0
    assert counts["head_and_shoulders"] >= 1
    assert counts["below_chest_portrait"] >= 1
