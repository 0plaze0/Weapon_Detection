"""Application settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime configuration.

    Attributes:
        custom_weights: Path to custom-trained weights.
        fallback_weights: Pretrained weights used if custom weights are missing.
        conf_threshold: Minimum confidence to accept a detection (0-1).
        cooldown_s: Minimum seconds between saved alerts.
        alerts_dir: Directory for annotated alert snapshots.
        camera_index: OpenCV camera index.
        window_name: Title of the display window.
    """

    custom_weights: str = "weights/best.pt"
    fallback_weights: str = "weights/pretrained/yolo11n.pt"
    conf_threshold: float = 0.60
    cooldown_s: float = 3.0
    alerts_dir: str = "alerts"
    camera_index: int = 0
    window_name: str = "Weapon Detection System"