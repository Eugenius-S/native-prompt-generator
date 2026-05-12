from collections import Counter

from backend import legacy_people
from backend.engine import generator
from backend.engine.render import prompt_renderer


def test_women_outfit_render_avoids_raw_palette_prefix_on_layered_piece() -> None:
    phrase = generator.render_outfit_phrase_from_parts(
        outfit_family_id="thigh_high_bodysuit_robe",
        outfit_family="opaque bodysuit styled with a robe layer and thigh-high hosiery for a polished boudoir-editorial look",
        color_story_id="rosewood_smoke",
        color_story="rosewood and smoke palette",
        material="matte jersey finish",
        scene_family_id="hospitality_suite",
        seed_parts=("layered-check",),
    )

    assert "rosewood and smoke palette opaque bodysuit" not in phrase
    assert "palette opaque bodysuit" not in phrase
    assert phrase.startswith("an opaque bodysuit")


def test_dual_color_full_palette_render_stays_rare_for_separates() -> None:
    total = 1000
    dual_count = 0

    for seed in range(total):
        phrase = generator.render_outfit_phrase_from_parts(
            outfit_family_id="bodysuit_trousers",
            outfit_family="sleek square neck bodysuit with high waisted tailored trousers",
            color_story_id="rosewood_smoke",
            color_story="rosewood and smoke palette",
            material="tailored woven fabric",
            scene_family_id="hospitality_suite",
            seed_parts=(seed,),
        )
        if "using a rosewood and smoke palette" in phrase:
            dual_count += 1

    ratio = dual_count / total
    assert 0.06 <= ratio <= 0.13


def test_separates_render_still_surfaces_split_and_pattern_variants() -> None:
    counts = Counter()

    for seed in range(300):
        phrase = generator.render_outfit_phrase_from_parts(
            outfit_family_id="bodysuit_trousers",
            outfit_family="sleek square neck bodysuit with high waisted tailored trousers",
            color_story_id="rosewood_smoke",
            color_story="rosewood and smoke palette",
            material="tailored woven fabric",
            scene_family_id="hospitality_suite",
            seed_parts=(seed,),
        )
        if "with rosewood on the top and smoke on the trousers" in phrase:
            counts["split"] += 1
        if any(token in phrase for token in ("pattern", "print", "stripe", "jacquard")):
            counts["pattern"] += 1

    assert counts["split"] > 0
    assert counts["pattern"] > 0


def test_close_neutral_separates_prefer_split_over_single_render() -> None:
    counts = Counter()

    for seed in range(400):
        phrase = generator.render_outfit_phrase_from_parts(
            outfit_family_id="cami_midi_skirt",
            outfit_family="silk cami with a bias cut midi skirt",
            color_story_id="champagne_taupe",
            color_story="champagne and taupe palette",
            material="soft satin finish",
            scene_family_id="hospitality_suite",
            seed_parts=(seed,),
        )
        if "with champagne on the top and taupe on the skirt" in phrase:
            counts["split"] += 1
        elif "using a champagne and taupe palette" in phrase:
            counts["dual"] += 1
        elif any(token in phrase for token in ("pattern", "print", "stripe", "jacquard")):
            counts["pattern"] += 1
        else:
            counts["single"] += 1

    assert counts["split"] > counts["single"]
    assert counts["pattern"] > 0


def test_legacy_couple_and_male_helpers_use_naturalized_clothing_render() -> None:
    female_phrase = legacy_people._couple_female_outfit_text(
        {
            "outfit_family_id": "thigh_high_bodysuit_robe",
            "scene_family_id": "hospitality_suite",
            "color_story_id": "rosewood_smoke",
            "color_story": "rosewood and smoke palette",
            "material": "matte jersey finish",
            "outfit_family": "opaque bodysuit styled with a robe layer and thigh-high hosiery for a polished boudoir-editorial look",
            "setting_scene_id": "suite_demo",
        },
        "random",
    )
    male_phrase = generator.render_male_outfit_phrase(
        "",
        "washed tee under a relaxed blazer with tailored trousers",
        scene_family_id="creative_gallery",
        seed_parts=("male-demo",),
    )

    assert "palette opaque bodysuit" not in female_phrase
    assert female_phrase.startswith("an opaque bodysuit")
    assert "clean washed tee" not in male_phrase
    assert "washed tee under a relaxed blazer with tailored trousers" in male_phrase


def test_women_line_bank_outfit_gets_color_story_clause() -> None:
    block = prompt_renderer._format_outfit_block(
        {
            "line_bank_outfit": "silk cami with a bias cut midi skirt",
            "line_bank_outfit_id": "line_outfits_demo",
            "outfit_family_id": "cami_midi_skirt",
            "color_story_id": "hot_pink",
            "color_story": "hot pink accent story",
            "scene_family_id": "hospitality_suite",
            "setting_scene_id": "suite_demo",
            "setting_micro_id": "mirror_zone",
            "photo_treatment_id": "mirror_selfie",
            "time_of_day_id": "afternoon",
        }
    )

    assert block.startswith("Wearing a silk cami with a bias cut midi skirt")
    assert "hot pink" in block
    assert any(token in block for token in ("rendered in", "with hot pink on", "hot pink palette"))


def test_women_line_bank_outfit_close_neutrals_prefer_split_render() -> None:
    counts = Counter()

    for seed in range(300):
        block = prompt_renderer._format_outfit_block(
            {
                "line_bank_outfit": "silk cami with a bias cut midi skirt",
                "line_bank_outfit_id": f"line_outfits_demo_{seed}",
                "outfit_family_id": "cami_midi_skirt",
                "color_story_id": "champagne_taupe",
                "color_story": "champagne and taupe palette",
                "scene_family_id": "hospitality_suite",
                "setting_scene_id": "suite_demo",
                "setting_micro_id": f"mirror_zone_{seed}",
                "photo_treatment_id": "mirror_selfie",
                "time_of_day_id": "afternoon",
            }
        )
        if "with champagne on the top and taupe on the skirt" in block:
            counts["split"] += 1
        elif any(token in block for token in ("pattern", "print", "stripe", "jacquard")):
            counts["pattern"] += 1
        elif "using a champagne and taupe palette" in block:
            counts["dual"] += 1
        else:
            counts["single"] += 1

    assert counts["split"] > counts["single"]
