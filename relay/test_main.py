import json
import os
import sqlite3
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from db import poll_once


@pytest.fixture
def db_path():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE rhdata ("
        "id INTEGER PRIMARY KEY, entry_type TEXT NOT NULL, "
        "payload TEXT NOT NULL, timestamp TIMESTAMP)"
    )
    conn.commit()
    conn.close()
    yield path
    os.unlink(path)


def insert(db_path, entry_type, payload):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO rhdata (entry_type, payload, timestamp) VALUES (?, ?, ?)",
        (entry_type, json.dumps(payload), "2026-05-05 00:00:00"),
    )
    conn.commit()
    conn.close()


def test_poll_once_emits_new_rows(db_path):
    snapshot_set = {"pilot_data", "heat_data"}
    captured: list[tuple[str, dict]] = []

    def emit(event, payload):
        captured.append((event, payload))

    insert(db_path, "pilot_data", {"pilots": [{"id": 1}]})
    insert(db_path, "heat_data", {"heats": []})

    last_max_id, last_data_version, emitted = poll_once(
        db_path, snapshot_set, 0, None, emit
    )

    assert emitted == 2
    assert ("pilot_data", {"pilots": [{"id": 1}]}) in captured
    assert ("heat_data", {"heats": []}) in captured
    assert last_max_id == 2

    # No new writes -> data_version unchanged -> nothing emitted.
    captured.clear()
    _, _, emitted2 = poll_once(
        db_path, snapshot_set, last_max_id, last_data_version, emit
    )
    assert emitted2 == 0
    assert captured == []


def test_poll_once_keeps_only_latest_per_type(db_path):
    snapshot_set = {"pilot_data"}
    captured: list[tuple[str, dict]] = []

    def emit(event, payload):
        captured.append((event, payload))

    insert(db_path, "pilot_data", {"pilots": [{"id": 1}]})
    insert(db_path, "pilot_data", {"pilots": [{"id": 1, "name": "alice"}]})

    _, _, emitted = poll_once(db_path, snapshot_set, 0, None, emit)
    assert emitted == 1
    assert captured == [("pilot_data", {"pilots": [{"id": 1, "name": "alice"}]})]


def test_poll_once_skips_non_snapshot_types(db_path):
    snapshot_set = {"pilot_data"}
    captured: list[tuple[str, dict]] = []

    def emit(event, payload):
        captured.append((event, payload))

    insert(db_path, "heartbeat", {"tick": 1})
    insert(db_path, "pilot_data", {"pilots": []})

    _, _, emitted = poll_once(db_path, snapshot_set, 0, None, emit)
    assert emitted == 1
    assert captured == [("pilot_data", {"pilots": []})]


# ----- Page-render and static-asset smoke tests -----

@pytest.fixture
def client(db_path):
    from main import create_app
    # Use threading mode for tests so the suite runs without gevent installed.
    app, _socketio, _state = create_app(db_path, [], async_mode="threading")
    app.config["TESTING"] = True
    return app.test_client()


PAGE_CASES = [
    ("/ddr_overlays/stream/results", b'id="header"'),
    ("/ddr_overlays/stream/bar", b'id="ddr_frame_topbar"'),
    ("/ddr_overlays/stream/leaderboard/ddr8de/1", b'id="ddr_leaderboard32"'),
    ("/ddr_overlays/stream/leaderboard_pages/ddr8de/1", b'id="ddr_leaderboard32"'),
    ("/ddr_overlays/stream/brackets/ddr8de/1", b'id="fai_brackets"'),
    ("/ddr_overlays/stream/last_heat/ddr8de/1", b'id="ddr_nextup"'),
    ("/ddr_overlays/stream/next_up/ddr8de/1", b'id="ddr_nextup"'),
    ("/ddr_overlays/stream/podium/ddr8de/1", b"Final Ranking"),
    ("/ddr_overlays/stream/node/1", b'id="ddr_node"'),
]


@pytest.mark.parametrize("url, marker", PAGE_CASES)
def test_overlay_page_renders(client, url, marker):
    resp = client.get(url)
    assert resp.status_code == 200, f"{url} returned {resp.status_code}"
    assert marker in resp.data, f"marker {marker!r} missing from {url}"


def test_node_route_rejects_out_of_range(client):
    resp = client.get("/ddr_overlays/stream/node/9")
    assert resp.status_code == 404


def test_static_assets_served(client):
    # Vendored RH static under /static/...
    resp = client.get("/static/rotorhazard.js")
    assert resp.status_code == 200
    assert b"rotorhazard" in resp.data

    # Plugin static under /ddr_overlays/static/...
    resp = client.get("/ddr_overlays/static/js/ddr_overlays.js")
    assert resp.status_code == 200
    assert b"default_handler" in resp.data
