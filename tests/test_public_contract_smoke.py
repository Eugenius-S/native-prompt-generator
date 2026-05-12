import json
import threading
import time

import requests

from backend import prompt_service, storage


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


def test_bootstrap_payload_top_level_keys_are_stable() -> None:
    server, thread, port = start_server()
    try:
        bootstrap = wait_bootstrap(port)
        assert bootstrap is not None
        assert bootstrap.status_code == 200

        assert set(bootstrap.json()) == {
            "defaults",
            "options",
            "enabledFields",
            "disabledFields",
            "presets",
            "history",
        }
    finally:
        server.shutdown()
        thread.join(timeout=1)


def test_generate_run_payload_top_level_keys_are_stable(monkeypatch) -> None:
    def _fake_append_history(payload):
        return {"id": "history-fixed", **payload}

    monkeypatch.setattr(prompt_service, "append_history", _fake_append_history)

    run = prompt_service.generate_run({"mode": "women", "batchSize": 1, "debugMode": True})

    assert set(run) == {"id", "timestamp", "formState", "outputText", "prompts", "debug"}


def test_history_and_presets_serialize_as_lists_of_dicts_with_current_keys(tmp_path, monkeypatch) -> None:
    history_path = tmp_path / "history.json"
    presets_path = tmp_path / "presets.json"
    monkeypatch.setattr(storage, "HISTORY_PATH", history_path)
    monkeypatch.setattr(storage, "PRESETS_PATH", presets_path)

    saved_history = storage.append_history(
        {
            "timestamp": "2026-04-21T00:00:00",
            "formState": {"mode": "women", "batchSize": 1},
            "outputText": "demo prompt",
            "prompts": [],
            "debug": {},
        }
    )
    saved_preset = storage.save_preset("Contract freeze", {"mode": "women", "batchSize": 1})

    history_items = storage.list_history()
    preset_items = storage.list_presets()
    raw_history = json.loads(history_path.read_text(encoding="utf-8"))
    raw_presets = json.loads(presets_path.read_text(encoding="utf-8"))

    assert isinstance(history_items, list)
    assert isinstance(preset_items, list)
    assert history_items and all(isinstance(item, dict) for item in history_items)
    assert preset_items and all(isinstance(item, dict) for item in preset_items)
    assert isinstance(raw_history, list)
    assert isinstance(raw_presets, list)
    assert set(saved_history) == {"id", "timestamp", "formState", "outputText", "prompts", "debug"}
    assert set(history_items[0]) == {"id", "timestamp", "formState", "outputText", "prompts", "debug"}
    assert set(saved_preset) == {"id", "name", "formState"}
    assert set(preset_items[0]) == {"id", "name", "formState"}
