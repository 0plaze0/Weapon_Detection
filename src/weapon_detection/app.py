"""Main application pipeline."""

from __future__ import annotations

import cv2

from weapon_detection.alerts import AlertManager
from weapon_detection.annotator import Annotator
from weapon_detection.camera import VideoStream
from weapon_detection.config import Settings
from weapon_detection.detector import YoloDetector
from weapon_detection.utils import FPSCounter


class DetectionApp:
    """Wires camera, detector, annotator, and alerting into a live loop."""

    def __init__(self, settings: Settings) -> None:
        """Args:
            settings: Runtime configuration.
        """
        self.settings = settings
        self.detector = YoloDetector(
            settings.custom_weights, settings.fallback_weights, settings.conf_threshold
        )
        self.annotator = Annotator()
        self.alerts = AlertManager(settings.alerts_dir, settings.cooldown_s)
        self.fps = FPSCounter()

    def run(self) -> None:
        """Runs the live loop until 'q' is pressed."""
        print("[INFO] Detection started. Press 'q' to quit.")
        try:
            with VideoStream(self.settings.camera_index) as stream:
                while True:
                    ok, frame = stream.read()
                    if not ok or frame is None:
                        print("[ERROR] Failed to read frame; exiting.")
                        break

                    detections = self.detector.detect(frame)
                    self.annotator.draw_all(frame, detections)
                    self.alerts.handle(frame, detections)
                    self.annotator.draw_hud(frame, self.fps.tick(), self.alerts.threat_count)

                    cv2.imshow(self.settings.window_name, frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted.")
        finally:
            print(f"[INFO] Shutdown. Total threats logged: {self.alerts.threat_count}")