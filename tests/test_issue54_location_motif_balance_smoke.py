from collections import Counter

from backend.prompt_service import _merged_form_state, generate_run
from backend.services import scoring


def _run_random_women_location_motifs(seed: int) -> tuple[Counter[str], int]:
    state = _merged_form_state(
        {
            "mode": "women",
            "batchSize": 20,
            "debugMode": "on",
            "styleMode": "random",
            "spicyLevel": "6",
            "antiRepeat": "hard",
            "locationStrategy": "allow_repeats",
            "seed": str(seed),
        }
    )
    result = generate_run(state)
    prompts = result["prompts"]
    motif_counts = Counter(scoring._location_motif_for_candidate(prompt["candidate"]) for prompt in prompts if prompt.get("candidate"))
    findings = sum(len(prompt.get("findings", [])) for prompt in prompts)
    return motif_counts, findings


def test_random_women_batches_reduce_pool_and_citrus_motif_repetition() -> None:
    aggregate = Counter()
    findings_total = 0

    for seed in range(8):
        motif_counts, findings = _run_random_women_location_motifs(seed)
        aggregate.update(motif_counts)
        findings_total += findings

    total = sum(aggregate.values())

    assert findings_total == 0
    assert aggregate["waterside"] / total <= 0.42
    assert aggregate["orchard_citrus"] / total <= 0.12
    assert len([motif for motif, count in aggregate.items() if count >= 12]) >= 4
