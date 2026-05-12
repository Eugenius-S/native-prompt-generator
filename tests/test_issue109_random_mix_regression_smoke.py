from collections import Counter

from backend.prompt_service import _merged_form_state, generate_run
from backend.services import batch_penalties, scoring


def _run_random_women(seed: int, batch_size: int = 20):
    state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": batch_size,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "random",
            "antiRepeat": "hard",
            "seed": str(seed),
        }
    )
    return generate_run(state)["prompts"]


def test_scene_family_clone_penalty_dislikes_conservatory_lock_in() -> None:
    repeated = [{"scene_family_id": "garden_conservatory"} for _ in range(6)] + [
        {"scene_family_id": "urban_daylight"},
        {"scene_family_id": "coastal_pool"},
    ]
    mixed = [
        {"scene_family_id": "garden_conservatory"},
        {"scene_family_id": "urban_daylight"},
        {"scene_family_id": "coastal_pool"},
        {"scene_family_id": "coastal_boardwalk"},
        {"scene_family_id": "nightlife_bar"},
        {"scene_family_id": "residential_luxury"},
        {"scene_family_id": "courtyard_garden"},
        {"scene_family_id": "creative_gallery"},
    ]

    assert batch_penalties._scene_family_clone_penalty(mixed, "random", "women") > batch_penalties._scene_family_clone_penalty(repeated, "random", "women")


def test_women_random_diversity_score_dislikes_dark_color_cluster() -> None:
    clustered = [
        {"outfit_family_id": "halter_trousers", "color_story_id": "slate_blue_ink"},
        {"outfit_family_id": "vest_trousers", "color_story_id": "navy_cream"},
        {"outfit_family_id": "wrap_blouse_skirt", "color_story_id": "oxblood_noir"},
        {"outfit_family_id": "structured_day_dress", "color_story_id": "emerald_noir"},
        {"outfit_family_id": "shirt_trousers", "color_story_id": "chocolate_cream"},
        {"outfit_family_id": "cardigan_skirt", "color_story_id": "earthy_soft"},
    ]
    spread = [
        {"outfit_family_id": "halter_trousers", "color_story_id": "slate_blue_ink"},
        {"outfit_family_id": "vest_trousers", "color_story_id": "dusty_rose_taupe"},
        {"outfit_family_id": "wrap_blouse_skirt", "color_story_id": "hot_pink"},
        {"outfit_family_id": "structured_day_dress", "color_story_id": "clean_neutrals"},
        {"outfit_family_id": "shirt_trousers", "color_story_id": "powder_blue"},
        {"outfit_family_id": "cardigan_skirt", "color_story_id": "soft_camel_cream"},
    ]

    assert scoring._women_random_outfit_color_diversity_score(spread) > scoring._women_random_outfit_color_diversity_score(clustered)


def test_random_women_batch_keeps_conservatory_and_dark_cluster_below_dominance() -> None:
    scene_counts = Counter()
    color_counts = Counter()
    duplicate_color_stories = 0
    for seed in (12001, 12002, 12003, 12004):
        prompts = _run_random_women(seed)
        scene_counts.update(prompt["candidate"].get("scene_family_id") for prompt in prompts if prompt.get("candidate"))
        batch_colors = [prompt["candidate"].get("color_story_id") for prompt in prompts if prompt.get("candidate")]
        color_counts.update(batch_colors)
        duplicate_color_stories += sum(count - 1 for count in Counter(batch_colors).values() if count > 1)

    total = sum(scene_counts.values())
    assert scene_counts["garden_conservatory"] <= 9
    dark_cluster_total = sum(color_counts[color_id] for color_id in ("slate_blue_ink", "navy_cream", "oxblood_noir", "emerald_noir", "chocolate_cream", "earthy_soft"))
    assert dark_cluster_total / total <= 0.38
    assert duplicate_color_stories <= 12
