from __future__ import annotations

import os
from http.server import ThreadingHTTPServer

from backend.api.http_handler import PromptGeneratorHandler


def main() -> None:
    host = os.environ.get("PROMPT_GENERATOR_HOST", "127.0.0.1").strip() or "127.0.0.1"
    try:
        port = int(os.environ.get("PROMPT_GENERATOR_PORT", "8765"))
    except ValueError:
        port = 8765
    server = ThreadingHTTPServer((host, port), PromptGeneratorHandler)
    print(f"Prompt Generator Web UI: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
