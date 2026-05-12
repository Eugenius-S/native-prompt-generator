from collections import Counter

from backend.services import postprocess


def _color_story_bank():
    return [
        {"id": "clean_neutrals", "value": "clean neutral palette"},
        {"id": "powder_blue", "value": "powder blue story"},
        {"id": "hot_pink", "value": "hot pink accent story"},
        {"id": "navy_cream", "value": "navy and cream palette"},
        {"id": "earthy_soft", "value": "earthy soft palette"},
        {"id": "slate_blue_ink", "value": "slate blue and ink palette"},
        {"id": "chocolate_cream", "value": "chocolate and cream palette"},
        {"id": "black_gold", "value": "black and gold evening palette"},
        {"id": "oxblood_noir", "value": "oxblood and noir palette"},
        {"id": "emerald_noir", "value": "emerald and noir palette"},
        {"id": "champagne_taupe", "value": "champagne taupe palette"},
        {"id": "rosewood_smoke", "value": "rosewood and smoke palette"},
        {"id": "winter_neutrals", "value": "winter neutral palette"},
        {"id": "soft_camel_cream", "value": "soft camel and cream palette"},
        {"id": "dusty_rose_taupe", "value": "dusty rose and taupe palette"},
    ]


def test_random_women_color_diversifier_widens_palette_and_promotes_pattern(monkeypatch):
    monkeypatch.setattr(postprocess.generator, "load_data_bank", lambda: {"styling": {"color_stories": _color_story_bank()}})
    monkeypatch.setattr(postprocess.generator, "render_candidate_segments", lambda candidate: {"color": candidate["color_story_id"]})
    monkeypatch.setattr(postprocess.generator, "render_candidate_prompt", lambda candidate: candidate["color_story_id"])

    prompts = []
    for idx in range(10):
        candidate = {
            "outfit_family_id": "column_dress",
            "outfit_family": "column dress",
            "material_id": f"mat_{idx % 2}",
            "color_story_id": "clean_neutrals",
            "color_story": "clean neutral palette",
        }
        prompts.append({"candidate": candidate, "segments": {}, "prompt": ""})

    diversified = postprocess._diversify_women_outfit_colors(
        prompts,
        {"mode": "women", "antiRepeat": "hard", "styleMode": "random"},
        spicy_level=6,
    )

    color_counts = Counter(item["candidate"]["color_story_id"] for item in diversified)
    assert len(color_counts) >= 8
    assert color_counts["clean_neutrals"] <= 2
    assert any(item["candidate"].get("outfit_render_mode_override") == "pattern" for item in diversified)


def test_random_couples_color_diversifier_widens_palette(monkeypatch):
    monkeypatch.setattr(postprocess.generator, "load_data_bank", lambda: {"styling": {"color_stories": _color_story_bank()}})

    scaffolds = []
    for idx in range(10):
        candidate = {
            "outfit_family_id": "wrap_blouse_skirt",
            "outfit_family": "wrap blouse with skirt",
            "material_id": f"mat_{idx % 2}",
            "color_story_id": "clean_neutrals",
            "color_story": "clean neutral palette",
        }
        scaffolds.append({"candidate": candidate})

    diversified = postprocess._diversify_couples_candidate_colors(
        scaffolds,
        {"mode": "couples", "antiRepeat": "hard", "styleMode": "random"},
        spicy_level=6,
    )

    color_counts = Counter(item["candidate"]["color_story_id"] for item in diversified)
    assert len(color_counts) >= 8
    assert color_counts["clean_neutrals"] <= 2
    assert any(item["candidate"].get("outfit_render_mode_override") == "pattern" for item in diversified)
