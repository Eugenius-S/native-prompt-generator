import threading
import time
import re

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


def test_couples_different_persons_hardens_exact_female_age_and_race():
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
                "age": "25-30",
                "racePreset": "white_ukrainian",
                "maleAge": "30+",
                "maleRacePreset": "black_nigerian",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            debug = item["debugMeta"]
            assert candidate["age_band_id"] == "mid_20s"
            assert candidate["ethnicity_id"] == "white_ukrainian"
            assert "25-year-old Ukrainian woman" in item["prompt"]
            assert "Black Nigerian man" in item["prompt"]
            assert debug["maleEthnicityId"] == "black_nigerian"
            male_age_match = re.search(r"(\d{2})", debug["maleAge"])
            assert male_age_match is not None
            assert int(male_age_match.group(1)) >= 30
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_couples_different_persons_hardens_group_race_presets_for_female_side():
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
                "age": "25-30",
                "racePreset": "mostly_latina",
                "maleAge": "25-30",
                "maleRacePreset": "mostly_blacks",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        for item in run["prompts"]:
            candidate = item["candidate"]
            debug = item["debugMeta"]
            assert candidate["age_band_id"] == "mid_20s"
            assert candidate["ethnicity_group"] == "latina"
            assert "25-year-old" in item["prompt"]
            assert "Latina woman" in item["prompt"]
            assert debug["maleEthnicityGroup"] == "black"
            male_age_match = re.search(r"(\d{2})", debug["maleAge"])
            assert male_age_match is not None
            assert 25 <= int(male_age_match.group(1)) <= 30
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_couples_different_persons_keeps_explicit_male_constraints_across_runs():
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
                "age": "25-30",
                "racePreset": "white_ukrainian",
                "maleAge": "30+",
                "maleRacePreset": "black_nigerian",
            }
        }

        for _ in range(3):
            response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
            assert response.status_code == 200

            run = response.json()["run"]
            for item in run["prompts"]:
                debug = item["debugMeta"]
                assert "Black Nigerian man" in item["prompt"]
                assert debug["maleEthnicityId"] == "black_nigerian"
                male_age_match = re.search(r"(\d{2})", debug["maleAge"])
                assert male_age_match is not None
                assert int(male_age_match.group(1)) >= 30
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_couples_different_persons_supports_male_age_18():
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
                "age": "18",
                "maleAge": "18",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        for item in run["prompts"]:
            debug = item["debugMeta"]
            assert debug["maleAge"].startswith("18")
            assert "18-year-old" in item["prompt"]
    finally:
        server.shutdown()
        thread.join(timeout=1)
