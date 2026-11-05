"""Frame annotation: boxes, labels, and HUD."""

from __future__ import annotations

from typing import Iterable

import cv2

from weapon_detection.models import Detection

RED = (0, 0, 255)  # BGR
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX


class Annotator:
    """Draws detections and HUD elements onto frames (in place)."""

    @staticmethod
    def draw_detection(frame: cv2.Mat, det: Detection) -> None:
        """Draws a red box and a solid label banner above it.

        The banner height is derived from the rendered text size. If the box
        touches the top edge, the banner is clamped to y=0 to stay visible.
        OpenCV draws directly on the NumPy array, so `frame` is mutated.

        Args:
            frame: BGR image to annotate.
            det: Detection to render.
        """
        x1, y1, x2, y2 = det.box
        cv2.rectangle(frame, (x1, y1), (x2, y2), RED, 2)

        label = f"ALERT: {det.class_name} ({det.confidence * 100:.0f}%)"
        (tw, th), baseline = cv2.getTextSize(label, FONT, 0.6, 2)
        top = max(y1 - th - baseline - 6, 0)
        cv2.rectangle(frame, (x1, top), (x1 + tw + 8, top + th + baseline + 6), RED, -1)
        cv2.putText(frame, label, (x1 + 4, top + th + 2), FONT, 0.6, WHITE, 2, cv2.LINE_AA)

    def draw_all(self, frame: cv2.Mat, detections: Iterable[Detection]) -> None:
        """Draws every detection onto the frame."""
        for det in detections:
            self.draw_detection(frame, det)

    @staticmethod
    def draw_hud(frame: cv2.Mat, fps: float, threat_count: int) -> None:
        """Draws the FPS counter (top-left) and status banner (bottom).

        Args:
            frame: BGR image to annotate.
            fps: Current frames per second.
            threat_count: Total threats logged so far.
        """
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 25), FONT, 0.7, GREEN, 2, cv2.LINE_AA)
        h, w = frame.shape[:2]
        text = f"SYSTEM STATUS: ACTIVE | THREATS DETECTED: {threat_count}"
        cv2.rectangle(frame, (0, h - 32), (w, h), BLACK, -1)
        cv2.putText(frame, text, (10, h - 10), FONT, 0.6, WHITE, 2, cv2.LINE_AA)