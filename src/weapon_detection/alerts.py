"""Alert debouncing, logging, snapshot saving, and DB persistence."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import cv2

from weapon_detection.db import AlertDB
from weapon_detection.notifier import EmailNotifier
from weapon_detection.models import Detection


class AlertManager:
    """Logs alerts, saves annotated snapshots, and records them in SQLite."""

    def __init__(self, alerts_dir: str, cooldown_s: float, db: Optional[AlertDB] = None, notifier: Optional[EmailNotifier] = None) -> None:
        """Args:
            alerts_dir: Directory where snapshots are saved.
            cooldown_s: Minimum seconds between alerts.
            db: Optional database to record alerts in.
        """
        self.alerts_dir = Path(alerts_dir)
        self.notifier = notifier
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        self.cooldown_s = cooldown_s
        self.db = db
        self.threat_count = 0
        self._last_alert_ts = 0.0

    def handle(self, frame: cv2.Mat, detections: List[Detection]) -> None:
        """Logs, saves, and stores an alert if the cooldown has elapsed."""
        now = time.time()
        if not detections or now - self._last_alert_ts < self.cooldown_s:
            return
        self._last_alert_ts = now
        self.threat_count += len(detections)

        top = max(detections, key=lambda d: d.confidence)
        stamp = datetime.now()
        safe_cls = top.class_name.replace(" ", "_").upper()
        filename = f"alert_{safe_cls}_{stamp:%Y%m%d_%H%M%S}.jpg"
        path = self.alerts_dir / filename
        cv2.imwrite(str(path), frame)
        if self.db is not None:
            self.db.insert(stamp, top.class_name, top.confidence, top.box, filename)
        if self.notifier is not None:
            self.notifier.send_photo(
                path,
                f"ALERT: {top.class_name} ({top.confidence * 100:.0f}%)\n"
                f"{stamp:%Y-%m-%d %H:%M:%S}",
            )
        print(
            f"[ALERT] {stamp:%Y-%m-%d %H:%M:%S} | class={top.class_name} | "
            f"conf={top.confidence:.2f} | box={top.box} | saved={path}"
        )