"""CLI entry point: `uv run weapon-detect` or `python -m weapon_detection`."""

from __future__ import annotations

import argparse

from weapon_detection.app import DetectionApp
from weapon_detection.config import Settings


def main() -> None:
    """Parses CLI args and starts the app."""
    d = Settings()
    p = argparse.ArgumentParser(description="Real-time weapon detection")
    p.add_argument("--weights", default=d.custom_weights)
    p.add_argument("--fallback", default=d.fallback_weights)
    p.add_argument("--conf", type=float, default=d.conf_threshold)
    p.add_argument("--cooldown", type=float, default=d.cooldown_s)
    p.add_argument("--alerts-dir", default=d.alerts_dir)
    p.add_argument("--camera", type=int, default=d.camera_index)
    a = p.parse_args()

    settings = Settings(
        custom_weights=a.weights,
        fallback_weights=a.fallback,
        conf_threshold=a.conf,
        cooldown_s=a.cooldown,
        alerts_dir=a.alerts_dir,
        camera_index=a.camera,
    )
    DetectionApp(settings).run()


if __name__ == "__main__":
    main()