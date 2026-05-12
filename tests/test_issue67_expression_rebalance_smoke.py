from collections import Counter

from backend import prompt_service
from backend.engine import generator


def _collect_mood_counts(monkeypatch, *, mode: str, spicy_level: int, seeds: tuple[int, ...]) -> Counter:
    monkeypatch.setattr(prompt_service, "append_history", lambda payload: payload)
    monkeypatch.setattr(generator, "_save_memory", lambda _memory: None)

    counts: Counter = Counter()
    for base_seed in seeds:
        monkeypatch.setattr(prompt_service.random, "randint", lambda _low, _high, chosen=base_seed: chosen)
        run = prompt_service.generate_run(
            {
                "formState": {
                    "mode": mode,
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "random",
                    "womenSceneFamily": "random",
                    "spicyLevel": str(spicy_level),
                    "locationStrategy": "allow_repeats",
                }
            }
        )
        for item in run["prompts"]:
            counts[item["candidate"]["mood_energy_id"]] += 1
    return counts


def test_women_high_spicy_random_bans_calm_confident(monkeypatch):
    seeds = (61001101, 62002202, 63003303, 64004404, 65005505)

    for spicy_level in (6, 7, 8):
        counts = _collect_mood_counts(monkeypatch, mode="women", spicy_level=spicy_level, seeds=seeds)
        assert counts["calm_confident"] == 0


def test_couples_high_spicy_random_bans_calm_confident(monkeypatch):
    seeds = (71001101, 72002202, 73003303, 74004404, 75005505)

    for spicy_level in (6, 7, 8):
        counts = _collect_mood_counts(monkeypatch, mode="couples", spicy_level=spicy_level, seeds=seeds)
        assert counts["calm_confident"] == 0


def test_women_random_low_and_mid_spicy_no_longer_overlock_to_calm_confident(monkeypatch):
    seeds = (1101, 2202, 3303, 4404, 5505, 6606)

    low_counts = _collect_mood_counts(monkeypatch, mode="women", spicy_level=3, seeds=seeds)
    mid_counts = _collect_mood_counts(monkeypatch, mode="women", spicy_level=5, seeds=seeds)

    assert low_counts["soft_flirty"] >= low_counts["calm_confident"]
    assert mid_counts["soft_flirty"] > mid_counts["calm_confident"]