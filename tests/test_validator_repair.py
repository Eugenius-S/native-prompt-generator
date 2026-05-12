from backend.engine.validator import validate_candidate, load_rule_bank
from backend.engine.repair import repair_candidate


def _has_finding(findings, finding_id):
    return any(item.get("id") == finding_id for item in findings)


def test_wet_skin_in_bookish_repair():
    candidate = {"tags": ["wet", "bookish", "library"], "beauty_level": "beautified and flattering"}
    rules = load_rule_bank()
    findings = validate_candidate(candidate, rules)
    assert _has_finding(findings, "wet_skin_in_dry_bookish_space")
    repaired = repair_candidate(candidate, findings, rules)
    post = validate_candidate(repaired, rules)
    assert not _has_finding(post, "wet_skin_in_dry_bookish_space")


def test_swimwear_in_office_repair():
    candidate = {"tags": ["swimwear", "office", "formal_restaurant"], "beauty_level": "beautified and flattering"}
    rules = load_rule_bank()
    findings = validate_candidate(candidate, rules)
    assert _has_finding(findings, "swimwear_in_office_like_setting")
    repaired = repair_candidate(candidate, findings, rules)
    post = validate_candidate(repaired, rules)
    assert not _has_finding(post, "swimwear_in_office_like_setting")


def test_sand_without_beach_repair():
    candidate = {"tags": ["sand", "sunny", "porch"], "beauty_level": "beautified and flattering"}
    rules = load_rule_bank()
    findings = validate_candidate(candidate, rules)
    assert _has_finding(findings, "sand_without_beach_context")
    repaired = repair_candidate(candidate, findings, rules)
    post = validate_candidate(repaired, rules)
    assert not _has_finding(post, "sand_without_beach_context")


def test_sand_without_beach_repair_preserves_existing_scene_identity():
    candidate = {
        "tags": ["sand", "sunny", "porch"],
        "beauty_level": "beautified and flattering",
        "scene_family_id": "urban_daylight",
        "setting_micro_id": "city_rooftop_day",
        "setting_scene_id": "city_rooftop_day__pale_concrete_glass__city_haze__soft_filtered_daylight",
    }
    rules = load_rule_bank()
    findings = validate_candidate(candidate, rules)

    repaired = repair_candidate(candidate, findings, rules)

    assert repaired["scene_family_id"] == "urban_daylight"
    assert repaired["setting_micro_id"] == "city_rooftop_day"
    assert repaired["setting_scene_id"] == "city_rooftop_day__pale_concrete_glass__city_haze__soft_filtered_daylight"


def test_vivid_colored_hair_finding():
    candidate = {
        "tags": ["vivid_colored_hair"],
        "hair_color_tags": ["vivid_colored_hair"],
        "age_band_id": "early_30s",
        "beauty_level": "beautified and flattering",
    }
    rules = load_rule_bank()
    findings = validate_candidate(candidate, rules)
    assert _has_finding(findings, "vivid_colored_hair_age_mismatch")


def test_very_big_breasts_age_mismatch():
    candidate = {"breast_size_id": "very_big_breasts", "age_band_id": "early_30s", "beauty_level": "beautified and flattering"}
    rules = load_rule_bank()
    findings = validate_candidate(candidate, rules)
    assert _has_finding(findings, "very_big_breasts_age_mismatch")
