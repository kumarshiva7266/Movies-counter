"""
dashboard_screen.py
Main application screen with sidebar, stats dashboard, and Movies / Web Series management.
"""

import customtkinter as ctk
import threading
import firebase_service

# ── Palette ────────────────────────────────────────────────────────────────────
BG_DARK       = "#0a0a1f"
SIDEBAR_BG    = "#0f0f28"
CARD_BG       = "#12122a"
CARD_BORDER   = "#2a2a5a"
ACCENT_1      = "#7c5cfc"   # purple
ACCENT_2      = "#f95ef6"   # pink
ACCENT_3      = "#22d3a5"   # teal/green
FIELD_BG      = "#1c1c3a"
FIELD_BORDER  = "#3a3a6a"
TEXT_PRIMARY  = "#ffffff"
TEXT_MUTED    = "#8888bb"
ERROR_CLR     = "#ff5a87"
ITEM_BG       = "#1a1a38"
ITEM_HOVER    = "#252550"
DELETE_COLOR  = "#ff4466"
DELETE_HOVER  = "#cc2244"
NAV_ACTIVE    = "#7c5cfc"
NAV_INACTIVE  = "transparent"


# ── Reusable widgets ───────────────────────────────────────────────────────────

class StatCard(ctk.CTkFrame):
    """A small stat display card."""
    def __init__(self, master, icon, label, value_var, accent):
        super().__init__(
            master,
            fg_color=CARD_BG,
            border_color=accent,
            border_width=1,
            corner_radius=16,
        )
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=20, pady=16, fill="both", expand=True)

        ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=30)).pack(anchor="w")
        ctk.CTkLabel(
            inner, textvariable=value_var,
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=accent,
        ).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(
            inner, text=label,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")


class ItemRow(ctk.CTkFrame):
    """A single movie / web-series list row with number, name, delete button."""
    def __init__(self, master, index, item, on_delete):
        super().__init__(
            master,
            fg_color=ITEM_BG,
            corner_radius=10,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self.bind("<Enter>", lambda _: self.configure(fg_color=ITEM_HOVER))
        self.bind("<Leave>", lambda _: self.configure(fg_color=ITEM_BG))

        num = ctk.CTkLabel(
            self,
            text=f"{index:02d}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED,
            width=32,
        )
        num.pack(side="left", padx=(12, 0), pady=10)

        name = ctk.CTkLabel(
            self,
            text=item["name"],
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        name.pack(side="left", padx=12, pady=10, fill="x", expand=True)

        del_btn = ctk.CTkButton(
            self,
            text="✕",
            width=30,
            height=28,
            fg_color=DELETE_COLOR,
            hover_color=DELETE_HOVER,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=on_delete,
        )
        del_btn.pack(side="right", padx=10, pady=8)


# ── Main Dashboard ─────────────────────────────────────────────────────────────

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master, fg_color=BG_DARK, corner_radius=0)
        self.pack(fill="both", expand=True)

        self.user        = user
        self.uid         = user["localId"]
        self.on_logout   = on_logout
        self._tab        = "movies"   # "movies" or "webseries"

        # State
        self._movies:    list[dict] = []
        self._webseries: list[dict] = []
        self._search_query = ctk.StringVar()
        self._search_query.trace_add("write", lambda *_: self._refresh_list())

        # StringVars for stat cards
        self.movies_count_var  = ctk.StringVar(value="—")
        self.series_count_var  = ctk.StringVar(value="—")
        self.total_count_var   = ctk.StringVar(value="—")

        self._build_layout()
        self._load_display_name()
        self._load_all_data()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_layout(self):
        # ── Sidebar ───────────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self, width=220, fg_color=SIDEBAR_BG, corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # ── Main area ─────────────────────────────────────────────────────────
        self.main = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)
        self._build_main()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        s = self.sidebar

        # Logo
        logo = ctk.CTkFrame(s, fg_color="transparent")
        logo.pack(pady=(28, 16), padx=20, fill="x")
        ctk.CTkLabel(logo, text="🎬", font=ctk.CTkFont(size=30)).pack(anchor="w")
        ctk.CTkLabel(
            logo, text="Movie Counter",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        # Divider
        ctk.CTkFrame(s, height=1, fg_color=CARD_BORDER).pack(fill="x", padx=20, pady=8)

        # ── Profile card ──────────────────────────────────────────────────────
        prof_card = ctk.CTkFrame(
            s, fg_color=CARD_BG, corner_radius=14,
            border_color=CARD_BORDER, border_width=1,
        )
        prof_card.pack(padx=16, fill="x", pady=(0, 16))

        inner_p = ctk.CTkFrame(prof_card, fg_color="transparent")
        inner_p.pack(padx=14, pady=14, fill="x")

        # Avatar circle
        av = ctk.CTkLabel(
            inner_p,
            text="👤",
            font=ctk.CTkFont(size=28),
            fg_color=FIELD_BG,
            width=52, height=52,
            corner_radius=26,
        )
        av.pack(anchor="center", pady=(0, 8))

        self.name_lbl = ctk.CTkLabel(
            inner_p, text="Loading…",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self.name_lbl.pack()

        email_txt = self.user.get("email", "")
        ctk.CTkLabel(
            inner_p, text=email_txt,
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
            wraplength=160,
        ).pack(pady=(2, 0))

        # ── Nav buttons ───────────────────────────────────────────────────────
        ctk.CTkLabel(
            s, text="LIBRARY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=24, pady=(8, 4))

        self.nav_movies_btn = ctk.CTkButton(
            s,
            text="  🎬  Movies",
            anchor="w",
            height=42,
            fg_color=NAV_ACTIVE,
            hover_color="#5c3ed6",
            text_color=TEXT_PRIMARY,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            command=self._switch_to_movies,
        )
        self.nav_movies_btn.pack(padx=12, fill="x", pady=3)

        self.nav_series_btn = ctk.CTkButton(
            s,
            text="  📺  Web Series",
            anchor="w",
            height=42,
            fg_color=NAV_INACTIVE,
            hover_color=ITEM_HOVER,
            text_color=TEXT_MUTED,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            command=self._switch_to_webseries,
        )
        self.nav_series_btn.pack(padx=12, fill="x", pady=3)

        # Spacer
        ctk.CTkFrame(s, fg_color="transparent").pack(fill="y", expand=True)

        # Logout button
        ctk.CTkButton(
            s,
            text="  ⏻  Logout",
            anchor="w",
            height=40,
            fg_color="transparent",
            hover_color="#2a0a1a",
            text_color=ERROR_CLR,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            command=self._logout,
        ).pack(padx=12, fill="x", pady=(0, 20))

    # ── Main content area ─────────────────────────────────────────────────────
    def _build_main(self):
        m = self.main

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(m, fg_color="transparent")
        header.pack(padx=28, pady=(24, 0), fill="x")

        self.page_title = ctk.CTkLabel(
            header,
            text="🎬  Movies",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self.page_title.pack(side="left")

        self.page_sub = ctk.CTkLabel(
            header,
            text="Your watched movie collection",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        )
        self.page_sub.pack(side="left", padx=(12, 0), pady=(4, 0))

        # ── Stat cards ────────────────────────────────────────────────────────
        stats_row = ctk.CTkFrame(m, fg_color="transparent")
        stats_row.pack(padx=28, pady=18, fill="x")
        for col in range(3):
            stats_row.columnconfigure(col, weight=1, pad=8)

        StatCard(stats_row, "🎬", "Total Movies",     self.movies_count_var, ACCENT_1).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        StatCard(stats_row, "📺", "Web Series",       self.series_count_var, ACCENT_2).grid(row=0, column=1, sticky="nsew", padx=4)
        StatCard(stats_row, "📚", "Total Library",    self.total_count_var,  ACCENT_3).grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        # ── Toolbar (search + add) ────────────────────────────────────────────
        toolbar = ctk.CTkFrame(m, fg_color="transparent")
        toolbar.pack(padx=28, pady=(0, 12), fill="x")

        self.search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self._search_query,
            placeholder_text="🔍  Search…",
            height=40,
            fg_color=FIELD_BG,
            border_color=FIELD_BORDER,
            border_width=1,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.add_btn = ctk.CTkButton(
            toolbar,
            text="＋  Add",
            height=40,
            width=110,
            fg_color=ACCENT_1,
            hover_color="#6344e0",
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._open_add_dialog,
        )
        self.add_btn.pack(side="right")

        # ── List area ─────────────────────────────────────────────────────────
        list_container = ctk.CTkFrame(m, fg_color="transparent")
        list_container.pack(padx=28, pady=(0, 20), fill="both", expand=True)

        self.list_scroll = ctk.CTkScrollableFrame(
            list_container,
            fg_color=CARD_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=16,
            scrollbar_button_color=FIELD_BORDER,
            scrollbar_button_hover_color=ACCENT_1,
        )
        self.list_scroll.pack(fill="both", expand=True)

        self.empty_lbl = ctk.CTkLabel(
            self.list_scroll,
            text="Nothing here yet.\nClick  ＋ Add  to get started!",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED,
            justify="center",
        )

    # ── Data loading ──────────────────────────────────────────────────────────
    def _load_display_name(self):
        def fetch():
            try:
                name = firebase_service.get_display_name(self.uid)
            except Exception:
                name = self.user.get("email", "User")
            self.after(0, lambda: self.name_lbl.configure(text=name))
        threading.Thread(target=fetch, daemon=True).start()

    def _load_all_data(self):
        def fetch():
            try:
                movies  = firebase_service.get_movies(self.uid)
                series  = firebase_service.get_webseries(self.uid)
            except Exception as e:
                movies, series = [], []
                self.after(0, lambda: self._show_toast(f"Load error: {e}", error=True))

            def update():
                self._movies   = movies
                self._webseries = series
                self._update_counts()
                self._refresh_list()
            self.after(0, update)
        threading.Thread(target=fetch, daemon=True).start()

    def _update_counts(self):
        m = len(self._movies)
        s = len(self._webseries)
        self.movies_count_var.set(str(m))
        self.series_count_var.set(str(s))
        self.total_count_var.set(str(m + s))

    # ── List rendering ────────────────────────────────────────────────────────
    def _refresh_list(self):
        # Clear
        for w in self.list_scroll.winfo_children():
            if isinstance(w, ItemRow):
                w.destroy()
        self.empty_lbl.pack_forget()

        query = self._search_query.get().strip().lower()
        data  = self._movies if self._tab == "movies" else self._webseries

        filtered = [
            item for item in data
            if not query or query in item["name"].lower()
        ]

        if not filtered:
            self.empty_lbl.pack(expand=True, pady=40)
            return

        for i, item in enumerate(filtered, start=1):
            iid = item["id"]
            tab = self._tab

            def make_delete(uid=self.uid, item_id=iid, t=tab):
                return lambda: self._delete_item(uid, item_id, t)

            row = ItemRow(self.list_scroll, i, item, make_delete())
            row.pack(fill="x", pady=3, padx=4)

    # ── Add dialog ────────────────────────────────────────────────────────────
    def _open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Item")
        dialog.geometry("400x220")
        dialog.resizable(False, False)
        dialog.configure(fg_color=CARD_BG)
        dialog.grab_set()
        dialog.focus()

        label_text = "Movie Name" if self._tab == "movies" else "Web Series Name"
        ctk.CTkLabel(
            dialog,
            text=f"➕  New {label_text}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(24, 12))

        entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Enter name…",
            height=44,
            width=320,
            fg_color=FIELD_BG,
            border_color=ACCENT_1,
            border_width=1,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRIMARY,
        )
        entry.pack(pady=4)
        entry.focus()

        err_lbl = ctk.CTkLabel(dialog, text="", text_color=ERROR_CLR, font=ctk.CTkFont(size=11))
        err_lbl.pack()

        def submit():
            name = entry.get().strip()
            if not name:
                err_lbl.configure(text="Name cannot be empty.")
                return
            dialog.destroy()
            self._add_item(name)

        entry.bind("<Return>", lambda _: submit())

        ctk.CTkButton(
            dialog,
            text="Add  ✓",
            height=44,
            width=320,
            fg_color=ACCENT_1,
            hover_color="#6344e0",
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=submit,
        ).pack(pady=10)

    def _add_item(self, name: str):
        def do_add():
            try:
                if self._tab == "movies":
                    new_id = firebase_service.add_movie(self.uid, name)
                    self.after(0, lambda: self._movies.append({"id": new_id, "name": name}))
                else:
                    new_id = firebase_service.add_webseries(self.uid, name)
                    self.after(0, lambda: self._webseries.append({"id": new_id, "name": name}))

                def refresh():
                    self._update_counts()
                    self._refresh_list()
                    self._show_toast(f"✅  \"{name}\" added!")
                self.after(0, refresh)
            except Exception as e:
                self.after(0, lambda: self._show_toast(f"Error: {e}", error=True))
        threading.Thread(target=do_add, daemon=True).start()

    def _delete_item(self, uid: str, item_id: str, tab: str):
        def do_delete():
            try:
                if tab == "movies":
                    firebase_service.delete_movie(uid, item_id)
                    self._movies = [m for m in self._movies if m["id"] != item_id]
                else:
                    firebase_service.delete_webseries(uid, item_id)
                    self._webseries = [s for s in self._webseries if s["id"] != item_id]

                def refresh():
                    self._update_counts()
                    self._refresh_list()
                    self._show_toast("🗑  Item deleted.")
                self.after(0, refresh)
            except Exception as e:
                self.after(0, lambda: self._show_toast(f"Error: {e}", error=True))
        threading.Thread(target=do_delete, daemon=True).start()

    # ── Tab switching ─────────────────────────────────────────────────────────
    def _switch_to_movies(self):
        self._tab = "movies"
        self._search_query.set("")
        self.page_title.configure(text="🎬  Movies")
        self.page_sub.configure(text="Your watched movie collection")
        self.add_btn.configure(text="＋  Add Movie")
        self.nav_movies_btn.configure(fg_color=NAV_ACTIVE, text_color=TEXT_PRIMARY)
        self.nav_series_btn.configure(fg_color=NAV_INACTIVE, text_color=TEXT_MUTED)
        self._refresh_list()

    def _switch_to_webseries(self):
        self._tab = "webseries"
        self._search_query.set("")
        self.page_title.configure(text="📺  Web Series")
        self.page_sub.configure(text="Your watched web series collection")
        self.add_btn.configure(text="＋  Add Series")
        self.nav_series_btn.configure(fg_color=NAV_ACTIVE, text_color=TEXT_PRIMARY)
        self.nav_movies_btn.configure(fg_color=NAV_INACTIVE, text_color=TEXT_MUTED)
        self._refresh_list()

    # ── Toast notification ────────────────────────────────────────────────────
    def _show_toast(self, message: str, error: bool = False):
        color = ERROR_CLR if error else ACCENT_3
        toast = ctk.CTkFrame(
            self,
            fg_color=CARD_BG,
            corner_radius=12,
            border_color=color,
            border_width=1,
        )
        ctk.CTkLabel(
            toast, text=message,
            font=ctk.CTkFont(size=12),
            text_color=color,
        ).pack(padx=16, pady=10)
        toast.place(relx=0.98, rely=0.96, anchor="se")
        self.after(2500, toast.destroy)

    # ── Logout ────────────────────────────────────────────────────────────────
    def _logout(self):
        self.on_logout()
