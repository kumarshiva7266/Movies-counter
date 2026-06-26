"""
main.py  —  Movie Counter entry point
"""

import sys
import customtkinter as ctk
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen


# ── App configuration ──────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MovieCounterApp(ctk.CTk):
    """Root application window."""

    def __init__(self):
        super().__init__()

        self.title("Movie Counter")
        self.geometry("1120x700")
        self.minsize(900, 620)

        # Center window on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - 1120) // 2
        y  = (sh - 700)  // 2
        self.geometry(f"1120x700+{x}+{y}")

        self._current_user = None
        self._show_login()

    # ── Screen navigation ──────────────────────────────────────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _show_login(self):
        self._clear()
        LoginScreen(self, on_success=self._on_login_success)

    def _on_login_success(self, user: dict):
        self._current_user = user
        self._clear()
        DashboardScreen(self, user=user, on_logout=self._show_login)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MovieCounterApp()
    app.mainloop()
