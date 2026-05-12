import json

from backend import prompt_service
from backend.engine import data_loader, generator, line_bank_loader


def test_women_line_bank_prompt_parts_surface_without_leaking_into_men(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "content_bank_config.json"
    line_bank_root = tmp_path / "line_banks"
    women_pose_dir = line_bank_root / "women" / "poses"
    women_outfit_dir = line_bank_root / "women" / "outfits"
    women_expression_dir = line_bank_root / "women" / "expressions"
    women_pose_dir.mkdir(parents=True)
    women_outfit_dir.mkdir(parents=True)
    women_expression_dir.mkdir(parents=True)
    (women_pose_dir / "4_5.md").write_text(
        "leaning on the windowsill with a quiet half-turn toward camera\n",
        encoding="utf-8",
    )
    (women_outfit_dir / "4_5.md").write_text(
        "silk camisole with tailored cream trousers and minimal gold jewelry\n",
        encoding="utf-8",
    )
    (women_expression_dir / "4_5.md").write_text(
        "soft knowing half-smile\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(data_loader, "CONTENT_BANK_CONFIG_PATH", config_path)
    monkeypatch.setattr(line_bank_loader, "LINE_BANK_ROOT", line_bank_root)
    monkeypatch.setattr(prompt_service, "append_history", lambda payload: payload)
    monkeypatch.setattr(generator, "_save_memory", lambda _memory: None)
    config_path.write_text(
        json.dumps({"load_drafts": False, "load_overrides": True, "load_line_banks": True}),
        encoding="utf-8",
    )

    data_loader._load_static_data_bank.cache_clear()
    monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high: 440000444)
    women_run = prompt_service.generate_run(
        {
            "formState": {
                "mode": "women",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "random",
                "womenSceneFamily": "random",
                "spicyLevel": "4",
                "locationStrategy": "allow_repeats",
            }
        }
    )

    women_prompt = women_run["prompts"][0]
    # Portrait-safe rendering can replace lower-body/scene-dependent pose text,
    # but the selected line-bank pose must still be captured on the candidate.
    assert (
        "leaning on the windowsill with a quiet half-turn toward camera" in women_prompt["segments"]["pose"]
        or "upper-body pose with a slight torso angle" in women_prompt["segments"]["pose"]
    )
    assert women_prompt["candidate"]["line_bank_pose"] == "leaning on the windowsill with a quiet half-turn toward camera"
    assert "silk camisole" in women_prompt["segments"]["outfit"]
    assert women_prompt["candidate"]["line_bank_outfit"] == "silk camisole with tailored cream trousers and minimal gold jewelry"
    assert "soft knowing half-smile" in women_prompt["segments"]["mood"]
    assert women_prompt["candidate"]["line_bank_expression"] == "soft knowing half-smile"

    data_loader._load_static_data_bank.cache_clear()
    monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high: 550000555)
    men_run = prompt_service.generate_run(
        {
            "formState": {
                "mode": "men",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "random",
                "spicyLevel": "4",
                "locationStrategy": "allow_repeats",
            }
        }
    )

    men_prompt = men_run["prompts"][0]
    assert "leaning on the windowsill with a quiet half-turn toward camera" not in men_prompt["prompt"]
    assert "silk camisole with tailored cream trousers and minimal gold jewelry" not in men_prompt["prompt"]
    assert "soft knowing half-smile" not in men_prompt["prompt"]

    data_loader._load_static_data_bank.cache_clear()
