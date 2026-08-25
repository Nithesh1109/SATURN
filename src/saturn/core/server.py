"""Local HTTP server for the SATURN core."""

from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .api import CoreAPI


class CoreRequestHandler(BaseHTTPRequestHandler):
    api = CoreAPI()
    max_body_bytes = 64 * 1024

    def _read_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError:
            return {}
        if length <= 0 or length > self.max_body_bytes:
            return {}
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _authorized(self) -> bool:
        """Require a bearer token when SATURN_API_TOKEN is configured.

        Development remains convenient when the variable is absent, while a
        deployed Core can be locked down without changing client code.
        """
        expected = os.getenv("SATURN_API_TOKEN", "").strip()
        if not expected:
            return True
        authorization = self.headers.get("Authorization", "")
        scheme, _, supplied = authorization.partition(" ")
        return scheme.lower() == "bearer" and bool(supplied) and hmac.compare_digest(
            supplied.strip(), expected
        )

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(200, self.api.health())
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if not self._authorized():
            self._send_json(401, {"error": "unauthorized"})
            return

        if self.path == "/core/start":
            self._send_json(200, self.api.start())
            return
        if self.path == "/core/stop":
            self._send_json(200, self.api.stop())
            return
        if self.path == "/agent/run":
            payload = self._read_json()
            if not payload and self.headers.get("Content-Length", "0") not in {"0", ""}:
                self._send_json(400, {"error": "invalid_json_or_body_too_large"})
                return
            goal = str(payload.get("goal", "")).strip()
            if not goal:
                self._send_json(400, {"error": "goal_required"})
                return
            self._send_json(200, self.api.run_task(goal))
            return
        self._send_json(404, {"error": "not_found"})

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the local SATURN core API server."""
    server = ThreadingHTTPServer((host, port), CoreRequestHandler)
    print(f"SATURN Core API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    serve()
