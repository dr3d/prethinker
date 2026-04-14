from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from gateway.config import ConfigStore
from gateway.phases import process_turn
from gateway.runtime_hooks import RuntimeHooks
from gateway.session_store import SessionStore


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
STATE_DIR = ROOT / "state"

config_store = ConfigStore(STATE_DIR / "gateway_config.json")
session_store = SessionStore()
runtime_hooks = RuntimeHooks()


class GatewayHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json(
                {
                    "status": "ok",
                    "service": "prethink-gateway-mvp",
                    "front_door_uri": config_store.get().front_door_uri,
                }
            )
            return
        if parsed.path == "/api/config":
            self._send_json({"status": "ok", "config": config_store.get().to_dict()})
            return
        if parsed.path == "/api/session/reset":
            session_id = self.headers.get("X-Session-Id")
            state = session_store.reset(session_id)
            self._send_json({"status": "ok", "session_id": state.session_id, "turns": []})
            return
        if parsed.path == "/api/session/state":
            session_id = self._resolve_session_id(parsed)
            if not session_id:
                self._send_json(
                    {"status": "error", "error": "session_id is required (query or X-Session-Id header)."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            snapshot = session_store.snapshot(session_id)
            if snapshot is None:
                self._send_json(
                    {"status": "error", "error": f"session not found: {session_id}"},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            self._send_json({"status": "ok", "session": snapshot})
            return
        return super().do_GET()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        payload = self._read_json()
        if parsed.path == "/api/config":
            updated = config_store.update(payload)
            self._send_json({"status": "ok", "config": updated.to_dict()})
            return
        if parsed.path == "/api/prethink":
            utterance = str(payload.get("utterance", "")).strip()
            if not utterance:
                self._send_json({"status": "error", "error": "utterance is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            session = session_store.get_or_create(payload.get("session_id"))
            response = process_turn(
                utterance=utterance,
                session=session,
                config=config_store.get().to_dict(),
                runtime=runtime_hooks,
                config_store=config_store,
            )
            self._send_json(response)
            return
        self._send_json({"status": "error", "error": f"Unknown endpoint: {parsed.path}"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        print(f"[ui_gateway] {self.address_string()} - {format % args}")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Session-Id")
        super().end_headers()

    def _resolve_session_id(self, parsed) -> str:
        query = parse_qs(parsed.query or "")
        from_query = ""
        if "session_id" in query and query["session_id"]:
            from_query = str(query["session_id"][0]).strip()
        if from_query:
            return from_query
        return str(self.headers.get("X-Session-Id", "")).strip()

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def run() -> None:
    parser = argparse.ArgumentParser(description="Run the isolated Prethink gateway MVP.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Port to serve.")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), GatewayHandler)
    print(f"Serving ui_gateway on http://{args.host}:{args.port}")
    print(f"Static assets: {STATIC_DIR}")
    print(f"Config file: {STATE_DIR / 'gateway_config.json'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down ui_gateway.")
    finally:
        server.server_close()
