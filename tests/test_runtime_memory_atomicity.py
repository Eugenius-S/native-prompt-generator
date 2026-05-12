import threading

from backend.engine import generator


def test_runtime_memory_stays_readable_under_parallel_access(tmp_path, monkeypatch):
    memory_path = tmp_path / "memory.json"
    monkeypatch.setattr(generator, "MEMORY_PATH", memory_path)
    generator._save_memory({"schema_version": 1, "items": []})

    barrier = threading.Barrier(5)
    failures: list[Exception] = []
    failure_lock = threading.Lock()

    def record_failure(error: Exception):
        with failure_lock:
            failures.append(error)

    def writer(prefix: str):
        try:
            barrier.wait()
            for index in range(200):
                generator._save_memory(
                    {
                        "schema_version": 1,
                        "items": [f"{prefix}_{index}"],
                    },
                )
        except Exception as error:  # pragma: no cover - test captures unexpected failures.
            record_failure(error)

    def reader():
        try:
            barrier.wait()
            for _ in range(300):
                payload = generator._load_runtime_memory()
                assert payload["schema_version"] == 1
                assert isinstance(payload["items"], list)
        except Exception as error:  # pragma: no cover - test captures unexpected failures.
            record_failure(error)

    threads = [
        threading.Thread(target=writer, args=("alpha",), daemon=True),
        threading.Thread(target=writer, args=("beta",), daemon=True),
        threading.Thread(target=reader, daemon=True),
        threading.Thread(target=reader, daemon=True),
    ]

    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join(timeout=10)
        assert not thread.is_alive()

    assert not failures
    payload = generator._load_runtime_memory()
    assert payload["schema_version"] == 1
    assert isinstance(payload["items"], list)