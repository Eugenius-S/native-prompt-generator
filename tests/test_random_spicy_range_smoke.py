from backend.forms import runtime_controls


def test_random_spicy_level_random_mode_uses_current_safe_range(monkeypatch):
    seen = []

    def fake_randint(low: int, high: int) -> int:
        seen.append((low, high))
        return 3 if len(seen) == 1 else 8

    monkeypatch.setattr(runtime_controls.random, "randint", fake_randint)

    assert runtime_controls._effective_spicy_level({"spicyLevel": "random"}) == 3
    assert runtime_controls._effective_spicy_level({"spicyLevel": "random"}) == 8
    assert seen == [(3, 8), (3, 8)]
