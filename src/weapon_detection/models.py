"""Data models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

BoundingBox = Tuple[int, int, int, int]  # (x1, y1, x2, y2) in pixels


@dataclass(frozen=True)
class Detection:
    """A single detected object.

    Attributes:
        box: Pixel coordinates (x1, y1, x2, y2): top-left and bottom-right corners.
        class_name: Human-readable class label.
        confidence: Confidence score in [0, 1].
    """

    box: BoundingBox
    class_name: str
    confidence: float