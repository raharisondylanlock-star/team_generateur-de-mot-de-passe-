from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Session:
    """In-memory UI session (desktop app).

    This prevents direct access to protected screens inside the UI flow.
    """

    username: str | None = None

    def is_authenticated(self) -> bool:
        return bool(self.username)

