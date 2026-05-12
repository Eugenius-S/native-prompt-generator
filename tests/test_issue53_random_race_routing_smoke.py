from collections import Counter

from backend.prompt_service import _merged_form_state, generate_run


def _run_batch(mode: str, race_preset: str, *, seed: int = 110001100, custom_race: str = "") -> list[dict]:
    state = _merged_form_state(
        {
            "mode": mode,
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "6",
            "antiRepeat": "hard",
            "racePreset": race_preset,
            "customRace": custom_race,
            "seed": str(seed),
        }
    )
    result = generate_run(state)
    prompts = result["prompts"]
    assert len(prompts) == 20
    assert sum(len(prompt.get("findings", [])) for prompt in prompts) == 0
    return [prompt["candidate"] for prompt in prompts]


def test_random_default_split_excludes_arab_and_indian_ids() -> None:
    seen_ethnicity_ids = set()
    for seed in range(6):
        candidates = _run_batch("women", "random_default_split", seed=730000000 + seed)
        seen_ethnicity_ids.update(candidate.get("ethnicity_id") for candidate in candidates)

    assert "middle_eastern" not in seen_ethnicity_ids
    assert "south_asian" not in seen_ethnicity_ids


def test_mostly_mixed_keeps_arab_and_indian_ids() -> None:
    combined_ids = Counter()
    for seed in range(8):
        candidates = _run_batch("women", "mostly_mixed", seed=740000000 + seed)
        combined_ids.update(candidate.get("ethnicity_id") for candidate in candidates)

    assert combined_ids["middle_eastern"] > 0
    assert combined_ids["south_asian"] > 0


def test_exact_arab_and_indian_presets_still_lock_ids() -> None:
    arab = _run_batch("women", "middle_eastern", seed=750000111)
    indian = _run_batch("women", "south_asian", seed=750000222)

    assert {candidate.get("ethnicity_id") for candidate in arab} == {"middle_eastern"}
    assert {candidate.get("ethnicity_id") for candidate in indian} == {"south_asian"}
