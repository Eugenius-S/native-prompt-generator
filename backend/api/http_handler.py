from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from backend.prompt_service import generate_run
from backend.services.bootstrap_service import get_bootstrap
from backend.services.preset_service import delete_preset_record, save_preset_record


ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_ROOT = FRONTEND_DIR.resolve()


class PromptGeneratorHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def _json_response(self, payload: object, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError):
            return

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = path.read_bytes()
        content_type, _ = mimetypes.guess_type(path.name)
        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", f"{content_type or 'application/octet-stream'}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError):
            return

    def _frontend_path(self, relative_path: str) -> Path | None:
        candidate = (FRONTEND_DIR / relative_path).resolve()
        if candidate == FRONTEND_ROOT or FRONTEND_ROOT in candidate.parents:
            return candidate
        return None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._serve_file(FRONTEND_DIR / "index.html")
            return
        if parsed.path.startswith("/static/"):
            candidate = self._frontend_path(parsed.path.removeprefix("/static/"))
            if candidate is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._serve_file(candidate)
            return
        if parsed.path == "/api/bootstrap":
            self._json_response(get_bootstrap())
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed.path == "/api/generate":
                self._json_response({"run": generate_run(payload.get("formState"))})
                return
            if parsed.path == "/api/presets":
                record = save_preset_record(payload.get("name", ""), payload.get("formState") or {})
                self._json_response({"preset": record})
                return
            self.send_error(HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._json_response({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._json_response({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/presets":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            query = parse_qs(parsed.query)
            delete_preset_record((query.get("id") or [""])[0])
            self._json_response({"ok": True})
        except ValueError as exc:
            self._json_response({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._json_response({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
