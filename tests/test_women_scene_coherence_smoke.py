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


def test_women_lifestyle_bookish_exact_theme_avoids_hot_or_sporty_outfits():
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
                "sceneFocus": "bookish",
                "locationStrategy": "exact_theme",
                "exactTheme": "museum",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        banned_outfit_ids = {
            "mini_dress",
            "blazer_mini_dress",
            "bodysuit_trousers",
            "polo_pleated_skirt",
            "workout_top_leggings",
            "zip_jacket_leggings",
            "training_jacket_trousers",
        }
        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "culture_bookish"
            assert candidate["outfit_family_id"] not in banned_outfit_ids
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_cultural_bookish_exact_theme_avoids_hot_outfits():
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
                "styleMode": "cultural_bookish",
                "sceneFocus": "bookish",
                "locationStrategy": "exact_theme",
                "exactTheme": "museum",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        banned_outfit_ids = {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "corset_trousers"}
        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "culture_bookish"
            assert candidate["outfit_family_id"] not in banned_outfit_ids
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_luxury_exact_theme_avoids_bodysuit_trousers():
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
                "styleMode": "luxury",
                "sceneFocus": "luxury",
                "locationStrategy": "exact_theme",
                "exactTheme": "hotel lobby",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        mini_dress_count = sum(1 for item in run["prompts"] if item["candidate"]["outfit_family_id"] == "mini_dress")
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] in {"residential_luxury", "hospitality_suite", "grooming_bath"}
            assert candidate["outfit_family_id"] != "bodysuit_trousers"
        assert mini_dress_count <= 2
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_nightlife_exact_theme_avoids_daywear_outfits():
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
                "styleMode": "nightlife",
                "sceneFocus": "nightlife",
                "locationStrategy": "exact_theme",
                "exactTheme": "cocktail bar",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        daywear_outfit_ids = {"cardigan_skirt", "cardigan_trousers", "shirt_trousers", "sweater_jeans"}
        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] in {"nightlife_bar", "nightlife_neon"}
            assert candidate["outfit_family_id"] not in daywear_outfit_ids
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_scene_family_control_locks_exact_scene_family():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "women",
                "batchSize": 6,
                "debugMode": True,
                "styleMode": "lifestyle",
                "sceneFocus": "random",
                "womenSceneFamily": "wellness_spa",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        assert run["debug"]["effectiveWomenSceneFamily"] == "wellness_spa"
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "wellness_spa"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_scene_family_override_beats_broader_scene_focus_family_pool():
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
                "sceneFocus": "coastal",
                "womenSceneFamily": "coastal_pool",
                "antiRepeat": "hard",
                "validationMode": "strict",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        assert run["debug"]["effectiveWomenSceneFamily"] == "coastal_pool"
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "coastal_pool"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_scene_family_fine_controls_shape_reveal_hair_and_makeup():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        wellness_payload = {
            "formState": {
                "mode": "women",
                "batchSize": 6,
                "debugMode": True,
                "styleMode": "random",
                "sceneFocus": "random",
                "womenSceneFamily": "wellness_spa",
            }
        }
        nightlife_payload = {
            "formState": {
                "mode": "women",
                "batchSize": 6,
                "debugMode": True,
                "styleMode": "random",
                "sceneFocus": "random",
                "womenSceneFamily": "nightlife_bar",
            }
        }

        wellness_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=wellness_payload, timeout=30)
        nightlife_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=nightlife_payload, timeout=30)
        assert wellness_response.status_code == 200
        assert nightlife_response.status_code == 200

        wellness_run = wellness_response.json()["run"]
        nightlife_run = nightlife_response.json()["run"]

        assert wellness_run["debug"]["effectiveOutfitReveal"] == "reserved"
        assert nightlife_run["debug"]["effectiveOutfitReveal"] == "revealing"

        women_banned_hair_ids = {"male_clean_side_part", "male_textured_crop", "male_medium_pushback", "male_soft_quiff", "male_wavy_brushback"}
        wellness_allowed_makeup = {"fresh_barely_there", "clean_minimal", "natural_pretty"}
        wellness_disallowed_outfits = {"mini_dress", "blazer_mini_dress", "bodysuit_trousers", "corset_trousers", "latex_editorial", "crop_top_mini_skirt", "swimsuit", "bikini_set"}
        nightlife_allowed_makeup = {"night_out_glam", "glossy_soft_glam"}
        nightlife_disallowed_outfits = {"cardigan_trousers", "blouse_trousers", "shirt_trousers", "structured_day_dress", "silk_blouse_midi_skirt", "knit_top_trousers", "cashmere_shell_trousers"}

        for item in wellness_run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "wellness_spa"
            assert candidate["hair_structure_id"] not in women_banned_hair_ids
            assert candidate["makeup_style_id"] in wellness_allowed_makeup
            assert candidate["outfit_family_id"] not in wellness_disallowed_outfits

        for item in nightlife_run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "nightlife_bar"
            assert candidate["hair_structure_id"] not in women_banned_hair_ids
            assert candidate["makeup_style_id"] in nightlife_allowed_makeup
            assert candidate["outfit_family_id"] not in nightlife_disallowed_outfits
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_women_random_hair_can_use_natural_dyed_colors_when_enabled():
    import json
    import random
    from pathlib import Path

    from backend.engine import generator

    styling_path = Path(__file__).resolve().parents[1] / "backend" / "engine" / "data" / "styling.json"
    hair_colors = json.loads(styling_path.read_text(encoding="utf-8"))["hair_colors"]
    allowed_natural_dyed_ids = {"copper_dyed", "burgundy_dyed", "silver_dyed"}
    vivid_dyed_ids = {"pastel_pink_dyed", "lavender_dyed", "electric_blue_dyed"}

    captured: dict[str, list[str]] = {}

    def fake_weighted_pick_filtered(items, rnd, predicate=None, avoid_id=None, avoid_ids=None, preferred_predicate=None):
        allowed_ids = [item["id"] for item in items if predicate is None or predicate(item)]
        captured["allowed_ids"] = allowed_ids
        for item in items:
            if predicate is None or predicate(item):
                return item
        raise AssertionError("No allowed hair color matched the predicate")

    original = generator._weighted_pick_filtered
    generator._weighted_pick_filtered = fake_weighted_pick_filtered
    try:
        generator._choose_hair_color(
            hair_colors,
            random.Random(7),
            "young_18",
            False,
            "white",
            None,
            required_ids=set(),
            preferred_ids=set(),
            allow_dyed_natural=False,
        )
        assert allowed_natural_dyed_ids.isdisjoint(captured["allowed_ids"])
        assert vivid_dyed_ids.isdisjoint(captured["allowed_ids"])

        generator._choose_hair_color(
            hair_colors,
            random.Random(7),
            "young_18",
            False,
            "white",
            None,
            required_ids=set(),
            preferred_ids=set(),
            allow_dyed_natural=True,
        )
        assert {"black_natural", "blonde_natural"}.issubset(set(captured["allowed_ids"]))
        assert allowed_natural_dyed_ids.issubset(set(captured["allowed_ids"]))
        assert vivid_dyed_ids.isdisjoint(captured["allowed_ids"])
    finally:
        generator._weighted_pick_filtered = original


def test_random_scene_context_blocks_obvious_outfit_and_pose_spillover():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        cases = [
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "wellness",
                    "womenSceneFamily": "wellness_spa",
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                },
                "bad_outfits": {"sweater_jeans", "cardigan_trousers", "blouse_trousers", "shirt_trousers"},
                "bad_poses": set(),
            },
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "coastal",
                    "womenSceneFamily": "coastal_pool",
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                },
                "bad_outfits": {"sweater_jeans", "cardigan_trousers", "blouse_trousers", "shirt_trousers", "knit_top_trousers", "cashmere_shell_trousers"},
                "bad_poses": set(),
            },
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "bookish",
                    "womenSceneFamily": "culture_bookish",
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                },
                "bad_outfits": set(),
                "bad_poses": {"track_shoe_tie_block"},
            },
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "creative",
                    "womenSceneFamily": "creative_gallery",
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                },
                "bad_outfits": set(),
                "bad_poses": {"track_shoe_tie_block"},
            },
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "luxury",
                    "womenSceneFamily": "random",
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                },
                "bad_outfits": {
                    "blazer_mini_dress",
                    "bodysuit_trousers",
                    "corset_trousers",
                    "cami_midi_skirt",
                    "latex_editorial",
                    "vest_trousers",
                    "halter_trousers",
                },
                "bad_poses": {"kneeling_both_knees", "one_knee_raised_floor_pose"},
            },
            {
                "formState": {
                    "mode": "women",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "random",
                    "sceneFocus": "random",
                    "womenSceneFamily": "urban_daylight",
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                },
                "bad_outfits": set(),
                "bad_poses": {"window_turn_teacup", "chess_piece_reach_up", "tea_pour_tray_level", "map_table_both_hands", "cabinet_reach_inside", "pottery_wheel_lift_face"},
            },
            {
                "formState": {
                    "mode": "couples",
                    "batchSize": 8,
                    "debugMode": True,
                    "styleMode": "lifestyle",
                    "sceneFocus": "bookish",
                    "antiRepeat": "hard",
                    "validationMode": "strict",
                },
                "bad_outfits": set(),
                "bad_poses": {"track_shoe_tie_block"},
            },
        ]

        for case in cases:
            for _ in range(3):
                response = requests.post(f"http://127.0.0.1:{port}/api/generate", json={"formState": case["formState"]}, timeout=30)
                assert response.status_code == 200, response.text
                run = response.json()["run"]
                for item in run["prompts"]:
                    candidate = item["candidate"]
                    if case["formState"]["mode"] == "women" and case["formState"].get("womenSceneFamily") not in {None, "random"}:
                        assert candidate["scene_family_id"] == case["formState"]["womenSceneFamily"]
                        assert run["debug"]["effectiveWomenSceneFamily"] == case["formState"]["womenSceneFamily"]
                    if case["formState"]["mode"] == "women" and case["formState"].get("sceneFocus") == "luxury":
                        assert candidate["scene_family_id"] in {"residential_luxury", "hospitality_suite", "grooming_bath"}
                        if candidate["scene_family_id"] == "residential_luxury":
                            assert candidate["outfit_family_id"] not in case["bad_outfits"]
                        if candidate["scene_family_id"] in {"residential_luxury", "hospitality_suite"}:
                            assert candidate["pose_family_id"] not in case["bad_poses"]
                    else:
                        assert candidate["outfit_family_id"] not in case["bad_outfits"]
                        assert candidate["pose_family_id"] not in case["bad_poses"]
    finally:
        server.shutdown()
        thread.join(timeout=1)
