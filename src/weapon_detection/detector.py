"""YOLO model loading and inference."""

from __future__ import annotations

from pathlib import Path
from typing import List

import cv2
from ultralytics import YOLO

from weapon_detection.models import Detection


class YoloDetector:
    """Wraps an Ultralytics YOLO model with custom-weights fallback."""

    def __init__(self, custom_weights: str, fallback_weights: str, conf_threshold: float) -> None:
        """Initializes the detector.

        Args:
            custom_weights: Path to custom-trained weights.
            fallback_weights: Weights used if the custom file is missing.
            conf_threshold: Minimum confidence to keep a detection.
        """
        self.conf_threshold = conf_threshold
        self.model = self._load(custom_weights, fallback_weights)

    @staticmethod
    def _load(custom: str, fallback: str) -> YOLO:
        """Loads custom weights, or falls back to a standard model."""
        if Path(custom).is_file():
            print(f"[INFO] Loaded custom model: {custom}")
            return YOLO(custom)
        print(
            f"[WARNING] '{custom}' not found. Falling back to '{fallback}' "
            "(generic COCO classes; for structure testing only)."
        )
        return YOLO(fallback)

    def detect(self, frame: cv2.Mat) -> List[Detection]:
        """Runs inference on a BGR frame.

        `box.xyxy` gives absolute pixel corners (x1, y1, x2, y2) in the input
        frame's coordinate system. They are cast to int because OpenCV drawing
        functions require integer pixels.

        Args:
            frame: BGR image array of shape (H, W, 3), dtype uint8.

        Returns:
            Detections above the confidence threshold.
        """
        result = self.model(frame, conf=self.conf_threshold, verbose=False)[0]
        detections: List[Detection] = []
        for box in result.boxes:
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0].tolist())
            detections.append(
                Detection(
                    box=(x1, y1, x2, y2),
                    class_name=str(self.model.names[int(box.cls[0])]),
                    confidence=float(box.conf[0]),
                )
            )
        return detections