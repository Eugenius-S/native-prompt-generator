import threading
import time

import requests


def start_server():
    # Importing app here to reuse PromptGeneratorHandler and ThreadingHTTPServer
    from app import PromptGeneratorHandler, ThreadingHTTPServer

    server = ThreadingHTTPServer(("127.0.0.1", 0), PromptGeneratorHandler)
    port = server.server_address[1]

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, port


def test_generate_endpoint_smoke():
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

        # Post a minimal generate request
        r = requests.post(
            f"http://127.0.0.1:{port}/api/generate",
            json={"formState": {"mode": "women", "batchSize": 1}},
            timeout=20,
        )
        assert r.status_code == 200
        body = r.json()
        assert "run" in body
    finally:
        server.shutdown()
        thread.join(timeout=1)
