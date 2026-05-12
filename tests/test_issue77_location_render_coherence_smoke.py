from backend.engine.render import prompt_renderer


def test_line_bank_location_does_not_append_unrelated_scene_tail() -> None:
    candidate = {
        "line_bank_location": "car wash tunnel with colored lights, wet glass and foam streaks",
        "setting_material": "warm travertine and pale stone detailing",
        "detail_accent": "framed canvases, stacked books and collected objects",
        "atmosphere_cue": "warm afternoon glow with gentle highlights",
    }

    rendered = prompt_renderer._format_setting_block(candidate)

    assert rendered == "Set in car wash tunnel with colored lights, wet glass and foam streaks"
