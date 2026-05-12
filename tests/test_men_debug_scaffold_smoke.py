import threading
import time

import pytest
import requests


GROOMING_VALUES = {"clean-shaven", "light stubble", "trimmed beard"}


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


@pytest.mark.parametrize("style_mode", ["random", "romantic"])
def test_men_debug_uses_male_scaffold_fields(style_mode: str):
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
                "styleMode": style_mode,
                "spicyLevel": "3",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        decisions = run["debug"]["promptDecisions"]
        assert decisions

        for decision in decisions:
            assert decision.get("maleOutfit")
            assert decision.get("malePose")
            assert decision.get("maleHair")
            assert decision.get("maleGrooming") in GROOMING_VALUES

            assert decision.get("outfit") == decision.get("maleOutfit")
            assert decision.get("pose") == decision.get("malePose")
            assert decision.get("hair") == decision.get("maleHair")
            assert decision.get("makeup", "") == ""
            assert not decision.get("femaleOutfit")
    finally:
        server.shutdown()
        thread.join(timeout=1)
