"""Read-only Socket.IO relay backed by collector's SQLite DB."""

import argparse
import logging
import os
import sqlite3

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

from db import (
    DEFAULT_SNAPSHOT_TYPES,
    initial_max_id,
    latest_payload_for_type,
    parse_db_path,
    poll_once,
)

logger = logging.getLogger("relay")


def create_app(db_path: str, snapshot_types: list[str]):
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")

    snapshot_set = set(snapshot_types)
    state = {"poller_alive": False}

    @app.get("/healthz")
    def healthz():
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("SELECT 1").fetchone()
        except Exception as e:
            return jsonify({"ok": False, "db_error": str(e)}), 500
        if not state["poller_alive"]:
            return jsonify({"ok": False, "poller": "not_running"}), 500
        return jsonify({"ok": True}), 200

    def _kick_load_all(sid):
        # Give the client time to register its load_all handler in
        # $(document).ready before we tell it to ask for its data_dependencies.
        socketio.sleep(1.0)
        socketio.emit("load_all", to=sid)
        logger.info(f"emit load_all -> sid={sid}")

    @socketio.on("connect")
    def on_connect():
        sid = request.sid
        logger.info(f"Client connected: sid={sid}")
        socketio.start_background_task(_kick_load_all, sid)

    @socketio.on("disconnect")
    def on_disconnect():
        logger.info(f"Client disconnected: sid={request.sid}")

    @socketio.on("load_data")
    def on_load_data(data):
        sid = request.sid
        if not isinstance(data, dict):
            logger.debug(f"load_data: ignoring non-dict payload from sid={sid}")
            return
        load_types = data.get("load_types")
        if isinstance(load_types, str):
            load_types = [load_types]
        if not isinstance(load_types, list):
            logger.debug(f"load_data: load_types missing or invalid from sid={sid}")
            return
        for t in load_types:
            if t not in snapshot_set:
                logger.debug(f"load_data: skipping non-snapshot type {t!r}")
                continue
            try:
                payload = latest_payload_for_type(db_path, t)
            except Exception:
                logger.exception(f"load_data: failed to read latest {t!r}")
                continue
            if payload is None:
                logger.info(f"load_data: no row for {t!r} (sid={sid})")
                continue
            emit(t, payload)
            logger.info(f"emit {t!r} -> sid={sid} (load_data response)")

    return app, socketio, state


def run_poller(socketio, db_path: str, snapshot_types: list[str], interval_ms: int, state: dict):
    """Poll PRAGMA data_version, broadcast new rows. Designed to run as a background task."""
    snapshot_set = set(snapshot_types)
    interval_s = interval_ms / 1000.0

    if not snapshot_set:
        logger.warning("poller: snapshot type list is empty; nothing will be broadcast")

    last_data_version = None
    last_max_id = initial_max_id(db_path)

    state["poller_alive"] = True
    logger.info(f"poller: started, last_max_id={last_max_id}, interval={interval_ms}ms")

    def emit_broadcast(entry_type, payload):
        try:
            socketio.emit(entry_type, payload)
            logger.info(f"emit {entry_type!r} -> all (poller broadcast)")
        except Exception:
            logger.exception(f"poller: broadcast {entry_type!r} failed")

    while True:
        try:
            last_max_id, last_data_version, _ = poll_once(
                db_path, snapshot_set, last_max_id, last_data_version, emit_broadcast
            )
        except Exception:
            logger.exception("poller: cycle failed; continuing")

        socketio.sleep(interval_s)


def main():
    parser = argparse.ArgumentParser(description="DroneRaceView Socket.IO relay (read-only)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--db-url", default=os.getenv("DATABASE_URL", "sqlite:///data.db"))
    parser.add_argument("--poll-interval-ms", type=int, default=1000)
    parser.add_argument("--snapshot-types", default=",".join(DEFAULT_SNAPSHOT_TYPES))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

    db_path = parse_db_path(args.db_url)
    snapshot_types = [t.strip() for t in args.snapshot_types.split(",") if t.strip()]

    app, socketio, state = create_app(db_path, snapshot_types)

    socketio.start_background_task(
        run_poller, socketio, db_path, snapshot_types, args.poll_interval_ms, state
    )

    logger.info(f"Listening on {args.host}:{args.port}, db={db_path}, "
                f"poll={args.poll_interval_ms}ms, types={snapshot_types}")
    socketio.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
