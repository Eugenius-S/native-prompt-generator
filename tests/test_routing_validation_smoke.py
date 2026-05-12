import threading
import time

import requests


def start_server():
    from app import PromptGeneratorHandler, ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), PromptGeneratorHandler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, port


def wait_bootstrap(port: int):
    response = None
    for _ in range(30):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/api/bootstrap", timeout=2)
            if response.status_code == 200:
                return response
        except requests.RequestException:
            time.sleep(0.1)
    return response


def test_race_dropdown_exposes_curated_presets_and_keeps_other_slot():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        options = bootstrap.json()["options"]
        race_values = [item["value"] for item in options["racePresetOptions"]]
        male_race_values = [item["value"] for item in options["maleRacePresetOptions"]]

        curated_presets = {
            "white_american",
            "white_ukrainian",
            "white_russian",
            "white_polish",
            "white_italian",
            "white_spanish",
            "white_english",
            "black_american",
            "black_british",
            "black_nigerian",
            "latina_mexican",
            "latina_colombian",
            "latina_brazilian",
            "east_asian_chinese",
            "east_asian_japanese",
            "southeast_asian_thai",
            "southeast_asian_vietnamese",
            "southeast_asian_filipina",
            "middle_eastern",
            "south_asian",
        }

        for values in (race_values, male_race_values):
            assert curated_presets <= set(values)
            assert values.count("other") == 1
            assert values[-1] == "other"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_curated_race_presets_normalize_and_japanese_is_supported():
    from backend.prompt_service import _merged_form_state

    merged = _merged_form_state({
        "racePreset": "black_nigerian",
        "maleRacePreset": "white_polish",
    })
    assert merged["racePreset"] == "black_nigerian"
    assert merged["maleRacePreset"] == "white_polish"

    japanese = _merged_form_state({
        "racePreset": "east_asian_japanese",
        "maleRacePreset": "east_asian_japanese",
    })
    assert japanese["racePreset"] == "east_asian_japanese"
    assert japanese["maleRacePreset"] == "east_asian_japanese"


def test_male_custom_race_matcher_accepts_custom_identity_text():
    from backend.prompt_service import _male_race_matches_request

    male_identity = {
        "ethnicity": "White Ukrainian man",
        "_ethnicity_id": "",
        "ethnicity_group": "custom",
    }

    assert _male_race_matches_request(male_identity, "other", "White Ukrainian man") is True


def test_men_low_spicy_luxury_nightlife_and_romantic_get_calm_moods():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        for style_mode in ("luxury", "nightlife", "romantic"):
            payload = {
                "formState": {
                    "mode": "men",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": style_mode,
                    "spicyLevel": "3",
                }
            }
            response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
            assert response.status_code == 200

            run = response.json()["run"]
            moods = [item["segments"]["mood"].lower() for item in run["prompts"]]
            assert moods
            assert all(any(keyword in mood for keyword in {"quiet", "calm", "soft", "easy"}) for mood in moods)
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_fitness_and_sport_route_sporty_scenes():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        fitness_payload = {
            "formState": {
                "mode": "women",
                "batchSize": 8,
                "debugMode": True,
                "styleMode": "fitness",
                "spicyLevel": "5",
            }
        }
        fitness_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=fitness_payload, timeout=30)
        assert fitness_response.status_code == 200
        fitness_run = fitness_response.json()["run"]
        fitness_safe_outfits = {"workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
        for item in fitness_run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] in {"urban_daylight", "courtyard_garden", "coastal_boardwalk"}
            assert candidate["outfit_family_id"] in fitness_safe_outfits

        sport_payload = {
            "formState": {
                "mode": "women",
                "batchSize": 8,
                "debugMode": True,
                "styleMode": "sport",
                "spicyLevel": "5",
            }
        }
        sport_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=sport_payload, timeout=30)
        assert sport_response.status_code == 200
        sport_run = sport_response.json()["run"]
        sport_safe_outfits = {"workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers", "zip_front_training_set"}
        sport_scene_families = {"urban_daylight", "courtyard_garden", "coastal_boardwalk"}
        for item in sport_run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] in sport_scene_families
            assert candidate["route"] == "sports_flirt"
            assert candidate["outfit_family_id"] in sport_safe_outfits
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_age_input_hard_locks_the_output_age():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "women",
                "batchSize": 8,
                "debugMode": True,
                "styleMode": "random",
                "age": "22",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        assert run["prompts"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["age_band_id"] == "young_22"
            assert "22-year-old" in item["prompt"]
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_exact_theme_routing_keeps_men_bookish_on_museum_theme():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "men",
                "batchSize": 8,
                "debugMode": True,
                "styleMode": "cultural_bookish",
                "sceneFocus": "bookish",
                "locationStrategy": "exact_theme",
                "exactTheme": "museum",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "culture_bookish"
            assert candidate["route"] in {"casual_candid", "luxury_interior"}
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_exact_theme_hard_locks_scene_family_when_scene_focus_is_random():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "men",
                "batchSize": 8,
                "debugMode": True,
                "styleMode": "lifestyle",
                "sceneFocus": "random",
                "locationStrategy": "exact_theme",
                "exactTheme": "museum",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "culture_bookish"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_exact_theme_hard_locks_edge_case_scene_families_when_scene_focus_is_random():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        cases = [
            ("industrial loft", "creative_gallery"),
            ("train compartment", "culture_bookish"),
            ("fire stair landing", "urban_daylight"),
        ]

        for exact_theme, expected_scene_family in cases:
            payload = {
                "formState": {
                    "mode": "women",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "random",
                    "locationStrategy": "exact_theme",
                    "exactTheme": exact_theme,
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                }
            }
            response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
            assert response.status_code == 200, response.text

            run = response.json()["run"]
            for item in run["prompts"]:
                candidate = item["candidate"]
                assert candidate["scene_family_id"] == expected_scene_family
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_age_18_normalizes_to_the_new_adult_floor():
    from backend.prompt_service import _normalize_age_filter

    assert _normalize_age_filter("18") == {"young_18"}
    assert _normalize_age_filter("18-20") == {"young_18", "young_19", "young_20"}


def test_legacy_age_picker_keeps_the_new_floor_at_18():
    import random

    from backend.legacy_people import _pick_age_text

    assert _pick_age_text(random.Random(1), "18") == "18 years old"
    for seed in range(10):
        picked = _pick_age_text(random.Random(seed), "random")
        assert int(picked.split()[0]) >= 18


def test_couples_can_keep_dyed_hair_toggle_with_random_hair_color():
    from backend.prompt_service import _merged_form_state, _user_style_profile

    merged = _merged_form_state({
        "mode": "couples",
        "hairColorControl": "random",
        "allowDyedNaturalHairColors": True,
    })
    assert merged["allowDyedNaturalHairColors"] is True

    profile = _user_style_profile(merged, spicy_level=5)
    assert profile.get("allow_dyed_natural_hair_colors") is True

    non_random = _merged_form_state({
        "mode": "couples",
        "hairColorControl": "blonde",
        "allowDyedNaturalHairColors": True,
    })
    assert non_random["allowDyedNaturalHairColors"] is False


def test_custom_race_routing_anchors_women_ethnicity():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "women",
                "batchSize": 8,
                "debugMode": True,
                "styleMode": "lifestyle",
                "racePreset": "other",
                "customRace": "Black Nigerian woman",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["ethnicity_id"] == "black_nigerian"
            assert candidate["ethnicity_group"] == "black"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_custom_race_routing_anchors_couples_male_identity():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "couples",
                "personMode": "different_persons",
                "batchSize": 4,
                "debugMode": True,
                "styleMode": "lifestyle",
                "maleRacePreset": "other",
                "maleCustomRace": "White Ukrainian man",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        for item in run["prompts"]:
            debug_meta = item["debugMeta"]
            assert debug_meta["maleEthnicity"] == "White Ukrainian man"
            assert debug_meta["maleEthnicityGroup"] == "custom"
            assert "White Ukrainian man" in item["prompt"]
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_character_constraint_routing_prefers_sport_scene_match():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "women",
                "batchSize": 8,
                "debugMode": True,
                "styleMode": "sport",
                "characterConstraint": "Lara Croft type",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        sport_match_scene_families = {"urban_daylight", "courtyard_garden", "coastal_boardwalk"}
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] in sport_match_scene_families
            assert candidate["route"] == "sports_flirt"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_character_constraint_renders_as_dedicated_segment():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "women",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "sport",
                "characterConstraint": "Lara Croft type",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        prompt_item = run["prompts"][0]
        segments = prompt_item["segments"]
        decision = run["debug"]["promptDecisions"][0]

        assert segments["character"] == "Character read: Lara Croft type"
        assert "character read inspired by" not in segments["subject"].lower()
        assert prompt_item["candidate"]["character_constraint_segment"] == "Character read: Lara Croft type"
        assert decision["characterConstraint"] == "Lara Croft type"
        assert decision["characterConstraintSegment"] == "Character read: Lara Croft type"
        assert "Character read: Lara Croft type." in prompt_item["prompt"]
    finally:
        server.shutdown()
        thread.join(timeout=1)
