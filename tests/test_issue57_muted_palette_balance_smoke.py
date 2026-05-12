from collections import Counter

from backend.prompt_service import _merged_form_state, generate_run


CLONE_PRONE_MUTED = {
    "clean_neutrals",
    "champagne_taupe",
    "rosewood_smoke",
}


def _run_random_women_color_stats(seed: int) -> tuple[Counter[str], int]:
    state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "6",
            "antiRepeat": "hard",
            "seed": str(seed),
        }
    )
    result = generate_run(state)
    prompts = result["prompts"]
    colors = Counter(prompt["candidate"].get("color_story_id") for prompt in prompts if prompt.get("candidate"))
    findings = sum(len(prompt.get("findings", [])) for prompt in prompts)
    return colors, findings


def test_random_women_batches_reduce_muted_palette_dominance() -> None:
    aggregate = Counter()
    findings_total = 0

    for seed in range(8):
        colors, findings = _run_random_women_color_stats(seed)
        aggregate.update(colors)
        findings_total += findings

    total = sum(aggregate.values())
    clone_prone_muted_total = sum(aggregate[color_id] for color_id in CLONE_PRONE_MUTED)

    assert findings_total == 0
    assert aggregate["clean_neutrals"] / total <= 0.18
    assert clone_prone_muted_total / total <= 0.30
    assert len([color_id for color_id, count in aggregate.items() if count >= 4]) >= 5