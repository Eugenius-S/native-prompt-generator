from __future__ import annotations

import random
from typing import Any

from backend.engine import generator
from backend.engine.validator import load_rule_bank, validate_candidate
from backend.forms import user_profile as form_user_profile
from backend.forms.runtime_controls import _infer_theme_style_mode
from backend.services import scoring


RELAXABLE_APPEARANCE_CONSTRAINTS = (
    ("required_hair_color_ids", "preferred_hair_color_ids"),
    ("required_male_hair_ids", "preferred_male_hair_ids"),
    ("required_eye_color_ids", "preferred_eye_color_ids"),
    ("required_male_grooming_ids", "preferred_male_grooming_ids"),
    ("required_breast_size_ids", "preferred_breast_size_ids"),
)

SOFT_STEERING_CONSTRAINTS = {
    "preferred_outfit_ids",
    "preferred_material_ids",
    "preferred_color_story_ids",
    "preferred_pose_ids",
    "preferred_route_ids",
    "preferred_photo_treatment_ids",
    "preferred_makeup_ids",
}


def _relax_profile_constraint(profile: dict[str, Any], required_key: str, preferred_key: str) -> dict[str, Any] | None:
    relaxed = dict(profile)
    required_values = set(relaxed.get(required_key, set()))
    if not required_values:
        return None
    preferred_values = set(relaxed.get(preferred_key, set()))
    relaxed[preferred_key] = preferred_values | required_values
    relaxed.pop(required_key, None)
    return relaxed


def _relaxed_generation_profiles(profile: dict[str, Any]) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []

    def add_profile(candidate_profile: dict[str, Any]) -> None:
        if candidate_profile not in profiles:
            profiles.append(candidate_profile)

    def add_broad_profile(candidate_profile: dict[str, Any]) -> None:
        broad = {key: value for key, value in candidate_profile.items() if key not in SOFT_STEERING_CONSTRAINTS}
        if broad != candidate_profile:
            add_profile(broad)

    current = profile
    for required_key, preferred_key in RELAXABLE_APPEARANCE_CONSTRAINTS:
        relaxed = _relax_profile_constraint(current, required_key, preferred_key)
        if relaxed is None:
            continue
        add_profile(relaxed)
        add_broad_profile(relaxed)
        current = relaxed
    add_broad_profile(profile)
    return profiles


def _best_batch(
    form_state: dict[str, Any],
    spicy_level: int,
    use_recent_batch_rules: bool,
    use_memory_rules: bool,
) -> tuple[list[dict[str, Any]], dict[int, list[dict[str, str]]], int]:
    base_seed = random.randint(10_000_000, 999_999_999)
    rules = load_rule_bank()
    batch_payload = tuple[
        int,
        list[dict[str, Any]],
        dict[int, list[dict[str, str]]],
        int,
        dict[str, Any],
        bool,
        bool,
    ]
    best_payload: batch_payload | None = None
    best_valid_payload: batch_payload | None = None
    effective_style_mode = _infer_theme_style_mode(form_state)
    scoring_form_state = dict(form_state)
    scoring_form_state["styleMode"] = effective_style_mode
    user_profile = form_user_profile._user_style_profile(scoring_form_state, spicy_level)
    relaxed_user_profiles = _relaxed_generation_profiles(user_profile)
    strict_couples_different_persons = form_state["mode"] == "couples" and form_state["personMode"] == "different_persons"
    ethnicity_group_override = None
    preferred_ethnicity_ids: set[str] = set()
    ethnicity_id_pool: set[str] | None = None
    if form_state["racePreset"] == "other" and form_state["customRace"]:
        ethnicity_group_override, preferred_ethnicity_ids = scoring._custom_race_preferences(form_state["customRace"])
    elif form_state["racePreset"] in scoring.SAME_PERSON_ETHNICITY_IDS:
        preferred_ethnicity_ids = {form_state["racePreset"]}
        ethnicity_id_pool = {form_state["racePreset"]}
    elif form_state["racePreset"] == "random_default_split":
        ethnicity_id_pool = scoring._random_default_ethnicity_ids()
    elif form_state["racePreset"] == "mostly_mixed":
        ethnicity_id_pool = scoring._mostly_mixed_ethnicity_ids()
    elif form_state["racePreset"] in scoring.SAME_PERSON_RACE_GROUPS:
        ethnicity_group_override = scoring.SAME_PERSON_RACE_GROUPS.get(form_state["racePreset"])
    attempt_budget = 80
    if form_state["antiRepeat"] in {"hard", "brutal"}:
        attempt_budget += 40
    if form_state["locationStrategy"] == "exact_theme" and form_state["exactTheme"]:
        attempt_budget += 40
    if form_state["racePreset"] == "other" and form_state["customRace"]:
        attempt_budget += 20
    if form_state["racePreset"] in scoring.SAME_PERSON_ETHNICITY_IDS:
        attempt_budget += 10
    if strict_couples_different_persons and (scoring._normalize_age_filter(form_state["age"]) or form_state["racePreset"] != "random_default_split"):
        attempt_budget += 20
    enforce_male_identity_constraints = strict_couples_different_persons and scoring._explicit_male_identity_constraints_active(form_state)
    if enforce_male_identity_constraints:
        attempt_budget += 20
        attempt_budget += 40
    if len(set(user_profile.get("required_hair_color_ids", set()))) == 1:
        attempt_budget = min(attempt_budget, 16)
    search_passes: list[tuple[int, dict[str, Any], bool, bool]] = [(attempt_budget, user_profile, use_recent_batch_rules, use_memory_rules)]
    fallback_attempt_budget = max(12, min(24, attempt_budget // 4))
    for relaxed_user_profile in relaxed_user_profiles:
        search_passes.append((fallback_attempt_budget, relaxed_user_profile, False, False))

    for pass_attempt_budget, pass_profile, pass_use_recent_batch_rules, pass_use_memory_rules in search_passes:
        for attempt in range(pass_attempt_budget):
            seed = base_seed + attempt * 9973
            try:
                batch = generator.generate_batch(
                    form_state["batchSize"],
                    seed=seed,
                    identity_lock=form_state["personMode"] == "same_person",
                    persist_memory=False,
                    use_recent_batch_rules=pass_use_recent_batch_rules,
                    use_memory_rules=pass_use_memory_rules,
                    style_mode=effective_style_mode,
                    ethnicity_group_override=ethnicity_group_override,
                    preferred_ethnicity_ids=preferred_ethnicity_ids,
                    ethnicity_id_pool=ethnicity_id_pool,
                    user_profile=pass_profile,
                    mode=form_state["mode"],
                    spicy_level=spicy_level,
                    photo_type_control=str(form_state.get("photoTypeControl", "balanced") or "balanced"),
                )
            except ValueError:
                continue
            findings_map = {index: validate_candidate(candidate, rules) for index, candidate in enumerate(batch)}
            score, hard_fail = scoring._batch_score(batch, scoring_form_state, findings_map, spicy_level, seed)
            payload = (score, batch, findings_map, seed, pass_profile, pass_use_recent_batch_rules, pass_use_memory_rules)
            if best_payload is None or score > best_payload[0]:
                best_payload = payload
            if not hard_fail and (best_valid_payload is None or score > best_valid_payload[0]):
                best_valid_payload = payload
            if not hard_fail and score >= form_state["batchSize"] * 10:
                best_payload = payload
                best_valid_payload = payload
                break
        if best_payload is not None:
            break
    if best_payload is None:
        raise ValueError("Could not generate a valid batch.")
    if enforce_male_identity_constraints:
        if best_valid_payload is None:
            raise ValueError("Could not satisfy male-side identity constraints for couples different_persons batch.")
        best_payload = best_valid_payload
    _, selected_batch, selected_findings, chosen_seed, _selected_profile, _selected_use_recent_batch_rules, _selected_use_memory_rules = best_payload
    generator.persist_batch_memory(selected_batch)
    return selected_batch, selected_findings, chosen_seed
