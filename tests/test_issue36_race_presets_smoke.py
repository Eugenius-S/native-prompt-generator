from collections import Counter

from backend.options import UI_OPTIONS
from backend.prompt_service import _merged_form_state, generate_run
from backend.forms.constants import ALLOWED_RACE_PRESETS


def _candidates(form_updates: dict):
    state = _merged_form_state({"batchSize": 20, "debugMode": "on", **form_updates})
    result = generate_run(state)
    prompts = result["prompts"]
    assert len(prompts) == 20
    assert sum(len(prompt.get("findings", [])) for prompt in prompts) == 0
    return [prompt["candidate"] for prompt in prompts], "\n".join(prompt["prompt"] for prompt in prompts)


def test_mostly_asian_routes_to_asian_candidates():
    candidates, _ = _candidates({"mode": "women", "racePreset": "mostly_asian"})
    assert Counter(candidate["ethnicity_group"] for candidate in candidates) == {"asian": 20}


def test_exact_race_preset_locks_candidate_ethnicity():
    candidates, prompt_text = _candidates({"mode": "women", "racePreset": "east_asian_japanese"})
    assert Counter(candidate["ethnicity_id"] for candidate in candidates) == {"east_asian_japanese": 20}
    assert "Japanese woman" in prompt_text


def test_mostly_mixed_uses_curated_full_pool():
    candidates, prompt_text = _candidates({"mode": "women", "racePreset": "mostly_mixed"})
    ids = {candidate["ethnicity_id"] for candidate in candidates}
    assert "middle_eastern" in ids
    assert "south_asian" in ids
    assert {"white", "black", "latina", "asian", "middle_eastern", "south_asian"} <= {
        candidate["ethnicity_group"] for candidate in candidates
    }
    assert "Arab woman" in prompt_text
    assert "Indian woman" in prompt_text


def test_european_presets_drop_redundant_white_wording():
    candidates, prompt_text = _candidates({"mode": "women", "racePreset": "white_russian"})
    assert Counter(candidate["ethnicity_id"] for candidate in candidates) == {"white_russian": 20}
    assert "Russian woman" in prompt_text
    assert "white Russian" not in prompt_text


def test_curated_exact_race_options_are_exposed_and_allowed():
    required = {
        "white_ukrainian",
        "white_russian",
        "white_polish",
        "white_italian",
        "white_spanish",
        "white_english",
        "black_american",
        "black_british",
        "black_nigerian",
        "latina_mexican",
        "latina_colombian",
        "latina_brazilian",
        "east_asian_chinese",
        "east_asian_japanese",
        "southeast_asian_thai",
        "southeast_asian_vietnamese",
        "southeast_asian_filipina",
        "middle_eastern",
        "south_asian",
    }
    female_values = {item["value"] for item in UI_OPTIONS["racePresetOptions"]}
    male_values = {item["value"] for item in UI_OPTIONS["maleRacePresetOptions"]}
    assert required <= female_values
    assert required <= male_values
    assert required <= ALLOWED_RACE_PRESETS
