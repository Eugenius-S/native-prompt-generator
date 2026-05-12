from collections import Counter

from backend.prompt_service import _merged_form_state, generate_run


def _women_random_batch() -> list[dict[str, object]]:
    state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "6",
            "antiRepeat": "hard",
        }
    )
    run = generate_run(state)
    prompts = run["prompts"]
    assert len(prompts) == 20
    return [prompt["candidate"] for prompt in prompts]


def test_issue86_random_women_body_type_mix_stays_curved_light() -> None:
    body_totals = Counter()
    for _ in range(5):
        candidates = _women_random_batch()
        body_totals.update(candidate["body_group"] for candidate in candidates)

    assert body_totals["curvy"] == 10
    assert body_totals["lean"] + body_totals["toned"] + body_totals["athletic"] == 90


def test_issue85_random_women_breast_size_mix_stays_visible() -> None:
    breast_totals = Counter()
    for _ in range(5):
        candidates = _women_random_batch()
        breast_totals.update(candidate["breast_size_id"] for candidate in candidates)

    assert breast_totals["small_breasts"] == 10
    assert breast_totals["medium_breasts"] + breast_totals["big_breasts"] == 80
    assert breast_totals["very_big_breasts"] + breast_totals["extra_large_breasts"] == 10