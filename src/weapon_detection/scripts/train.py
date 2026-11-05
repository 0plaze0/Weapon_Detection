"""Trains a YOLO model and copies the best weights to weights/best.pt."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

from pathlib import Path

PRETRAINED_DIR = Path("weights/pretrained")
PRETRAINED_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    """Runs training and deploys the best checkpoint."""
    p = argparse.ArgumentParser(description="Train YOLO on a custom dataset")
    p.add_argument("--data", default="datasets/weapons/data.yaml")
    p.add_argument("--model", default="yolo11s.pt")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--device", default="0", help="GPU index, or 'cpu'")
    a = p.parse_args()

    model = YOLO(str(PRETRAINED_DIR / a.model))
    results = model.train(
        data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch,
        device=a.device, project="runs", name="weapons", exist_ok=True,
    )

    best = Path(results.save_dir) / "weights" / "best.pt"
    Path("weights").mkdir(exist_ok=True)
    shutil.copy(best, "weights/best.pt")
    print(f"[INFO] Copied {best} -> weights/best.pt")


if __name__ == "__main__":
    main()