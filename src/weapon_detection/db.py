"""SQLite storage for alerts."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    class_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    x1 INTEGER, y1 INTEGER, x2 INTEGER, y2 INTEGER,
    image TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_alerts_ts ON alerts(ts);
CREATE INDEX IF NOT EXISTS idx_alerts_class ON alerts(class_name);
"""


class AlertDB:
    """Thin SQLite wrapper. Opens a connection per call, so it is thread-safe."""

    def __init__(self, path: str = "alerts/alerts.db") -> None:
        """Args:
            path: SQLite file path.
        """
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def insert(self, ts: datetime, class_name: str, confidence: float,
               box: Tuple[int, int, int, int], image: str) -> None:
        """Stores one alert. `image` is the snapshot file name."""
        with self._conn() as c:
            c.execute(
                "INSERT INTO alerts (ts, class_name, confidence, x1, y1, x2, y2, image) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ts.isoformat(timespec="seconds"), class_name, confidence, *box, image),
            )

    def list(self, limit: int = 50, offset: int = 0,
             class_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns alerts, newest first."""
        sql, args = "SELECT * FROM alerts", []
        if class_name:
            sql += " WHERE class_name = ?"
            args.append(class_name)
        sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
        args += [limit, offset]
        with self._conn() as c:
            return [dict(r) for r in c.execute(sql, args)]

    def stats(self) -> Dict[str, Any]:
        """Aggregates for the dashboard."""
        today = datetime.now().strftime("%Y-%m-%d")
        with self._conn() as c:
            total = c.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
            today_n = c.execute(
                "SELECT COUNT(*) FROM alerts WHERE ts LIKE ?", (today + "%",)
            ).fetchone()[0]
            avg = c.execute("SELECT AVG(confidence) FROM alerts").fetchone()[0] or 0.0
            by_class = [dict(r) for r in c.execute(
                "SELECT class_name, COUNT(*) AS count FROM alerts "
                "GROUP BY class_name ORDER BY count DESC")]
            by_hour = [dict(r) for r in c.execute(
                "SELECT substr(ts, 1, 13) AS hour, COUNT(*) AS count FROM alerts "
                "GROUP BY hour ORDER BY hour DESC LIMIT 24")][::-1]
        return {"total": total, "today": today_n, "avg_conf": round(avg, 3),
                "by_class": by_class, "by_hour": by_hour}

    def delete(self, alert_id: int) -> Optional[str]:
        """Deletes a row and returns its image file name (or None)."""
        with self._conn() as c:
            row = c.execute("SELECT image FROM alerts WHERE id = ?", (alert_id,)).fetchone()
            c.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        return row["image"] if row else None