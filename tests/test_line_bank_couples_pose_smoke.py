import json

from backend import prompt_service
from backend.engine import data_loader, generator, line_bank_loader


def test_couples_line_bank_pose_surfaces_without_leaking_into_women(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "content_bank_config.json"
    line_bank_root = tmp_path / "line_banks"
    couples_pose_dir = line_bank_root / "couples" / "poses"
    couples_pose_dir.mkdir(parents=True)
    couples_line = "standing close with linked hands and a soft shared smile"
    (couples_pose_dir / "4_5.md").write_text(
        f"{couples_line}\n",
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
    monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high: 881000881)
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
    assert couples_prompt["candidate"]["line_bank_pose"] == couples_line
    assert couples_line in couples_prompt["segments"]["pose"]
    assert couples_prompt["debugMeta"]["coupleLineBankPose"] == couples_line

    data_loader._load_static_data_bank.cache_clear()
    monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high: 882000882)
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
    assert couples_line not in women_prompt["prompt"]

    data_loader._load_static_data_bank.cache_clear()
