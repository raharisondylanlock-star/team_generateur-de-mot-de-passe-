from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from security.session import Session


def _close_root(root: tk.Tk) -> None:
    try:
        root.destroy()
    except Exception:
        pass


def require_login(root: tk.Tk, session: Session) -> bool:
    """Block access to protected screens if user is not authenticated."""
    if session is None or not session.is_authenticated():
        messagebox.showwarning("Accès refusé", "Veuillez vous connecter d'abord.", parent=root)
        _close_root(root)
        return False
    return True


def require_admin(root: tk.Tk, session: Session, auth_service) -> bool:
    if not require_login(root, session):
        return False
    assert session.username is not None
    if not auth_service.is_admin(session.username):
        messagebox.showerror("Accès refusé", "Vous n'avez pas les droits administrateur.", parent=root)
        _close_root(root)
        return False
    return True

