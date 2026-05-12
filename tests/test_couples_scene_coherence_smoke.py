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


def test_couples_lifestyle_bookish_exact_theme_avoids_sporty_female_outfits():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "couples",
                "personMode": "different_persons",
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

        sporty_outfit_ids = {"polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] == "culture_bookish"
            assert candidate["outfit_family_id"] not in sporty_outfit_ids
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_couples_luxury_exact_theme_avoids_bodysuit_trousers():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "couples",
                "personMode": "different_persons",
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
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] in {"residential_luxury", "hospitality_suite", "grooming_bath"}
            assert candidate["outfit_family_id"] != "bodysuit_trousers"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_couples_nightlife_exact_theme_avoids_daywear_female_outfits():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "couples",
                "personMode": "different_persons",
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

        daywear_outfit_ids = {"cardigan_skirt", "cardigan_trousers", "shirt_trousers", "sweater_jeans", "polo_pleated_skirt", "workout_top_leggings", "zip_jacket_leggings", "training_jacket_trousers"}
        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            assert candidate["scene_family_id"] in {"nightlife_bar", "nightlife_neon"}
            assert candidate["outfit_family_id"] not in daywear_outfit_ids
    finally:
        server.shutdown()
        thread.join(timeout=1)
