"""Small helpers."""

from __future__ import annotations

import time


class FPSCounter:
    """Exponentially smoothed FPS estimator."""

    def __init__(self, smoothing: float = 0.9) -> None:
        """Args:
            smoothing: Weight of the previous estimate (0-1).
        """
        self.smoothing = smoothing
        self.fps = 0.0
        self._prev = time.time()

    def tick(self) -> float:
        """Updates and returns the smoothed FPS."""
        now = time.time()
        inst = 1.0 / max(now - self._prev, 1e-6)
        self._prev = now
        self.fps = self.smoothing * self.fps + (1 - self.smoothing) * inst
        return self.fps