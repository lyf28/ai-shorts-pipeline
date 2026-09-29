from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class RunStore:
    """SQLite persistence for one durable record per pipeline invocation."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_at TEXT NOT NULL,
              idea TEXT, script TEXT, storyboard_json TEXT, prompts_json TEXT,
              generation_status TEXT NOT NULL, output_path TEXT, error_logs TEXT
            )
        """)
        self.connection.commit()

    def create(self) -> int:
        cursor = self.connection.execute(
            "INSERT INTO pipeline_runs(created_at, generation_status, error_logs) VALUES (?, ?, ?)",
            (datetime.now(UTC).isoformat(), "started", ""),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def update(self, run_id: int, **fields: Any) -> None:
        allowed = {"idea", "script", "storyboard_json", "prompts_json", "generation_status", "output_path", "error_logs"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(f"Unsupported database fields: {unknown}")
        serialized = {key: json.dumps(value, ensure_ascii=False) if key in {"storyboard_json", "prompts_json"} else value for key, value in fields.items()}
        assignments = ", ".join(f"{key} = ?" for key in serialized)
        self.connection.execute(f"UPDATE pipeline_runs SET {assignments} WHERE id = ?", (*serialized.values(), run_id))
        self.connection.commit()

    def get(self, run_id: int) -> dict[str, Any]:
        cursor = self.connection.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        if not row:
            raise KeyError(run_id)
        return dict(zip([column[0] for column in cursor.description], row))

    def close(self) -> None:
        self.connection.close()
