from backend.prompt_service import _merged_form_state
from backend.services import batch_selection


def test_best_batch_reuses_selected_batch_instead_of_regenerating(monkeypatch) -> None:
    form_state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 4,
            "debugMode": "on",
            "styleMode": "random",
            "photoTypeControl": "balanced",
            "antiRepeat": "hard",
        }
    )

    fixed_batch = [
        {
            "setting_macro_id": "macro_a",
            "scene_family_id": "urban_daylight",
            "setting_micro_id": "micro_a",
            "setting_scene_id": "scene_a",
            "outfit_family_id": "outfit_a",
            "pose_family_id": "pose_a",
            "camera_framing_id": "frame_a",
            "camera_angle_id": "angle_a",
        }
        for _ in range(form_state["batchSize"])
    ]
    calls = {"generate": 0, "persist": 0}

    def fake_generate_batch(*args, **kwargs):
        calls["generate"] += 1
        return list(fixed_batch)

    def fake_persist_batch_memory(batch):
        calls["persist"] += 1
        assert batch == fixed_batch

    monkeypatch.setattr(batch_selection.form_user_profile, "_user_style_profile", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(batch_selection.generator, "generate_batch", fake_generate_batch)
    monkeypatch.setattr(batch_selection.generator, "persist_batch_memory", fake_persist_batch_memory)
    monkeypatch.setattr(batch_selection, "validate_candidate", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(batch_selection.scoring, "_batch_score", lambda *_args, **_kwargs: (999, False))
    monkeypatch.setattr(batch_selection.random, "randint", lambda *_args, **_kwargs: 12345678)

    batch, findings, seed = batch_selection._best_batch(
        form_state,
        spicy_level=6,
        use_recent_batch_rules=True,
        use_memory_rules=True,
    )

    assert batch == fixed_batch
    assert findings == {index: [] for index in range(form_state["batchSize"])}
    assert seed == 12345678
    assert calls["generate"] == 1
    assert calls["persist"] == 1
