import json

from backend import prompt_service
from backend.engine import data_loader, generator, line_bank_loader


def test_men_line_bank_prompt_parts_surface_without_leaking_into_couples(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "content_bank_config.json"
    line_bank_root = tmp_path / "line_banks"
    men_pose_dir = line_bank_root / "men" / "poses"
    men_outfit_dir = line_bank_root / "men" / "outfits"
    men_expression_dir = line_bank_root / "men" / "expressions"
    men_pose_dir.mkdir(parents=True)
    men_outfit_dir.mkdir(parents=True)
    men_expression_dir.mkdir(parents=True)
    (men_pose_dir / "4_5.md").write_text(
        "standing with one shoulder angled slightly toward camera\n",
        encoding="utf-8",
    )
    (men_outfit_dir / "4_5.md").write_text(
        "washed black tee under a soft suede jacket with relaxed charcoal trousers\n",
        encoding="utf-8",
    )
    (men_expression_dir / "4_5.md").write_text(
        "soft amused half-smile\n",
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
    monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high: 660000666)
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
    assert "standing with one shoulder angled slightly toward camera" in men_prompt["segments"]["pose"]
    assert "washed black tee under a soft suede jacket with relaxed charcoal trousers" in men_prompt["segments"]["outfit"]
    assert "soft amused half-smile" in men_prompt["segments"]["mood"]
    assert men_prompt["debugMeta"]["malePose"] == "standing with one shoulder angled slightly toward camera"
    assert men_prompt["debugMeta"]["maleOutfit"] == "washed black tee under a soft suede jacket with relaxed charcoal trousers"
    assert men_prompt["debugMeta"]["maleExpression"] == "soft amused half-smile"

    data_loader._load_static_data_bank.cache_clear()
    monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high: 770000777)
    couples_run = prompt_service.generate_run(
        {
            "formState": {
                "mode": "couples",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "random",
                "spicyLevel": "4",
                "locationStrategy": "allow_repeats",
            }
        }
    )

    couples_prompt = couples_run["prompts"][0]
    assert "standing with one shoulder angled slightly toward camera" not in couples_prompt["prompt"]
    assert "washed black tee under a soft suede jacket with relaxed charcoal trousers" not in couples_prompt["prompt"]
    assert "soft amused half-smile" not in couples_prompt["prompt"]

    data_loader._load_static_data_bank.cache_clear()
