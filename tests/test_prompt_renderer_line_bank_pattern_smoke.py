from backend.engine.render import prompt_renderer


def test_line_bank_outfit_respects_pattern_override():
    phrase = prompt_renderer.render_outfit_phrase_from_parts(
        outfit_family_id="bodycon_dress",
        outfit_family="bodycon dress",
        color_story_id="powder_blue",
        color_story="powder blue story",
        material="",
        scene_family_id="garden_conservatory",
        seed_parts=("seed",),
        render_mode_override="pattern",
    )

    assert "pattern" in phrase or "print" in phrase or "stripe" in phrase or "jacquard" in phrase or "check" in phrase
