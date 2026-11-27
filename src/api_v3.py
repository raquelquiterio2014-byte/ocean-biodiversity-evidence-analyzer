"""Localhost-only prototype HTTP JSON API, standard library; no device connectivity."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from src.sensors_v3 import validate_observation, checksum

DB = Path(__file__).resolve().parents[1] / "data" / "v3_synthetic.sqlite3"

def init_db(path=DB):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as con, con:
        con.execute("""CREATE TABLE IF NOT EXISTS synthetic_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload_sha256 TEXT NOT NULL UNIQUE,
            received_at_utc TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )""")
    return path

def store_observation(obs, path=DB):
    obs = validate_observation(obs)
    digest = checksum(obs)
    path = init_db(path)
    with closing(sqlite3.connect(path)) as con, con:
        cur = con.execute("INSERT OR IGNORE INTO synthetic_observations (payload_sha256, received_at_utc, payload_json) VALUES (?, ?, ?)",
            (digest, datetime.now(timezone.utc).isoformat(), json.dumps(obs, sort_keys=True)))
        inserted = cur.rowcount == 1
    return {"sha256": digest, "stored": inserted, "source_type": "synthetic_simulator"}

def recent_observations(path=DB, limit=100):
    if type(limit) is not int or not 1 <= limit <= 500:
        raise ValueError("Invalid limit")
    path = init_db(path)
    with closing(sqlite3.connect(path)) as con, con:
        rows = con.execute("SELECT payload_json FROM synthetic_observations ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [json.loads(row[0]) for row in rows]

class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/health":
            return self.respond(200, {"status": "ok", "mode": "synthetic_only"})
        if route == "/observations":
            return self.respond(200, {"source_type": "synthetic_simulator", "records": recent_observations()})
        self.respond(404, {"error": "not_found"})

    def do_POST(self):
        if urlparse(self.path).path != "/observations":
            return self.respond(404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384:
                raise ValueError("Payload must be 1..16384 bytes")
            obj = json.loads(self.rfile.read(length))
            result = store_observation(obj)
            self.respond(201 if result["stored"] else 200, result)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self.respond(400, {"error": "invalid_observation", "detail": str(exc)})

def main():
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8766), Handler)
    print("V3 synthetic-only HTTP API: http://127.0.0.1:8766")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    main()
