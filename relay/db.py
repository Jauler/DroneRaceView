"""SQLite read helpers for the relay. No flask dependency — keeps tests light."""

import json
import sqlite3


DEFAULT_SNAPSHOT_TYPES = [
    "pilot_data",
    "heat_data",
    "class_data",
    "result_data",
    "race_status",
    "leaderboard",
    "current_heat",
    "current_laps",
    "language",
    "all_languages",
]


def parse_db_path(db_url: str) -> str:
    """Translate a SQLAlchemy-style sqlite URL into a filesystem path for sqlite3."""
    if db_url.startswith("sqlite:////"):
        return "/" + db_url[len("sqlite:////"):]
    if db_url.startswith("sqlite:///"):
        return db_url[len("sqlite:///"):]
    return db_url


def latest_payload_for_type(db_path: str, entry_type: str):
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT payload FROM rhdata WHERE entry_type = ? ORDER BY id DESC LIMIT 1",
            (entry_type,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return json.loads(row[0])


def initial_max_id(db_path: str) -> int:
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute("SELECT COALESCE(MAX(id), 0) FROM rhdata").fetchone()
            return row[0] if row else 0
    except sqlite3.OperationalError:
        return 0


def poll_once(db_path: str, snapshot_set: set, last_max_id: int, last_data_version,
              emit) -> tuple[int, int | None, int]:
    """Run one polling cycle. Returns (new_last_max_id, new_last_data_version, emitted_count).

    last_data_version is accepted/returned for API stability with earlier callers
    but is no longer consulted — running the SELECT every cycle is cheap and avoids
    cross-process data_version caching surprises.
    """
    if not snapshot_set:
        return last_max_id, last_data_version, 0

    with sqlite3.connect(db_path) as conn:
        placeholders = ",".join("?" * len(snapshot_set))
        cur = conn.execute(
            f"SELECT id, entry_type, payload FROM rhdata "
            f"WHERE id > ? AND entry_type IN ({placeholders}) "
            f"ORDER BY id",
            (last_max_id, *tuple(snapshot_set)),
        )

        latest_per_type: dict[str, str] = {}
        max_seen = last_max_id
        for row_id, entry_type, payload in cur:
            latest_per_type[entry_type] = payload
            if row_id > max_seen:
                max_seen = row_id

        emitted = 0
        for entry_type, payload in latest_per_type.items():
            emit(entry_type, json.loads(payload))
            emitted += 1

        return max_seen, last_data_version, emitted
