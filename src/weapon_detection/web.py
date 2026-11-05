"""FastAPI server: receives browser webcam frames over WebSocket, returns detections."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any, Dict

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Any, Dict, List, Optional

from weapon_detection.db import AlertDB

from weapon_detection.alerts import AlertManager
from weapon_detection.annotator import Annotator
from weapon_detection.config import Settings
from weapon_detection.detector import YoloDetector
from weapon_detection.utils import FPSCounter
from weapon_detection.notifier import EmailNotifier

from dotenv import load_dotenv



STATIC_DIR = Path(__file__).parent / "static"


class FrameProcessor:
    """Decodes JPEG bytes, runs detection, and handles alerts."""

    def __init__(self, settings: Settings, db: AlertDB, notifier: EmailNotifier) -> None:
        """Args:
            settings: Runtime configuration.
            db: Alert database.
            notifier: Email notifier.
        """
        self.detector = YoloDetector(
            settings.custom_weights, settings.fallback_weights, settings.conf_threshold
        )
        self.annotator = Annotator()
        self.alerts = AlertManager(settings.alerts_dir, settings.cooldown_s, db, notifier)
        self.fps = FPSCounter()

    def process(self, data: bytes) -> Dict[str, Any]:
        """Runs the pipeline on one JPEG-encoded frame.

        `np.frombuffer` wraps the bytes without copying; `cv2.imdecode`
        converts them to a BGR (H, W, 3) uint8 array.

        Args:
            data: JPEG bytes from the browser.

        Returns:
            JSON-serializable dict with detections and stats.
        """
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return {"detections": [], "threats": self.alerts.threat_count, "fps": 0.0}

        detections = self.detector.detect(frame)
        if detections:
            self.annotator.draw_all(frame, detections)  # annotated copy is saved as snapshot
            self.alerts.handle(frame, detections)
        return {
            "detections": [
                {"box": d.box, "label": d.class_name, "conf": round(d.confidence, 3)}
                for d in detections
            ],
            "threats": self.alerts.threat_count,
            "fps": round(self.fps.tick(), 1),
        }


def create_app(settings: Settings) -> FastAPI:
    """Builds the FastAPI app.

    Args:
        settings: Runtime configuration.
    """
    app = FastAPI(title="Weapon Detection")
    db = AlertDB(f"{settings.alerts_dir}/alerts.db")
    load_dotenv()
    notifier = EmailNotifier.from_env()
    processor = FrameProcessor(settings, db, notifier)
    app.mount("/alert-images", StaticFiles(directory=settings.alerts_dir), name="alert-images")

    @app.get("/dashboard")
    async def dashboard() -> FileResponse:
        return FileResponse(STATIC_DIR / "dashboard.html")

    @app.get("/api/alerts")
    async def api_alerts(limit: int = 50, offset: int = 0,
                         class_name: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.list(min(limit, 200), offset, class_name)

    @app.get("/api/stats")
    async def api_stats() -> Dict[str, Any]:
        return db.stats()

    @app.delete("/api/alerts/{alert_id}")
    async def api_delete(alert_id: int) -> Dict[str, bool]:
        image = db.delete(alert_id)
        if image is None:
            raise HTTPException(404, "Alert not found")
        (Path(settings.alerts_dir) / image).unlink(missing_ok=True)
        return {"ok": True}
    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket) -> None:
        await ws.accept()
        try:
            while True:
                data = await ws.receive_bytes()
                result = await asyncio.to_thread(processor.process, data)
                await ws.send_json(result)
        except WebSocketDisconnect:
            pass

    return app


def main() -> None:
    """CLI entry point: `uv run weapon-serve`."""
    d = Settings()
    p = argparse.ArgumentParser(description="Weapon detection web server")
    p.add_argument("--weights", default=d.custom_weights)
    p.add_argument("--fallback", default=d.fallback_weights)
    p.add_argument("--conf", type=float, default=d.conf_threshold)
    p.add_argument("--cooldown", type=float, default=d.cooldown_s)
    p.add_argument("--alerts-dir", default=d.alerts_dir)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    a = p.parse_args()

    settings = Settings(
        custom_weights=a.weights,
        fallback_weights=a.fallback,
        conf_threshold=a.conf,
        cooldown_s=a.cooldown,
        alerts_dir=a.alerts_dir,
    )
    uvicorn.run(create_app(settings), host=a.host, port=a.port)


if __name__ == "__main__":
    main()