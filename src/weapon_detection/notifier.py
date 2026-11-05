"""Email notifications via SMTP."""

from __future__ import annotations

import os
import smtplib
import threading
from email.message import EmailMessage
from pathlib import Path
from typing import Optional


class EmailNotifier:
    """Sends alert emails with the snapshot attached, off the main thread."""

    def __init__(
        self,
        host: Optional[str],
        port: int,
        user: Optional[str],
        password: Optional[str],
        to: Optional[str],
    ) -> None:
        """Args:
            host: SMTP server host.
            port: SMTP SSL port (465).
            user: SMTP login (sender address).
            password: SMTP password or app password.
            to: Recipient address.
        """
        self.host, self.port = host, port
        self.user, self.password, self.to = user, password, to
        self.enabled = all([host, user, password, to])
        if not self.enabled:
            print("[WARNING] Email disabled: set SMTP_* and ALERT_EMAIL_TO in .env.")

    @classmethod
    def from_env(cls) -> "EmailNotifier":
        """Builds a notifier from environment variables."""
        return cls(
            os.getenv("SMTP_HOST"),
            int(os.getenv("SMTP_PORT", "465")),
            os.getenv("SMTP_USER"),
            os.getenv("SMTP_PASSWORD"),
            os.getenv("ALERT_EMAIL_TO"),
        )

    def send_photo(self, image_path: Path, caption: str) -> None:
        """Queues an email with the snapshot (non-blocking)."""
        print(f"[DEBUG] send_photo called, enabled={self.enabled}")
        if self.enabled:
            threading.Thread(target=self._send, args=(image_path, caption), daemon=True).start()

    def _send(self, image_path: Path, caption: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = caption.splitlines()[0]
        msg["From"] = self.user
        msg["To"] = self.to
        msg.set_content(caption)
        msg.add_attachment(
            image_path.read_bytes(), maintype="image", subtype="jpeg", filename=image_path.name
        )
        try:
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=20)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=20)
                server.starttls()
            with server:    def send_photo(self, image_path: Path, caption: str) -> None:
        print(f"[DEBUG] send_photo called, enabled={self.enabled}")
                server.login(self.user, self.password)
                server.send_message(msg)
        except Exception as exc:
            print(f"[WARNING] Email send failed: {exc}")