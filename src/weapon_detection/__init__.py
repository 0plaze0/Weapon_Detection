"""Real-time weapon detection package."""

from weapon_detection.app import DetectionApp
from weapon_detection.config import Settings
from weapon_detection.models import Detection

__all__ = ["DetectionApp", "Settings", "Detection"]
__version__ = "0.1.0"