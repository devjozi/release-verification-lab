#!/usr/bin/env python3
"""Minimal service used as the deployable target for release verification."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


def health_payload() -> dict[str, Any]:
    """Return the runtime contract used by the smoke verifier."""
    return {"status": "ok", "service": "release-verification-lab"}


class Handler(BaseHTTPRequestHandler):
    """Expose the small HTTP surface used by the release gate."""

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/healthz":
            self._json(200, health_payload())
            return
        self._json(404, {"status": "not_found"})

    def log_message(self, format: str, *args: object) -> None:
        """Keep CI output compact while preserving request visibility."""
        print(format % args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), Handler)
    print(f"serving on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
