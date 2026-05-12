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


def test_hair_and_breast_option_smoke():
    server, thread, port = start_server()
    try:
        # wait for server to be ready
        for _ in range(30):
            try:
                r = requests.get(f"http://127.0.0.1:{port}/api/bootstrap", timeout=2)
                if r.status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(0.1)

        assert r.status_code == 200

        data = r.json()
        options = data.get("options", {})
        breast_opts = options.get("breastSizeOptions", [])
        assert any(opt.get("value") == "small_breasts" for opt in breast_opts)

        payload = {
            "formState": {
                "mode": "women",
                "batchSize": 4,
                "breastSizeControl": "small_breasts",
                "hairstyle": "soft_waves",
                "hairLength": "short",
                "hairColorControl": "blonde",
            }
        }
        r = requests.post(f"http://127.0.0.1:{port}/api/generate", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "run" in body
        run = body["run"]
        assert run.get("formState", {}).get("breastSizeControl") == "small_breasts"
        assert "debug" in run
        assert len(run.get("prompts", [])) == 4
    finally:
        server.shutdown()
        thread.join(timeout=1)
