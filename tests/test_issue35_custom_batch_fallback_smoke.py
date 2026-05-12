from collections import Counter
import json
import random
from pathlib import Path

from backend.engine import selectors
from backend.prompt_service import _merged_form_state, generate_run


def test_custom_heavy_women_random_batch_does_not_dead_end():
    state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "6",
            "antiRepeat": "hard",
            "validationMode": "strict",
            "outfitReveal": "pushing_it",
            "beautyFinishControl": "after_dark",
            "hairstyle": "sleek_bob",
            "hairColorControl": "black",
            "eyeColorControl": "green_eyes",
            "breastSizeControl": "extra_large_breasts",
            "locationStrategy": "fresh_only",
        }
    )

    result = generate_run(state)
    prompts = result["prompts"]
    candidates = [prompt["candidate"] for prompt in prompts]

    assert len(prompts) == 20
    assert sum(len(prompt.get("findings", [])) for prompt in prompts) == 0
    assert Counter(candidate.get("hair_color_id") for candidate in candidates) == {"black_natural": 20}
    assert Counter(candidate.get("eye_color_id") for candidate in candidates) == {"green_eyes": 20}
    assert Counter(candidate.get("breast_size_id") for candidate in candidates) == {"extra_large_breasts": 20}


def test_exact_black_hair_color_can_repeat_when_it_is_the_only_valid_match():
    styling_path = Path(__file__).resolve().parents[1] / "backend" / "engine" / "data" / "styling.json"
    hair_colors = json.loads(styling_path.read_text(encoding="utf-8"))["hair_colors"]

    chosen = selectors._choose_hair_color(
        hair_colors,
        random.Random(7),
        "young_18",
        False,
        "white",
        "black_natural",
        required_ids={"black_natural"},
        preferred_ids={"black_natural"},
        allow_dyed_natural=False,
    )

    assert chosen["id"] == "black_natural"
