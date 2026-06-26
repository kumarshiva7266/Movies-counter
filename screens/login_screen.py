"""
login_screen.py
Modern glassmorphism Login / Register screen.
"""

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter
import threading
import firebase_service


# ── Palette ────────────────────────────────────────────────────────────────────
BG_DARK      = "#0a0a1f"
CARD_BG      = "#12122a"
CARD_BORDER  = "#2a2a5a"
ACCENT_1     = "#7c5cfc"   # purple
ACCENT_2     = "#f95ef6"   # pink
FIELD_BG     = "#1c1c3a"
FIELD_BORDER = "#3a3a6a"
TEXT_PRIMARY = "#ffffff"
TEXT_MUTED   = "#8888bb"
SUCCESS      = "#22d3a5"
ERROR_CLR    = "#ff5a87"


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.pack(fill="both", expand=True)
        self.on_success = on_success
        self._mode = "login"   # or "register"

        self._draw_bg_canvas()
        self._build_card()

    # ── Animated gradient background ──────────────────────────────────────────
    def _draw_bg_canvas(self):
        self.canvas = ctk.CTkCanvas(self, bg=BG_DARK, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.update_idletasks()
        w = self.winfo_width() or 1100
        h = self.winfo_height() or 700

        # Draw three soft gradient blobs
        blobs = [
            (w * 0.15, h * 0.25, 300, ACCENT_1),
            (w * 0.85, h * 0.15, 250, ACCENT_2),
            (w * 0.55, h * 0.80, 280, "#2255ff"),
        ]
        for bx, by, r, color in blobs:
            rgb = _hex_to_rgb(color)
            for i in range(r, 0, -4):
                alpha_f = (i / r) * 0.18
                alpha_i = int(alpha_f * 255)
                c = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0] * alpha_f + _hex_to_rgb(BG_DARK)[0] * (1 - alpha_f)),
                    int(rgb[1] * alpha_f + _hex_to_rgb(BG_DARK)[1] * (1 - alpha_f)),
                    int(rgb[2] * alpha_f + _hex_to_rgb(BG_DARK)[2] * (1 - alpha_f)),
                )
                self.canvas.create_oval(
                    bx - i, by - i, bx + i, by + i,
                    outline="", fill=c
                )

    # ── Glass card ────────────────────────────────────────────────────────────
    def _build_card(self):
        outer = ctk.CTkFrame(
            self,
            width=440,
            height=580,
            fg_color=CARD_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=24,
        )
        outer.place(relx=0.5, rely=0.5, anchor="center")
        outer.pack_propagate(False)

        # ── Logo / Title ──────────────────────────────────────────────────────
        title_frame = ctk.CTkFrame(outer, fg_color="transparent")
        title_frame.pack(pady=(36, 4))

        ctk.CTkLabel(
            title_frame,
            text="🎬",
            font=ctk.CTkFont(size=44),
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="Movie Counter",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="Track your cinematic journey",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
        ).pack(pady=(2, 0))

        # ── Tab toggle ────────────────────────────────────────────────────────
        tab_frame = ctk.CTkFrame(outer, fg_color=FIELD_BG, corner_radius=12)
        tab_frame.pack(padx=36, pady=(20, 10), fill="x")

        self.login_tab_btn = ctk.CTkButton(
            tab_frame, text="Login",
            fg_color=ACCENT_1, text_color="white",
            hover_color="#6344e0", corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._show_login,
        )
        self.login_tab_btn.pack(side="left", expand=True, fill="x", padx=4, pady=4)

        self.reg_tab_btn = ctk.CTkButton(
            tab_frame, text="Register",
            fg_color="transparent", text_color=TEXT_MUTED,
            hover_color=FIELD_BORDER, corner_radius=10,
            font=ctk.CTkFont(size=13),
            command=self._show_register,
        )
        self.reg_tab_btn.pack(side="right", expand=True, fill="x", padx=4, pady=4)

        # ── Form fields ───────────────────────────────────────────────────────
        form = ctk.CTkFrame(outer, fg_color="transparent")
        form.pack(padx=36, fill="x")

        # Display name (register only)
        self.name_frame = ctk.CTkFrame(form, fg_color="transparent")
        ctk.CTkLabel(
            self.name_frame,
            text="Display Name",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))
        self.name_entry = ctk.CTkEntry(
            self.name_frame,
            placeholder_text="Your name",
            height=44,
            fg_color=FIELD_BG,
            border_color=FIELD_BORDER,
            border_width=1,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
        )
        self.name_entry.pack(fill="x")

        # Email
        email_frame = ctk.CTkFrame(form, fg_color="transparent")
        email_frame.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(
            email_frame, text="Email",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 4))
        self.email_entry = ctk.CTkEntry(
            email_frame,
            placeholder_text="you@example.com",
            height=44,
            fg_color=FIELD_BG,
            border_color=FIELD_BORDER,
            border_width=1,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
        )
        self.email_entry.pack(fill="x")

        # Password
        pwd_frame = ctk.CTkFrame(form, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=(12, 0))
        ctk.CTkLabel(
            pwd_frame, text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED, anchor="w",
        ).pack(fill="x", pady=(0, 4))
        self.pwd_entry = ctk.CTkEntry(
            pwd_frame,
            placeholder_text="••••••••",
            show="•",
            height=44,
            fg_color=FIELD_BG,
            border_color=FIELD_BORDER,
            border_width=1,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
        )
        self.pwd_entry.pack(fill="x")

        # ── Status label ─────────────────────────────────────────────────────
        self.status_lbl = ctk.CTkLabel(
            outer, text="",
            font=ctk.CTkFont(size=12),
            text_color=ERROR_CLR,
            wraplength=360,
        )
        self.status_lbl.pack(pady=(10, 0))

        # ── Action button ─────────────────────────────────────────────────────
        self.action_btn = ctk.CTkButton(
            outer,
            text="Login  →",
            height=48,
            fg_color=ACCENT_1,
            hover_color="#6344e0",
            corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._handle_action,
        )
        self.action_btn.pack(padx=36, fill="x", pady=(8, 0))

        # ── Loading spinner label ─────────────────────────────────────────────
        self.loading_lbl = ctk.CTkLabel(
            outer, text="",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        )
        self.loading_lbl.pack(pady=(4, 0))

        # Bind Enter key
        self.winfo_toplevel().bind("<Return>", lambda _: self._handle_action())

    # ── Mode switching ────────────────────────────────────────────────────────
    def _show_login(self):
        self._mode = "login"
        self.name_frame.pack_forget()
        self.login_tab_btn.configure(fg_color=ACCENT_1, text_color="white")
        self.reg_tab_btn.configure(fg_color="transparent", text_color=TEXT_MUTED)
        self.action_btn.configure(text="Login  →")
        self.status_lbl.configure(text="")

    def _show_register(self):
        self._mode = "register"
        self.name_frame.pack(fill="x", pady=(12, 0), before=self.email_entry.master)
        self.reg_tab_btn.configure(fg_color=ACCENT_1, text_color="white")
        self.login_tab_btn.configure(fg_color="transparent", text_color=TEXT_MUTED)
        self.action_btn.configure(text="Create Account  →")
        self.status_lbl.configure(text="")

    # ── Action handling ───────────────────────────────────────────────────────
    def _handle_action(self):
        self.action_btn.configure(state="disabled")
        self.loading_lbl.configure(text="⏳ Please wait…")
        self.status_lbl.configure(text="")
        threading.Thread(target=self._do_auth, daemon=True).start()

    def _do_auth(self):
        email = self.email_entry.get().strip()
        password = self.pwd_entry.get().strip()

        try:
            if self._mode == "login":
                user = firebase_service.login(email, password)
            else:
                name = self.name_entry.get().strip() or email.split("@")[0]
                user = firebase_service.register(email, password, name)

            self.after(0, lambda: self._on_success(user))
        except Exception as exc:
            msg = self._parse_error(str(exc))
            self.after(0, lambda m=msg: self._on_error(m))

    def _on_success(self, user):
        self.loading_lbl.configure(text="")
        self.status_lbl.configure(text="✅ Success!", text_color=SUCCESS)
        self.action_btn.configure(state="normal")
        self.after(600, lambda: self.on_success(user))

    def _on_error(self, msg):
        self.loading_lbl.configure(text="")
        self.status_lbl.configure(text=f"⚠ {msg}", text_color=ERROR_CLR)
        self.action_btn.configure(state="normal")

    @staticmethod
    def _parse_error(raw: str) -> str:
        if "EMAIL_NOT_FOUND" in raw or "INVALID_EMAIL" in raw:
            return "Invalid email address."
        if "WRONG_PASSWORD" in raw or "INVALID_LOGIN_CREDENTIALS" in raw:
            return "Wrong password. Please try again."
        if "EMAIL_EXISTS" in raw:
            return "Email already registered. Try logging in."
        if "WEAK_PASSWORD" in raw:
            return "Password must be at least 6 characters."
        if "TOO_MANY_ATTEMPTS" in raw:
            return "Too many attempts. Try again later."
        if "INVALID_API_KEY" in raw or "API_KEY" in raw:
            return "Firebase API key not configured. See README."
        return "Something went wrong. Check your connection."
