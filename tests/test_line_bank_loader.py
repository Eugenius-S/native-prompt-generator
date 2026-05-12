import json

from backend.engine import data_loader, line_bank_loader


def test_line_bank_loader_returns_empty_structure_for_empty_tree(tmp_path) -> None:
    root = tmp_path / "line_banks"
    root.mkdir(parents=True)

    payload = line_bank_loader.load_line_bank_overrides(root)

    assert payload["enabled"] is True
    assert payload["validation"]["errors"] == []
    assert payload["validation"]["warnings"] == []
    assert payload["validation"]["stats"]["total_records"] == 0
    assert payload["records"]["women"]["poses"] == []
    assert payload["records"]["women"]["expressions"] == []
    assert payload["records"]["women"]["outfits"] == []
    assert payload["records"]["men"]["poses"] == []
    assert payload["records"]["men"]["expressions"] == []
    assert payload["records"]["men"]["outfits"] == []


def test_line_bank_loader_normalizes_and_validates_records(tmp_path) -> None:
    root = tmp_path / "line_banks"
    women_poses = root / "women" / "poses"
    women_poses.mkdir(parents=True)
    (women_poses / "1_3.md").write_text(
        "\n".join(
            [
                "# comment",
                "leaning lightly against a railing with a playful side glance",
                "leaning lightly against a railing with a playful side glance",
                "tiny",
                "x" * 141,
            ]
        ),
        encoding="utf-8",
    )
    (women_poses / "4_5.md").write_text(
        "leaning lightly against a railing with a playful side glance\n"
        "walking mid-step and looking back over the shoulder\n",
        encoding="utf-8",
    )

    payload = line_bank_loader.load_line_bank_overrides(root)
    records = payload["records"]["women"]["poses"]

    assert len(records) == 3
    assert all(record["line_bank_gender"] == "women" for record in records)
    assert all(record["line_bank_domain"] == "poses" for record in records)
    assert {record["line_bank_bucket"] for record in records} == {"1_3", "4_5"}
    assert any("duplicate line skipped in same file" in item for item in payload["validation"]["warnings"])
    assert any("Exact duplicate poses line across files for women" in item for item in payload["validation"]["warnings"])
    assert any("skipped short poses line" in item for item in payload["validation"]["warnings"])
    assert any("poses line exceeds 140 chars" in item for item in payload["validation"]["errors"])


def test_line_bank_loader_ignores_root_docs_and_comment_only_templates(tmp_path) -> None:
    root = tmp_path / "line_banks"
    women_poses = root / "women" / "poses"
    women_poses.mkdir(parents=True)
    (root / "README.md").write_text("# line-bank docs\n", encoding="utf-8")
    (root / "TROUBLESHOOTING.md").write_text("# help\n", encoding="utf-8")
    (women_poses / "1_3.md").write_text(
        "\n".join(
            [
                "# women / poses / 1_3",
                "# replace this comment with one pose per line",
            ]
        ),
        encoding="utf-8",
    )

    payload = line_bank_loader.load_line_bank_overrides(root)

    assert payload["validation"]["errors"] == []
    assert payload["validation"]["warnings"] == []
    assert payload["validation"]["stats"]["total_records"] == 0


def test_static_data_bank_stays_stable_with_empty_line_banks(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "content_bank_config.json"
    line_bank_root = tmp_path / "line_banks"
    line_bank_root.mkdir(parents=True)

    monkeypatch.setattr(data_loader, "CONTENT_BANK_CONFIG_PATH", config_path)
    monkeypatch.setattr(line_bank_loader, "LINE_BANK_ROOT", line_bank_root)

    config_path.write_text(
        json.dumps({"load_drafts": False, "load_overrides": True, "load_line_banks": False}),
        encoding="utf-8",
    )
    data_loader._load_static_data_bank.cache_clear()
    without_line_banks = data_loader._load_static_data_bank()

    config_path.write_text(
        json.dumps({"load_drafts": False, "load_overrides": True, "load_line_banks": True}),
        encoding="utf-8",
    )
    data_loader._load_static_data_bank.cache_clear()
    with_line_banks = data_loader._load_static_data_bank()

    assert without_line_banks["pose_bank"] == with_line_banks["pose_bank"]
    assert without_line_banks["styling"] == with_line_banks["styling"]
    assert without_line_banks["composition"] == with_line_banks["composition"]
    assert with_line_banks["line_banks"]["validation"]["stats"]["total_records"] == 0
    assert with_line_banks["line_banks"]["validation"]["errors"] == []


def test_repo_backed_live_pose_line_banks_load_cleanly() -> None:
    payload = line_bank_loader.load_line_bank_overrides()

    assert payload["validation"]["errors"] == []

    women_low = line_bank_loader.records_for_level(payload, gender="women", domain="poses", spicy_level=2)
    women_mid = line_bank_loader.records_for_level(payload, gender="women", domain="poses", spicy_level=4)
    men_low = line_bank_loader.records_for_level(payload, gender="men", domain="poses", spicy_level=2)
    men_high = line_bank_loader.records_for_level(payload, gender="men", domain="poses", spicy_level=7)
    couples_low = line_bank_loader.records_for_level(payload, gender="couples", domain="poses", spicy_level=2)
    couples_high = line_bank_loader.records_for_level(payload, gender="couples", domain="poses", spicy_level=7)

    assert any(record["value"] == "standing relaxed with hands in pockets" for record in women_low)
    assert any(record["value"] == "hand on hip, body turned sideways" for record in women_mid)
    assert any(record["value"] == "standing relaxed with hands in pockets" for record in men_low)
    assert any(record["value"] == "leaning forward with a low direct stare" for record in men_high)
    assert any(record["value"] == "standing close shoulder to shoulder with a relaxed shared smile" for record in couples_low)
    assert any(record["value"] == "standing chest to chest with his hand low at her waist and their focus locked on each other" for record in couples_high)

    assert all(record["line_bank_gender"] == "women" for record in women_low + women_mid)
    assert all(record["line_bank_gender"] == "men" for record in men_low + men_high)
    assert all(record["line_bank_gender"] == "couples" for record in couples_low + couples_high)
    assert all(record["line_bank_domain"] == "poses" for record in women_low + women_mid + men_low + men_high + couples_low + couples_high)


def test_repo_backed_live_expression_line_banks_load_cleanly() -> None:
    payload = line_bank_loader.load_line_bank_overrides()

    assert payload["validation"]["errors"] == []

    women_low = line_bank_loader.records_for_level(payload, gender="women", domain="expressions", spicy_level=2)
    women_high = line_bank_loader.records_for_level(payload, gender="women", domain="expressions", spicy_level=7)
    men_mid = line_bank_loader.records_for_level(payload, gender="men", domain="expressions", spicy_level=4)
    men_high = line_bank_loader.records_for_level(payload, gender="men", domain="expressions", spicy_level=7)

    assert any(record["value"] == "small closed mouth smile, relaxed cheeks" for record in women_low)
    assert any(record["value"] == "half lidded eyes, lips softly parted" for record in women_high)
    assert any(record["value"] == "faint smirk, direct eye contact" for record in men_mid)
    assert any(record["value"] == "intense stare, lips slightly parted" for record in men_high)

    assert all(record["line_bank_gender"] == "women" for record in women_low + women_high)
    assert all(record["line_bank_gender"] == "men" for record in men_mid + men_high)
    assert all(
        record["line_bank_domain"] == "expressions"
        for record in women_low + women_high + men_mid + men_high
    )


def test_repo_backed_live_outfit_line_banks_load_cleanly() -> None:
    payload = line_bank_loader.load_line_bank_overrides()

    assert payload["validation"]["errors"] == []

    women_low = line_bank_loader.records_for_level(payload, gender="women", domain="outfits", spicy_level=2)
    women_high = line_bank_loader.records_for_level(payload, gender="women", domain="outfits", spicy_level=7)
    men_low = line_bank_loader.records_for_level(payload, gender="men", domain="outfits", spicy_level=2)
    men_high = line_bank_loader.records_for_level(payload, gender="men", domain="outfits", spicy_level=7)

    assert any(record["value"] == "plain tee with straight jeans" for record in women_low)
    assert any(record["value"] == "ultra short halter dress" for record in women_high)
    assert any(record["value"] == "plain white tee with dark jeans" for record in men_low)
    assert any(record["value"] == "open black shirt over a fitted black tank and dark trousers" for record in men_high)
    assert all("bare torso" not in record["value"] for record in men_high)
    assert all("bare chest" not in record["value"] for record in men_low + men_high)

    assert all(record["line_bank_gender"] == "women" for record in women_low + women_high)
    assert all(record["line_bank_gender"] == "men" for record in men_low + men_high)
    assert all(record["line_bank_domain"] == "outfits" for record in women_low + women_high + men_low + men_high)


def test_repo_backed_live_location_line_banks_load_cleanly() -> None:
    payload = line_bank_loader.load_line_bank_overrides()

    assert payload["validation"]["errors"] == []

    shared_low = line_bank_loader.records_for_level(payload, gender="shared", domain="locations", spicy_level=2)
    shared_mid = line_bank_loader.records_for_level(payload, gender="shared", domain="locations", spicy_level=4)
    shared_high = line_bank_loader.records_for_level(payload, gender="shared", domain="locations", spicy_level=7)

    assert any(record["value"] == "wood panel corner with vertical grain and plain base" for record in shared_low)
    assert any(record["value"] == "waterfall base with dark rocks and pale mistless spray" for record in shared_low)
    assert any(record["value"] == "empty room with white walls and pale floor" for record in shared_low)
    assert any(record["value"] == "red canyon wall with smooth stone curves and dry ground" for record in shared_low)
    assert any(record["value"] == "plain terrace with stone paving and potted plants" for record in shared_low)
    assert any(record["value"] == "waiting room with pale chairs and clean base" for record in shared_low)
    fantasy_records = line_bank_loader.shared_location_records_for_domain(payload, spicy_level=2, requested_location_domain="fantasy_sci_fi")
    realism_records = line_bank_loader.shared_location_records_for_domain(payload, spicy_level=2, requested_location_domain="realism")
    assert {record["id"] for record in shared_low} == {record["id"] for record in shared_mid}
    assert {record["id"] for record in shared_low} == {record["id"] for record in shared_high}
    assert any(record["value"] == "fantasy tavern corner with dark wood, candle glow and soft smoke by the window" for record in fantasy_records)
    assert all(record.get("location_domain") == "fantasy_sci_fi" for record in fantasy_records)
    assert all(record.get("location_domain") == "realism" for record in realism_records)
    assert all(record["value"] != "fantasy tavern corner with dark wood, candle glow and soft smoke by the window" for record in realism_records)

    assert all(record["line_bank_gender"] == "shared" for record in shared_low + shared_mid + shared_high)
    assert all(record["line_bank_domain"] == "locations" for record in shared_low + shared_mid + shared_high)


def test_outfit_line_tags_and_scene_guardrails() -> None:
    bathrobe = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "a short bathrobe slightly unbuttoned at the top",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    bikini = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "a bikini top and short denim shorts",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    satin = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "deep-cut satin mini dress with sheer tights",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert "robe_like" in bathrobe["tags"]
    assert "swim_like" in bikini["tags"]
    assert line_bank_loader.line_bank_outfit_matches_scene(
        bathrobe,
        scene_family_id="grooming_bath",
        style_mode="luxury",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        bathrobe,
        scene_family_id="nightlife_bar",
        style_mode="luxury",
    )
    assert line_bank_loader.line_bank_outfit_matches_scene(
        bikini,
        scene_family_id="coastal_pool",
        style_mode="coastal",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        bikini,
        scene_family_id="residential_luxury",
        style_mode="luxury",
    )
    assert line_bank_loader.line_bank_outfit_matches_scene(
        satin,
        scene_family_id="nightlife_bar",
        style_mode="nightlife",
    )


def test_budget_club_outfit_lines_are_blocked_in_refined_modes() -> None:
    clubwear = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "club mini dress with thin straps",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert "budget_club_like" in clubwear["tags"]
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        clubwear,
        scene_family_id="residential_luxury",
        style_mode="random",
    )
    assert line_bank_loader.line_bank_outfit_matches_scene(
        clubwear,
        scene_family_id="studio",
        style_mode="studio",
    )


def test_wet_outfit_line_bank_items_require_wet_context() -> None:
    wet_tank = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "wet white tank top with tiny black shorts",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    sweater = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "soft sweater with relaxed jeans",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )

    assert "wet_like" in wet_tank["tags"]
    assert "wet_like" not in sweater["tags"]
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        wet_tank,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "urban", "daylight"},
        setting_value="sunlit city street with glass storefronts",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        wet_tank,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "luxury", "hotelized_living"},
        setting_value="quiet hotel corridor with marble floors",
    )
    assert line_bank_loader.line_bank_outfit_matches_scene(
        wet_tank,
        scene_family_id="coastal_pool",
        scene_tags={"outdoor", "pool", "coastal"},
        setting_value="poolside steps with bright reflected water",
    )
    assert line_bank_loader.line_bank_outfit_matches_scene(
        wet_tank,
        scene_family_id="wellness_spa",
        scene_tags={"interior", "spa", "humid"},
        setting_value="steam room threshold with pale stone",
    )


def test_pool_scene_blocks_tailored_blazer_high_spicy_line() -> None:
    blazer_line = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "open blazer over a lace trim bodysuit",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )

    assert not line_bank_loader.line_bank_outfit_matches_scene(
        blazer_line,
        scene_family_id="coastal_pool",
        scene_tags={"outdoor", "pool", "coastal", "daylight"},
        setting_value="poolside terrace with pale loungers and bright reflected water",
    )


def test_pose_line_tags_and_scene_guardrails() -> None:
    bed_pose = line_bank_loader.normalize_line_bank_record(
        "poses",
        "6_8",
        "sitting on the edge of the bed, knees apart",
        line_bank_loader.LINE_BANK_ROOT / "women" / "poses" / "6_8.md",
        gender="women",
    )
    chair_pose = line_bank_loader.normalize_line_bank_record(
        "poses",
        "4_5",
        "sitting on the edge of a chair, legs crossed",
        line_bank_loader.LINE_BANK_ROOT / "women" / "poses" / "4_5.md",
        gender="women",
    )
    reclined_pose = line_bank_loader.normalize_line_bank_record(
        "poses",
        "6_8",
        "half-reclined with one knee bent and her gaze held straight toward camera",
        line_bank_loader.LINE_BANK_ROOT / "women" / "poses" / "6_8.md",
        gender="women",
    )

    assert "seated_like" in bed_pose["tags"]
    assert "bed_support" in bed_pose["tags"]
    assert "chair_support" in chair_pose["tags"]
    assert "lying_like" in reclined_pose["tags"]

    assert line_bank_loader.line_bank_pose_matches_scene(
        bed_pose,
        scene_family_id="residential_luxury",
        scene_tags={"interior", "luxury", "bedroom"},
        setting_value="tailored bedroom suite with an upholstered headboard wall and crisp bedding",
    )
    assert not line_bank_loader.line_bank_pose_matches_scene(
        bed_pose,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "hotelized_living", "public_elegant"},
        setting_value="heritage hotel staircase with marble steps, brass lamps and flower arrangements in soft blur",
    )
    assert line_bank_loader.line_bank_pose_matches_scene(
        chair_pose,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "bookish"},
        setting_value="record listening room with walnut shelving, low speakers and a deep leather chair",
    )
    assert not line_bank_loader.line_bank_pose_matches_scene(
        chair_pose,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "hotelized_living", "travel"},
        setting_value="moody hotel corridor with soft wall sconces and dark carpet",
    )
    assert not line_bank_loader.line_bank_pose_matches_scene(
        reclined_pose,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "urban", "daylight"},
        setting_value="city rooftop terrace with pale concrete and a skyline beyond",
    )


def test_pose_line_bank_overhead_arm_lines_are_blocked_in_tight_framing() -> None:
    raised_arm_pose = line_bank_loader.normalize_line_bank_record(
        "poses",
        "6_8",
        "standing with both arms lifted and her torso angled in a slow stretch",
        line_bank_loader.LINE_BANK_ROOT / "women" / "poses" / "6_8.md",
        gender="women",
    )

    assert "overhead_arm_risk" in raised_arm_pose["tags"]
    assert not line_bank_loader.line_bank_pose_matches_scene(
        raised_arm_pose,
        scene_family_id="residential_luxury",
        scene_tags={"bedroom", "indoor"},
        setting_value="quiet bedroom with a chair and soft daylight",
        framing_id="waist_up",
    )
    assert line_bank_loader.line_bank_pose_matches_scene(
        raised_arm_pose,
        scene_family_id="residential_luxury",
        scene_tags={"bedroom", "indoor"},
        setting_value="quiet bedroom with a chair and soft daylight",
        framing_id="full_body",
    )


def test_location_line_tags_and_scene_guardrails() -> None:
    lounge = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "quiet hotel lounge corner with pale stone, tall drapes and soft daylight",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    conservatory = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "quiet conservatory walkway with filtered greenhouse light and patterned stone",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    cabana = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "poolside cabana threshold with pale curtains and bright coastal glare",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    meadow = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "wildflower meadow path with dry grass, scattered blooms and a golden late-afternoon glow",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert "luxury_like" in lounge["tags"]
    assert "garden_like" in conservatory["tags"]
    assert "coastal_like" in cabana["tags"]
    assert "outdoor_like" in meadow["tags"]
    assert "garden_like" in meadow["tags"]
    assert line_bank_loader.line_bank_location_matches_scene(
        lounge,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "luxury", "hotelized_living"},
        setting_value="luxury hotel suite sitting area with a low boucle sofa and city view",
    )
    assert line_bank_loader.line_bank_location_matches_scene(
        conservatory,
        scene_family_id="garden_conservatory",
        scene_tags={"interior", "greenhouse", "daylight"},
        setting_value="conservatory cafe with filtered greenhouse light and cane seating",
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        cabana,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "urban", "daylight"},
        setting_value="glass link bridge between city buildings",
    )
    assert line_bank_loader.line_bank_location_matches_scene(
        meadow,
        scene_family_id="courtyard_garden",
        scene_tags={"outdoor", "garden", "daylight"},
        setting_value="sunlit garden walkway with clipped hedges and pale gravel",
    )


def test_location_line_infers_extended_semantic_tags() -> None:
    terrace = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "sunlit city cafe terrace with woven chairs, striped shade and bright summer pavement",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    suite = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "sunlit hotel suite lounge with a low sofa, tall drapes and a restrained city view",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    booth = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "dim private lounge booth with mirror, lacquer and amber spill",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    cabana = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "poolside cabana threshold with pale curtains and bright coastal glare",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert {"public_like", "day_capable", "restaurant_like", "seat_friendly"} <= set(terrace["tags"])
    assert {"private_like", "seat_friendly"} <= set(suite["tags"])
    assert {"night_capable", "private_like", "seat_friendly"} <= set(booth["tags"])
    assert {"resort_like", "wet_humid_like", "day_capable"} <= set(cabana["tags"])


def test_location_scene_matching_respects_extended_semantics() -> None:
    terrace = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "sunlit city cafe terrace with woven chairs, striped shade and bright summer pavement",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    booth = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "dim private lounge booth with mirror, lacquer and amber spill",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert line_bank_loader.line_bank_location_matches_scene(
        terrace,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "public_elegant", "dining", "social"},
        setting_value="sunlit cafe terrace with woven chairs",
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        terrace,
        scene_family_id="grooming_bath",
        scene_tags={"spa", "private"},
        setting_value="quiet bath mirror corner",
    )
    assert line_bank_loader.line_bank_location_matches_scene(
        booth,
        scene_family_id="nightlife_bar",
        scene_tags={"social", "night", "lounge"},
        setting_value="private lacquer booth with amber lamp glow",
    )


def test_location_scene_matching_blocks_seasonal_tails_without_seasonal_context() -> None:
    winter_balcony = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "winter hotel balcony with timber rail, folded blanket and snow on rooftops",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert "winter_like" in winter_balcony["tags"]
    assert not line_bank_loader.line_bank_location_matches_scene(
        winter_balcony,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "urban", "daylight"},
        setting_value="sunlit city cafe terrace with woven chairs",
    )


def test_location_scene_matching_blocks_non_studio_shared_locations_for_studio_scene() -> None:
    record_store = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "record store aisle with vinyl bins, low shelves and warm afternoon light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        record_store,
        scene_family_id="studio",
        scene_tags={"studio", "interior"},
        setting_value="controlled studio sweep with seamless backdrop",
    )


def test_location_scene_matching_blocks_institutional_tail_for_hospitality_suite() -> None:
    school_gym = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "school gym corner with varnished floor, wall padding and high window light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        school_gym,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "luxury", "hotelized_living"},
        setting_value="luxury hotel suite sitting area with a low boucle sofa and city view",
    )


def test_location_scene_matching_blocks_pool_tail_for_culture_bookish() -> None:
    infinity_pool = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "infinity pool edge with mirrored water, pale tile and harsh noon light over a distant skyline",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        infinity_pool,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "bookish", "quiet"},
        setting_value="quiet library room with warm wood shelves and shaded reading chairs",
    )


def test_location_scene_matching_blocks_generic_home_tail_for_garden_conservatory() -> None:
    living_room = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "tidy living room sofa corner with ivory cushions, folded throw and window light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        living_room,
        scene_family_id="garden_conservatory",
        scene_tags={"interior", "greenhouse", "daylight"},
        setting_value="conservatory cafe with filtered greenhouse light and cane seating",
    )


def test_location_scene_matching_blocks_dorm_tail_for_hospitality_suite() -> None:
    dorm_room = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "clean dorm room corner with simple desk, narrow bed and late day window light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        dorm_room,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "luxury", "hotelized_living"},
        setting_value="luxury hotel suite sitting area with a low boucle sofa and city view",
    )


def test_location_scene_matching_blocks_artist_loft_tail_for_residential_luxury() -> None:
    artist_corner = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "artist apartment corner with paint tubes, wood floor and tall window glow",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        artist_corner,
        scene_family_id="residential_luxury",
        scene_tags={"interior", "luxury", "private"},
        setting_value="quiet luxury apartment salon with bookmatched marble, soft drapes and controlled daylight",
    )


def test_location_scene_matching_blocks_pool_shower_tail_for_residential_luxury() -> None:
    pool_shower = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "private pool shower with stone wall, wet floor and bright sun reflections",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        pool_shower,
        scene_family_id="residential_luxury",
        scene_tags={"interior", "luxury", "private"},
        setting_value="quiet luxury apartment salon with bookmatched marble, soft drapes and controlled daylight",
    )


def test_location_scene_matching_blocks_pool_shower_tail_for_creative_gallery() -> None:
    pool_shower = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "private pool shower with stone wall, wet floor and bright sun reflections",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        pool_shower,
        scene_family_id="creative_gallery",
        scene_tags={"interior", "creative", "editorial"},
        setting_value="quiet gallery room with white walls, plinths and controlled concept light",
    )


def test_location_scene_matching_blocks_nightlife_tail_for_hospitality_suite() -> None:
    jazz_club = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "jazz club table near stage with velvet seats, brass lamp and smoky warm light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        jazz_club,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "luxury", "hotelized_living"},
        setting_value="luxury hotel suite sitting area with a low boucle sofa and city view",
    )


def test_location_scene_matching_blocks_day_promenade_for_nightlife_scene() -> None:
    promenade = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "Swiss lakeside promenade with stone rail, mountain haze and clean morning light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        promenade,
        scene_family_id="nightlife_neon",
        scene_tags={"night", "social", "neon"},
        setting_value="after-dark neon corridor with glossy walls and colored spill",
    )


def test_location_scene_matching_blocks_day_promenade_for_nightlife_scene_even_with_neutral_context_tags() -> None:
    promenade = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "Swiss lakeside promenade with stone rail, mountain haze and clean morning light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        promenade,
        scene_family_id="nightlife_neon",
        scene_tags={"interior", "social"},
        setting_value="moody lounge passage with dark lacquer and colored spill",
    )


def test_location_scene_matching_blocks_transit_tail_for_nightlife_scene() -> None:
    bus_stop = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "late night bus stop with glass panels, cold light and wet pavement",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        bus_stop,
        scene_family_id="nightlife_bar",
        scene_tags={"night", "social", "lounge"},
        setting_value="private lacquer booth with amber lamp glow",
    )


def test_location_scene_matching_blocks_night_only_tail_for_urban_daylight() -> None:
    rooftop_night = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "rooftop at night with antennas, low parapet and cold city glow",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert not line_bank_loader.line_bank_location_matches_scene(
        rooftop_night,
        scene_family_id="urban_daylight",
        scene_tags={"outdoor", "urban", "daylight"},
        setting_value="bright city street with glass storefront reflections and noon sun",
    )


def test_location_scene_matching_respects_exact_theme_keywords_for_edge_cases() -> None:
    train_compartment = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "night train compartment with warm lamp, dark window and streaking city lights",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    subway_platform = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "empty subway platform with glossy floor, tiled walls and cold overhead light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    station_cafe = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "train station cafe corner with brass trim, marble table and warm overhead light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    fire_stair = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "apartment fire stair landing with metal steps, brick wall and soft cloudy light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )
    museum_room = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "empty museum room with pale bench, clean walls and controlled skylight",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert line_bank_loader.line_bank_location_matches_scene(
        train_compartment,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "travel", "bookish", "night", "modest_safe"},
        setting_value="first class train compartment at dusk with wood paneling, cream curtains and city lights outside the window",
        exact_theme_keywords={"compartment"},
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        subway_platform,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "travel", "bookish", "night", "modest_safe"},
        setting_value="first class train compartment at dusk with wood paneling, cream curtains and city lights outside the window",
        exact_theme_keywords={"compartment"},
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        station_cafe,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "travel", "bookish", "night", "modest_safe"},
        setting_value="first class train compartment at dusk with wood paneling, cream curtains and city lights outside the window",
        exact_theme_keywords={"compartment"},
    )
    assert line_bank_loader.line_bank_location_matches_scene(
        fire_stair,
        scene_family_id="urban_daylight",
        scene_tags={"interior", "urban", "daylight"},
        setting_value="glass link bridge between city buildings with long reflections and pale floor wash",
        exact_theme_keywords={"fire", "escape"},
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        museum_room,
        scene_family_id="urban_daylight",
        scene_tags={"interior", "urban", "daylight"},
        setting_value="glass link bridge between city buildings with long reflections and pale floor wash",
        exact_theme_keywords={"fire", "escape"},
    )


def test_location_scene_matching_respects_requested_location_domain() -> None:
    fantasy_library = line_bank_loader.normalize_line_bank_record(
        "locations",
        "fantasy_locations",
        "old library aisle with tall ladders, dark wood shelves and soft top light",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "fantasy_locations.md",
        gender="shared",
    )
    realism_lounge = line_bank_loader.normalize_line_bank_record(
        "locations",
        "all",
        "quiet hotel lounge corner with pale stone, tall drapes and soft daylight",
        line_bank_loader.LINE_BANK_ROOT / "shared" / "locations" / "all.md",
        gender="shared",
    )

    assert fantasy_library["location_domain"] == "fantasy_sci_fi"
    assert realism_lounge["location_domain"] == "realism"
    assert line_bank_loader.line_bank_location_matches_scene(
        fantasy_library,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "bookish", "quiet"},
        setting_value="quiet library room with warm wood shelves and shaded reading chairs",
        requested_location_domain="fantasy_sci_fi",
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        fantasy_library,
        scene_family_id="culture_bookish",
        scene_tags={"interior", "bookish", "quiet"},
        setting_value="quiet library room with warm wood shelves and shaded reading chairs",
        requested_location_domain="realism",
    )
    assert not line_bank_loader.line_bank_location_matches_scene(
        realism_lounge,
        scene_family_id="hospitality_suite",
        scene_tags={"interior", "luxury", "hotelized_living"},
        setting_value="luxury hotel suite sitting area with a low boucle sofa and city view",
        requested_location_domain="fantasy_sci_fi",
    )


def test_outfit_line_infers_extended_semantic_tags() -> None:
    sundress = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "light sundress with flat sandals",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )
    trousers = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "linen blouse with loose trousers",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )
    robe = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "open satin robe over a matching lace set",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    sporty = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "zip jacket with leggings and running shoes",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )

    assert {"hot_weather_ok", "casual_like"} <= set(sundress["tags"])
    assert {"indoor_neutral_ok", "restaurant_ok", "seat_friendly"} <= set(trousers["tags"])
    assert {"lounge_ok", "minimal_coverage", "dressy_like"} <= set(robe["tags"])
    assert {"active_ok", "casual_like"} <= set(sporty["tags"])


def test_outfit_scene_matching_respects_extended_semantics() -> None:
    dress = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "linen blouse with a midi skirt",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )
    robe = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "6_8",
        "open satin robe over a matching lace set",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "6_8.md",
        gender="women",
    )
    leggings = line_bank_loader.normalize_line_bank_record(
        "outfits",
        "1_3",
        "zip jacket with leggings and running shoes",
        line_bank_loader.LINE_BANK_ROOT / "women" / "outfits" / "1_3.md",
        gender="women",
    )

    assert line_bank_loader.line_bank_outfit_matches_scene(
        dress,
        scene_family_id="urban_daylight",
        style_mode="lifestyle",
        scene_tags={"public_elegant", "dining", "social"},
        setting_value="sunlit cafe terrace with woven chairs",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        robe,
        scene_family_id="urban_daylight",
        style_mode="lifestyle",
        scene_tags={"public_elegant", "dining", "social"},
        setting_value="sunlit cafe terrace with woven chairs",
    )
    assert not line_bank_loader.line_bank_outfit_matches_scene(
        leggings,
        scene_family_id="nightlife_bar",
        style_mode="nightlife",
        scene_tags={"night", "social", "dining"},
        setting_value="velvet booth with low lamp glow",
    )
