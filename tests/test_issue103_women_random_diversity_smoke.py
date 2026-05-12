from collections import Counter

from backend.prompt_service import _merged_form_state, generate_run
from backend.services import scoring


FITTED_LANE_OUTFITS = {"mini_dress", "blazer_mini_dress", "bodysuit_trousers"}
ISSUE103_DOMINANT_COLORS = {
    "clean_neutrals",
    "navy_cream",
    "powder_blue",
    "earthy_soft",
    "chocolate_cream",
    "champagne_taupe",
    "hot_pink",
    "oxblood_noir",
    "rosewood_smoke",
}


def _run_random_women_stats(seed: int) -> tuple[Counter[str], Counter[str], int]:
    state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "4",
            "antiRepeat": "hard",
            "seed": str(seed),
        }
    )
    result = generate_run(state)
    prompts = result["prompts"]
    colors = Counter(prompt["candidate"].get("color_story_id") for prompt in prompts if prompt.get("candidate"))
    outfits = Counter(prompt["candidate"].get("outfit_family_id") for prompt in prompts if prompt.get("candidate"))
    findings = sum(len(prompt.get("findings", [])) for prompt in prompts)
    return colors, outfits, findings


def test_women_random_diversity_score_prefers_broader_non_fitted_mix() -> None:
    varied_batch = [
        {"outfit_family_id": "cardigan_skirt", "color_story_id": "soft_camel_cream"},
        {"outfit_family_id": "shirt_trousers", "color_story_id": "slate_blue_ink"},
        {"outfit_family_id": "vest_trousers", "color_story_id": "emerald_noir"},
        {"outfit_family_id": "wrap_blouse_skirt", "color_story_id": "dusty_rose_taupe"},
        {"outfit_family_id": "structured_day_dress", "color_story_id": "oxblood_noir"},
        {"outfit_family_id": "apron_workshop_trousers", "color_story_id": "winter_neutrals"},
    ]
    rigid_batch = [
        {"outfit_family_id": "mini_dress", "color_story_id": "powder_blue"},
        {"outfit_family_id": "mini_dress", "color_story_id": "powder_blue"},
        {"outfit_family_id": "blazer_mini_dress", "color_story_id": "navy_cream"},
        {"outfit_family_id": "bodysuit_trousers", "color_story_id": "clean_neutrals"},
        {"outfit_family_id": "mini_dress", "color_story_id": "hot_pink"},
        {"outfit_family_id": "blazer_mini_dress", "color_story_id": "chocolate_cream"},
    ]

    assert scoring._women_random_outfit_color_diversity_score(varied_batch) > scoring._women_random_outfit_color_diversity_score(rigid_batch)


def test_women_random_diversity_score_dislikes_repeating_one_exact_color_story() -> None:
    repeated_batch = [
        {"outfit_family_id": "halter_trousers", "color_story_id": "powder_blue"},
        {"outfit_family_id": "vest_trousers", "color_story_id": "powder_blue"},
        {"outfit_family_id": "wrap_blouse_skirt", "color_story_id": "powder_blue"},
        {"outfit_family_id": "structured_day_dress", "color_story_id": "powder_blue"},
        {"outfit_family_id": "shirt_trousers", "color_story_id": "teal_cream"},
        {"outfit_family_id": "cardigan_skirt", "color_story_id": "olive_sand"},
    ]
    spread_batch = [
        {"outfit_family_id": "halter_trousers", "color_story_id": "powder_blue"},
        {"outfit_family_id": "vest_trousers", "color_story_id": "teal_cream"},
        {"outfit_family_id": "wrap_blouse_skirt", "color_story_id": "olive_sand"},
        {"outfit_family_id": "structured_day_dress", "color_story_id": "coral_ivory"},
        {"outfit_family_id": "shirt_trousers", "color_story_id": "plum_blush"},
        {"outfit_family_id": "cardigan_skirt", "color_story_id": "butter_denim"},
    ]

    assert scoring._women_random_outfit_color_diversity_score(spread_batch) > scoring._women_random_outfit_color_diversity_score(repeated_batch)


def test_women_random_diversity_score_prefers_broader_silhouette_mix() -> None:
    varied_batch = [
        {"outfit_family_id": "halter_trousers", "color_story_id": "soft_camel_cream"},
        {"outfit_family_id": "vest_trousers", "color_story_id": "slate_blue_ink"},
        {"outfit_family_id": "wrap_blouse_skirt", "color_story_id": "emerald_noir"},
        {"outfit_family_id": "structured_day_dress", "color_story_id": "dusty_rose_taupe"},
        {"outfit_family_id": "sweater_jeans", "color_story_id": "oxblood_noir"},
        {"outfit_family_id": "workout_top_leggings", "color_story_id": "winter_neutrals"},
    ]
    rigid_batch = [
        {"outfit_family_id": "mini_dress", "color_story_id": "powder_blue"},
        {"outfit_family_id": "mini_dress", "color_story_id": "powder_blue"},
        {"outfit_family_id": "blazer_mini_dress", "color_story_id": "navy_cream"},
        {"outfit_family_id": "crop_top_mini_skirt", "color_story_id": "clean_neutrals"},
        {"outfit_family_id": "mini_dress", "color_story_id": "hot_pink"},
        {"outfit_family_id": "bodysuit_trousers", "color_story_id": "chocolate_cream"},
    ]

    assert scoring._women_random_outfit_color_diversity_score(varied_batch) > scoring._women_random_outfit_color_diversity_score(rigid_batch)


def test_random_women_batches_keep_fitted_and_issue_palette_lanes_in_check() -> None:
    aggregate_colors = Counter()
    aggregate_outfits = Counter()
    findings_total = 0

    for seed in range(8):
        colors, outfits, findings = _run_random_women_stats(seed)
        aggregate_colors.update(colors)
        aggregate_outfits.update(outfits)
        findings_total += findings

    total = sum(aggregate_outfits.values())
    fitted_total = sum(aggregate_outfits[outfit_id] for outfit_id in FITTED_LANE_OUTFITS)
    dominant_color_total = sum(aggregate_colors[color_id] for color_id in ISSUE103_DOMINANT_COLORS)

    assert findings_total == 0
    assert aggregate_outfits["mini_dress"] / total <= 0.14
    assert fitted_total / total <= 0.28
    assert dominant_color_total / total <= 0.42
    assert len([outfit_id for outfit_id, count in aggregate_outfits.items() if count >= 6]) >= 8
