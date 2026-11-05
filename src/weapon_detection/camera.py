"""Webcam stream handling."""

from __future__ import annotations

from types import TracebackType
from typing import Optional, Tuple, Type

import cv2 


class VideoStream:
    """Context manager around `cv2.VideoCapture`."""

    def __init__(self, index: int = 0) -> None:
        """Args:
            index: OpenCV camera index.
        """
        self.index = index
        self._cap: Optional[cv2.VideoCapture] = None

    def __enter__(self) -> "VideoStream":
        self._cap = cv2.VideoCapture(self.index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {self.index}")
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if self._cap is not None:
            self._cap.release()
        cv2.destroyAllWindows()

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Reads one BGR frame. Returns (success, frame)."""
        assert self._cap is not None, "Use VideoStream as a context manager."
        return self._cap.read()