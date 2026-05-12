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


def test_male_appearance_controls_smoke():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        data = bootstrap.json()
        options = data.get("options", {})
        assert any(opt.get("value") == "male_clean_side_part" for opt in options.get("maleHairstyleOptions", []))
        assert any(opt.get("value") == "male_soft_quiff" for opt in options.get("maleHairstyleOptions", []))
        assert any(opt.get("value") == "male_wavy_brushback" for opt in options.get("maleHairstyleOptions", []))
        assert any(opt.get("value") == "clean_shaven" for opt in options.get("maleGroomingOptions", []))
        assert any(opt.get("value") == "athletic" for opt in options.get("bodyMixPresetOptions", []))
        male_outfit_values = [opt.get("value") for opt in options.get("maleOutfitOptions", [])]
        assert any(value == "random" for value in male_outfit_values)
        assert any(value == "luxury" for value in male_outfit_values)
        assert any(value == "nightlife" for value in male_outfit_values)
        assert any(value == "coastal" for value in male_outfit_values)
        assert all(not str(value).startswith("male_") for value in male_outfit_values if value)

        men_payload = {
            "formState": {
                "mode": "men",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "luxury",
                "bodyMixPreset": "athletic",
                "maleHairLength": "short",
                "maleHairstyle": "male_soft_quiff",
                "maleGroomingControl": "clean_shaven",
                "maleOutfitControl": "luxury",
            }
        }
        men_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=men_payload, timeout=30)
        assert men_response.status_code == 200
        men_run = men_response.json()["run"]
        men_prompt = men_run["prompts"][0]["prompt"]
        men_decision = men_run["debug"]["promptDecisions"][0]
        assert any(phrase in men_prompt for phrase in ("athletic build", "muscular athletic build"))
        assert "soft textured quiff" in men_prompt
        assert "clean-shaven" in men_prompt
        assert men_decision.get("maleOutfitVibe") == "luxury"

        couples_payload = {
            "formState": {
                "mode": "couples",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "nightlife",
                "maleHairLength": "medium",
                "maleHairstyle": "male_wavy_brushback",
                "maleGroomingControl": "trimmed_beard",
                "maleOutfitControl": "nightlife",
            }
        }
        couples_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=couples_payload, timeout=30)
        assert couples_response.status_code == 200
        couples_run = couples_response.json()["run"]
        couples_prompt = couples_run["prompts"][0]["prompt"]
        couples_decision = couples_run["debug"]["promptDecisions"][0]
        assert "medium wavy hair brushed back" in couples_prompt
        assert "trimmed beard" in couples_prompt
        assert couples_decision.get("maleOutfitVibe") == "nightlife"

        prompt_decision = couples_run["debug"]["promptDecisions"][0]
        assert prompt_decision.get("maleHair") == "medium wavy hair brushed back"
        assert prompt_decision.get("maleOutfitVibe") == "nightlife"
        assert prompt_decision.get("maleGrooming") == "trimmed beard"
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_male_outfit_random_tracks_scene_vibe():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        nightlife_payload = {
            "formState": {
                "mode": "men",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "random",
                "sceneFocus": "nightlife",
                "maleOutfitControl": "random",
            }
        }
        coastal_payload = {
            "formState": {
                "mode": "men",
                "batchSize": 1,
                "debugMode": True,
                "styleMode": "random",
                "sceneFocus": "coastal",
                "maleOutfitControl": "random",
            }
        }

        nightlife_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=nightlife_payload, timeout=30)
        coastal_response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=coastal_payload, timeout=30)
        assert nightlife_response.status_code == 200
        assert coastal_response.status_code == 200

        nightlife_run = nightlife_response.json()["run"]
        coastal_run = coastal_response.json()["run"]
        nightlife_decision = nightlife_run["debug"]["promptDecisions"][0]
        coastal_decision = coastal_run["debug"]["promptDecisions"][0]

        assert nightlife_decision.get("maleOutfitVibe") == "nightlife"
        assert coastal_decision.get("maleOutfitVibe") == "coastal"
        assert nightlife_decision.get("maleOutfitVibe") != coastal_decision.get("maleOutfitVibe")
    finally:
        server.shutdown()
        thread.join(timeout=1)
