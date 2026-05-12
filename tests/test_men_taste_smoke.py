import threading
import time
from collections import Counter

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


def test_men_romantic_pose_spread_is_broader():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "men",
                "batchSize": 20,
                "debugMode": True,
                "styleMode": "romantic",
                "spicyLevel": "3",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        poses = Counter(item["debugMeta"]["malePose"] for item in run["prompts"])
        assert len(poses) >= 7
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_men_random_outfit_spread_is_less_luxury_heavy():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        payload = {
            "formState": {
                "mode": "men",
                "batchSize": 20,
                "debugMode": True,
                "styleMode": "random",
                "spicyLevel": "5",
            }
        }
        response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert response.status_code == 200

        run = response.json()["run"]
        outfits = Counter(item["debugMeta"]["maleOutfit"] for item in run["prompts"])
        assert len(outfits) >= 5
        assert outfits.most_common(1)[0][1] <= 7
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_men_romantic_outfit_spread_avoids_two_template_collapse():
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        aggregate = Counter()
        for _ in range(3):
            payload = {
                "formState": {
                    "mode": "men",
                    "batchSize": 18,
                    "debugMode": True,
                    "styleMode": "romantic",
                    "spicyLevel": "3",
                }
            }
            response = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
            assert response.status_code == 200
            run = response.json()["run"]
            aggregate.update(item["debugMeta"]["maleOutfit"] for item in run["prompts"])

        assert len(aggregate) >= 8
        assert aggregate.most_common(1)[0][1] <= 14
    finally:
        server.shutdown()
        thread.join(timeout=1)
