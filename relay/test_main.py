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
