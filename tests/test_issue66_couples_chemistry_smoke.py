from collections import Counter

from backend import prompt_service
from backend.engine import generator


def _collect_couple_stats(monkeypatch, *, spicy_level: int, seeds: tuple[int, ...]) -> tuple[Counter, int]:
    monkeypatch.setattr(prompt_service, "append_history", lambda payload: payload)
    monkeypatch.setattr(generator, "_save_memory", lambda _memory: None)

    pose_ids: Counter = Counter()
    direct_eye_contact_hits = 0

    for base_seed in seeds:
        monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high, chosen=base_seed: chosen)
        run = prompt_service.generate_run(
            {
                "formState": {
                    "mode": "couples",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "random",
                    "spicyLevel": str(spicy_level),
                    "locationStrategy": "allow_repeats",
                }
            }
        )
        for item in run["prompts"]:
            candidate = item["candidate"]
            pose_ids[candidate.get("line_bank_pose_id") or candidate.get("pose_family_id")] += 1
            if "direct eye contact" in item.get("prompt", ""):
                direct_eye_contact_hits += 1

    return pose_ids, direct_eye_contact_hits


def test_couples_mid_spicy_random_uses_broader_4_5_pose_pool(monkeypatch):
    pose_ids, _ = _collect_couple_stats(
        monkeypatch,
        spicy_level=5,
        seeds=(51000111, 52000222, 53000333, 54000444, 55000555, 56000666),
    )

    assert len(pose_ids) >= 5


def test_couples_high_spicy_random_uses_broader_6_8_pose_pool(monkeypatch):
    pose_ids, _ = _collect_couple_stats(
        monkeypatch,
        spicy_level=8,
        seeds=(81000111, 82000222, 83000333, 84000444, 85000555, 86000666),
    )

    assert len(pose_ids) >= 8


def test_couples_high_spicy_random_drops_camera_locked_mood_language(monkeypatch):
    for spicy_level in (6, 7, 8):
        _, direct_eye_contact_hits = _collect_couple_stats(
            monkeypatch,
            spicy_level=spicy_level,
            seeds=(61000111, 62000222, 63000333, 64000444, 65000555),
        )

        assert direct_eye_contact_hits == 0