"""
ui.memory_viewer
~~~~~~~~~~~~~~~~
Professional, themeable CustomTkinter GUI for the 3D Living Memory Core.
Features a live metric dashboard, multi-theme / dark-light support, 
memory strand inspection, manual memory creation, and real-time filtering.
"""

import sys
import threading
from pathlib import Path

# Add root directory to path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import customtkinter as ctk
from core.memory_engine import MemoryCore

# Professional Color Themes
THEMES = {
    "Synthwave 80s (Dark)": {
        "mode": "dark",
        "BG": "#0d0221",
        "BG2": "#1a0933",
        "BG3": "#260e4a",
        "CARD": "#1f0a3d",
        "CARD_HOVER": "#2b0e54",
        "TXT": "#fbeeeb",
        "TXT_MUTED": "#a288c9",
        "ACCENT1": "#ff007f",
        "ACCENT2": "#00f0ff",
        "CHIP_BG": "#34135e",
        "BORDER": "#491b82",
        "ERR": "#ff2a6d",
        "WARN": "#ffb800",
        "SUCCESS": "#05ffa1"
    },
    "Cyber Neon (Dark)": {
        "mode": "dark",
        "BG": "#0a0a0f",
        "BG2": "#12121a",
        "BG3": "#181828",
        "CARD": "#141422",
        "CARD_HOVER": "#1e1e32",
        "TXT": "#f0f0ff",
        "TXT_MUTED": "#7a7a9e",
        "ACCENT1": "#ff00ff",
        "ACCENT2": "#00ffcc",
        "CHIP_BG": "#222238",
        "BORDER": "#2e2e4a",
        "ERR": "#ff4444",
        "WARN": "#ffaa00",
        "SUCCESS": "#00ff88"
    },
    "Midnight Obsidian (Dark)": {
        "mode": "dark",
        "BG": "#090d16",
        "BG2": "#0f172a",
        "BG3": "#1e293b",
        "CARD": "#131e36",
        "CARD_HOVER": "#1a2a4c",
        "TXT": "#f8fafc",
        "TXT_MUTED": "#94a3b8",
        "ACCENT1": "#38bdf8",
        "ACCENT2": "#818cf8",
        "CHIP_BG": "#1e293b",
        "BORDER": "#334155",
        "ERR": "#f43f5e",
        "WARN": "#f59e0b",
        "SUCCESS": "#10b981"
    },
    "Clean Minimal (Light)": {
        "mode": "light",
        "BG": "#f8fafc",
        "BG2": "#ffffff",
        "BG3": "#f1f5f9",
        "CARD": "#ffffff",
        "CARD_HOVER": "#f8fafc",
        "TXT": "#0f172a",
        "TXT_MUTED": "#64748b",
        "ACCENT1": "#0284c7",
        "ACCENT2": "#0d9488",
        "CHIP_BG": "#e2e8f0",
        "BORDER": "#cbd5e1",
        "ERR": "#e11d48",
        "WARN": "#d97706",
        "SUCCESS": "#16a34a"
    }
}

PAGE_SIZE = 25


class MemoryViewer(ctk.CTkToplevel):
    """Standalone professional desktop browser for 3D Weaire-Phelan Living Memories."""

    def __init__(self, parent=None, initial_theme="Synthwave 80s (Dark)", memory_core: MemoryCore = None):
        if memory_core is None:
            raise ValueError(
                "MemoryViewer requires an explicit MemoryCore instance. "
                "Example: memory = MemoryCore(); ui = MemoryViewer(root, memory_core=memory)"
            )
        self.memory = memory_core
        if parent is None:
            self._root = ctk.CTk()
            self._root.withdraw()
            super().__init__(self._root)
        else:
            self._root = None
            super().__init__(parent)

        self.current_theme_name = initial_theme
        self.theme = THEMES[self.current_theme_name]
        ctk.set_appearance_mode(self.theme["mode"])

        self.title("3D Living Memory Core — Cluster & Lattice Browser v1.0.0")
        self.geometry("960x720")
        self.minsize(780, 520)
        self.configure(fg_color=self.theme["BG"])

        self.after(100, self.lift)
        self._all_memories = []
        self._filtered_memories = []
        self._displayed_count = 0
        self._is_loading = False
        self._stats = {}

        self._build_ui()
        self._start_fetch()

    def _build_ui(self):
        T = self.theme

        # -------------------------------------------------------------------
        # 1. Top Header & Metric Dashboard Banner
        # -------------------------------------------------------------------
        header_card = ctk.CTkFrame(self, fg_color=T["BG2"], corner_radius=12, border_width=1, border_color=T["BORDER"])
        header_card.pack(fill="x", padx=16, pady=(16, 10))

        # Title Row
        title_row = ctk.CTkFrame(header_card, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(12, 6))

        title = ctk.CTkLabel(
            title_row,
            text="🧠 3D WEAIRE–PHELAN LIVING MEMORY CORE",
            font=("Consolas", 15, "bold"),
            text_color=T["ACCENT1"]
        )
        title.pack(side="left")

        # Theme selector dropdown
        theme_row = ctk.CTkFrame(title_row, fg_color="transparent")
        theme_row.pack(side="right")

        ctk.CTkLabel(theme_row, text="Theme:", font=("Consolas", 10), text_color=T["TXT_MUTED"]).pack(side="left", padx=4)
        self.theme_menu = ctk.CTkOptionMenu(
            theme_row,
            values=list(THEMES.keys()),
            command=self._change_theme,
            variable=ctk.StringVar(value=self.current_theme_name),
            fg_color=T["BG3"],
            button_color=T["ACCENT2"],
            text_color=T["TXT"],
            dropdown_fg_color=T["BG2"],
            dropdown_text_color=T["TXT"],
            font=("Consolas", 10),
            width=170,
            height=24
        )
        self.theme_menu.pack(side="left")

        # Metrics Dashboard Row
        self.metrics_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.chip_total = self._create_metric_chip(self.metrics_frame, "Memories", "0", T["ACCENT2"])
        self.chip_cells = self._create_metric_chip(self.metrics_frame, "3D Cells", "0", T["ACCENT1"])
        self.chip_strands = self._create_metric_chip(self.metrics_frame, "Strands", "0", T["SUCCESS"])
        self.chip_maps = self._create_metric_chip(self.metrics_frame, "Active Maps", "0", T["WARN"])
        self.chip_security = self._create_metric_chip(self.metrics_frame, "Security", "Plaintext", T["TXT_MUTED"])

        # -------------------------------------------------------------------
        # 2. Filter & Search Controls Bar
        # -------------------------------------------------------------------
        ctrl_card = ctk.CTkFrame(self, fg_color=T["BG2"], corner_radius=10, border_width=1, border_color=T["BORDER"])
        ctrl_card.pack(fill="x", padx=16, pady=(0, 10))

        ctrl_inner = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=12, pady=10)

        # Domain map selector
        ctk.CTkLabel(ctrl_inner, text="Domain:", font=("Consolas", 11), text_color=T["TXT"]).pack(side="left", padx=(0, 4))
        self.map_var = ctk.StringVar(value="all")
        self.map_menu = ctk.CTkOptionMenu(
            ctrl_inner,
            variable=self.map_var,
            values=["all"],
            command=lambda _: self._apply_filters(),
            fg_color=T["BG3"],
            button_color=T["ACCENT2"],
            text_color=T["TXT"],
            dropdown_fg_color=T["BG2"],
            dropdown_text_color=T["TXT"],
            width=130,
            height=28,
            font=("Consolas", 11)
        )
        self.map_menu.pack(side="left", padx=(0, 12))

        # Emotional weight filter
        ctk.CTkLabel(ctrl_inner, text="Weight:", font=("Consolas", 11), text_color=T["TXT"]).pack(side="left", padx=(0, 4))
        self.weight_var = ctk.StringVar(value="All Weights")
        self.weight_menu = ctk.CTkOptionMenu(
            ctrl_inner,
            variable=self.weight_var,
            values=["All Weights", "High (>= 0.8)", "Mid (0.4 - 0.7)", "Low (< 0.4)"],
            command=lambda _: self._apply_filters(),
            fg_color=T["BG3"],
            button_color=T["ACCENT2"],
            text_color=T["TXT"],
            dropdown_fg_color=T["BG2"],
            dropdown_text_color=T["TXT"],
            width=135,
            height=28,
            font=("Consolas", 11)
        )
        self.weight_menu.pack(side="left", padx=(0, 12))

        # Search Bar
        self.search_entry = ctk.CTkEntry(
            ctrl_inner,
            placeholder_text="Search semantic concepts, keywords, or text...",
            fg_color=T["BG3"],
            border_color=T["BORDER"],
            text_color=T["TXT"],
            placeholder_text_color=T["TXT_MUTED"],
            height=28,
            font=("Consolas", 11)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._apply_filters())

        search_btn = ctk.CTkButton(
            ctrl_inner,
            text="Search",
            command=self._apply_filters,
            fg_color=T["ACCENT2"],
            hover_color=T.get("SUCCESS", "#00ffaa"),
            text_color="#000000" if T["mode"] == "dark" else "#ffffff",
            font=("Consolas", 11, "bold"),
            width=75,
            height=28
        )
        search_btn.pack(side="left")

        # -------------------------------------------------------------------
        # 3. Main Scrollable Memory Card View
        # -------------------------------------------------------------------
        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=T["BG2"],
            corner_radius=12,
            border_width=1,
            border_color=T["BORDER"]
        )
        self.cards_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        # -------------------------------------------------------------------
        # 4. Bottom Action & Status Toolbar
        # -------------------------------------------------------------------
        bottom_card = ctk.CTkFrame(self, fg_color=T["BG2"], corner_radius=10, border_width=1, border_color=T["BORDER"])
        bottom_card.pack(fill="x", padx=16, pady=(0, 16))

        bottom_inner = ctk.CTkFrame(bottom_card, fg_color="transparent")
        bottom_inner.pack(fill="x", padx=12, pady=8)

        refresh_btn = ctk.CTkButton(
            bottom_inner,
            text="🔄 Refresh",
            command=self._start_fetch,
            fg_color=T["BG3"],
            hover_color=T["BORDER"],
            text_color=T["ACCENT2"],
            font=("Consolas", 11, "bold"),
            width=90,
            height=28
        )
        refresh_btn.pack(side="left", padx=(0, 8))

        add_btn = ctk.CTkButton(
            bottom_inner,
            text="➕ New Memory",
            command=self._open_add_dialog,
            fg_color=T["BG3"],
            hover_color=T["BORDER"],
            text_color=T["SUCCESS"],
            font=("Consolas", 11, "bold"),
            width=120,
            height=28
        )
        add_btn.pack(side="left", padx=(0, 8))

        prune_btn = ctk.CTkButton(
            bottom_inner,
            text="🧹 Prune Decay",
            command=self._run_prune,
            fg_color=T["BG3"],
            hover_color=T["WARN"],
            text_color=T["WARN"],
            font=("Consolas", 11),
            width=115,
            height=28
        )
        prune_btn.pack(side="left")

        self.status_lbl = ctk.CTkLabel(
            bottom_inner,
            text="Ready",
            font=("Consolas", 10),
            text_color=T["TXT_MUTED"]
        )
        self.status_lbl.pack(side="left", padx=16)

        close_btn = ctk.CTkButton(
            bottom_inner,
            text="Close",
            command=self._close_window,
            fg_color=T["BG3"],
            hover_color=T["ERR"],
            text_color=T["TXT"],
            font=("Consolas", 11),
            width=75,
            height=28
        )
        close_btn.pack(side="right")

    def _create_metric_chip(self, parent, title: str, value: str, color: str):
        T = self.theme
        chip = ctk.CTkFrame(parent, fg_color=T["CHIP_BG"], corner_radius=8, height=36)
        chip.pack(side="left", padx=4, fill="y")
        
        lbl_title = ctk.CTkLabel(chip, text=title.upper(), font=("Consolas", 8, "bold"), text_color=T["TXT_MUTED"])
        lbl_title.pack(padx=8, pady=(3, 0))
        
        lbl_val = ctk.CTkLabel(chip, text=value, font=("Consolas", 11, "bold"), text_color=color)
        lbl_val.pack(padx=8, pady=(0, 3))
        return lbl_val

    def _change_theme(self, new_theme_name: str):
        self.current_theme_name = new_theme_name
        self.theme = THEMES[new_theme_name]
        ctk.set_appearance_mode(self.theme["mode"])
        
        # Rebuild UI with new theme colors
        for w in self.winfo_children():
            w.destroy()
        self.configure(fg_color=self.theme["BG"])
        self._build_ui()
        self._update_metrics(self._stats)
        self._apply_filters()

    def _close_window(self):
        if self._root:
            self._root.destroy()
        else:
            self.destroy()

    def _start_fetch(self):
        if self._is_loading:
            return
        self._is_loading = True
        self._fetch_result = None
        self._fetch_error = None
        self.status_lbl.configure(text="Loading 3D lattice from disk...")

        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        loading_lbl = ctk.CTkLabel(
            self.cards_frame,
            text="⏳ Fetching vector memories and 3D spiderweb graph from disk...",
            font=("Consolas", 12, "italic"),
            text_color=self.theme["TXT_MUTED"]
        )
        loading_lbl.pack(pady=50)

        def worker():
            try:
                stats = self.memory.get_stats()
                mems = self.memory.get_all_memories()
                maps = stats.get("available_maps", ["general"])
                self._fetch_result = (mems, maps, stats)
            except Exception as e:
                self._fetch_error = e

        threading.Thread(target=worker, daemon=True).start()
        self.after(30, self._check_fetch_status)

    def _check_fetch_status(self):
        if self._fetch_result is not None:
            mems, maps, stats = self._fetch_result
            self._fetch_result = None
            self._on_fetch_done(mems, maps, stats)
        elif self._fetch_error is not None:
            err = self._fetch_error
            self._fetch_error = None
            self._on_fetch_error(err)
        else:
            if self._is_loading:
                self.after(30, self._check_fetch_status)

    def _on_fetch_done(self, mems, maps, stats):
        self._is_loading = False
        self._all_memories = mems
        self._stats = stats

        all_maps = ["all"] + sorted(list(set(maps)))
        self.map_menu.configure(values=all_maps)

        self._update_metrics(stats)
        self.status_lbl.configure(text="Synced & Ready")
        self._apply_filters()

    def _update_metrics(self, stats: dict):
        if not stats:
            return
        total = stats.get("total_memories", 0)
        cells = stats.get("weaire_phelan_cells", 0)
        strands = stats.get("spiderweb_strands", 0)
        maps = stats.get("total_maps", 0)
        enc = "Encrypted (AES)" if stats.get("encryption_enabled") else "Plaintext"

        self.chip_total.configure(text=str(total))
        self.chip_cells.configure(text=str(cells))
        self.chip_strands.configure(text=str(strands))
        self.chip_maps.configure(text=str(maps))
        self.chip_security.configure(
            text=enc,
            text_color=self.theme["SUCCESS"] if stats.get("encryption_enabled") else self.theme["TXT_MUTED"]
        )

    def _on_fetch_error(self, err):
        self._is_loading = False
        self.status_lbl.configure(text=f"Error: {err}", text_color=self.theme["ERR"])
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        ctk.CTkLabel(
            self.cards_frame,
            text=f"Failed to load memories: {err}",
            font=("Consolas", 11),
            text_color=self.theme["ERR"]
        ).pack(pady=40)

    def _apply_filters(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        selected_map = self.map_var.get()
        selected_weight = self.weight_var.get()
        search_query = self.search_entry.get().strip().lower()

        filtered = self._all_memories

        # Filter by map
        if selected_map != "all":
            filtered = [m for m in filtered if m.get("map", "general") == selected_map]

        # Filter by emotional weight
        if selected_weight == "High (>= 0.8)":
            filtered = [m for m in filtered if float(m.get("emotional_weight", 0.5)) >= 0.8]
        elif selected_weight == "Mid (0.4 - 0.7)":
            filtered = [m for m in filtered if 0.4 <= float(m.get("emotional_weight", 0.5)) < 0.8]
        elif selected_weight == "Low (< 0.4)":
            filtered = [m for m in filtered if float(m.get("emotional_weight", 0.5)) < 0.4]

        # Filter by search query
        if search_query:
            filtered = [
                m for m in filtered
                if search_query in m.get("content", "").lower() or search_query in m.get("map", "").lower()
            ]

        filtered.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
        self._filtered_memories = filtered
        self._displayed_count = 0

        self.status_lbl.configure(text=f"Showing {len(filtered)} of {len(self._all_memories)} memories")

        if not filtered:
            ctk.CTkLabel(
                self.cards_frame,
                text="No memories found matching the specified filters.",
                font=("Consolas", 11, "italic"),
                text_color=self.theme["TXT_MUTED"]
            ).pack(pady=40)
            return

        self._render_batch()

    def _render_batch(self):
        if hasattr(self, "_load_more_btn") and self._load_more_btn.winfo_exists():
            self._load_more_btn.destroy()

        T = self.theme
        start_idx = self._displayed_count
        end_idx = min(len(self._filtered_memories), start_idx + PAGE_SIZE)

        for i in range(start_idx, end_idx):
            mem = self._filtered_memories[i]
            card = ctk.CTkFrame(self.cards_frame, fg_color=T["CARD"], corner_radius=10, border_width=1, border_color=T["BORDER"])
            card.pack(fill="x", padx=4, pady=4)

            # Card Header Row
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(8, 4))

            map_name = mem.get("map", "general").upper()
            map_badge = ctk.CTkLabel(
                top_row,
                text=f"[{map_name}]",
                font=("Consolas", 10, "bold"),
                text_color=T["ACCENT2"]
            )
            map_badge.pack(side="left")

            cell_name = mem.get("cell", "").replace("WeairePhelan_", "")
            cell_badge = ctk.CTkLabel(
                top_row,
                text=f"🕸️ {cell_name}" if cell_name else "",
                font=("Consolas", 9, "italic"),
                text_color=T["ACCENT1"]
            )
            cell_badge.pack(side="left", padx=6)

            coords = mem.get("3d_coords", (0, 0, 0))
            coords_lbl = ctk.CTkLabel(
                top_row,
                text=f"3D: ({coords[0]:.2f}, {coords[1]:.2f}, {coords[2]:.2f})",
                font=("Consolas", 8),
                text_color=T["TXT_MUTED"]
            )
            coords_lbl.pack(side="left", padx=4)

            wt = float(mem.get("emotional_weight", 0.5))
            wt_color = T["SUCCESS"] if wt >= 0.8 else (T["WARN"] if wt >= 0.4 else T["TXT_MUTED"])
            wt_lbl = ctk.CTkLabel(
                top_row,
                text=f"Resonance: {wt:.2f}",
                font=("Consolas", 9, "bold"),
                text_color=wt_color
            )
            wt_lbl.pack(side="left", padx=6)

            ts = mem.get("timestamp", "")
            if ts and len(ts) >= 16:
                ts = ts[:16].replace("T", " ")
            time_lbl = ctk.CTkLabel(
                top_row,
                text=f"• {ts}",
                font=("Consolas", 8),
                text_color=T["TXT_MUTED"]
            )
            time_lbl.pack(side="left", padx=4)

            acc_cnt = mem.get("access_count", 1)
            acc_lbl = ctk.CTkLabel(
                top_row,
                text=f"• 👁️ {acc_cnt}x",
                font=("Consolas", 8, "bold"),
                text_color=T["ACCENT2"] if acc_cnt > 1 else T["TXT_MUTED"]
            )
            acc_lbl.pack(side="left", padx=4)

            # Action buttons
            mem_id = mem.get("id", "")
            if mem_id:
                del_btn = ctk.CTkButton(
                    top_row,
                    text="🗑️",
                    command=lambda m_id=mem_id, c=card: self._delete_single(m_id, c),
                    fg_color="transparent",
                    hover_color=T["ERR"],
                    text_color=T["TXT_MUTED"],
                    width=26,
                    height=20,
                    font=("Consolas", 10)
                )
                del_btn.pack(side="right")

                strand_btn = ctk.CTkButton(
                    top_row,
                    text="🔗 Strands",
                    command=lambda m_id=mem_id: self._inspect_strands(m_id),
                    fg_color="transparent",
                    hover_color=T["CHIP_BG"],
                    text_color=T["ACCENT2"],
                    width=65,
                    height=20,
                    font=("Consolas", 9, "bold")
                )
                strand_btn.pack(side="right", padx=4)

            # Card Content
            content_lbl = ctk.CTkLabel(
                card,
                text=mem.get("content", ""),
                font=("Consolas", 12),
                text_color=T["TXT"],
                wraplength=840,
                justify="left",
                anchor="w"
            )
            content_lbl.pack(fill="x", padx=12, pady=(0, 10))

        self._displayed_count = end_idx

        # Show Load More button if items remain
        if self._displayed_count < len(self._filtered_memories):
            remaining = len(self._filtered_memories) - self._displayed_count
            self._load_more_btn = ctk.CTkButton(
                self.cards_frame,
                text=f"🔽 Load Next {min(PAGE_SIZE, remaining)} Memories (Showing {self._displayed_count} of {len(self._filtered_memories)})",
                command=self._render_batch,
                fg_color=T["BG3"],
                hover_color=T["BORDER"],
                text_color=T["ACCENT1"],
                font=("Consolas", 11, "bold"),
                height=34
            )
            self._load_more_btn.pack(fill="x", padx=20, pady=14)

    def _delete_single(self, mem_id: str, card_widget):
        try:
            ok = self.memory.delete_entry(mem_id)
            if ok:
                card_widget.destroy()
                self._all_memories = [m for m in self._all_memories if m.get("id") != mem_id]
                self._filtered_memories = [m for m in self._filtered_memories if m.get("id") != mem_id]
                self.status_lbl.configure(text=f"Deleted memory {mem_id[:12]}...")
                self._update_metrics(self.memory.get_stats())
        except Exception as e:
            self.status_lbl.configure(text=f"Delete error: {e}", text_color=self.theme["ERR"])

    def _inspect_strands(self, mem_id: str):
        conns = self.memory.get_connections(mem_id)
        strands = conns.get("strands", [])

        # Modal Window
        dlg = ctk.CTkToplevel(self)
        dlg.title(f"3D Strands for Memory [{mem_id[:16]}]")
        dlg.geometry("520x360")
        dlg.configure(fg_color=self.theme["BG"])
        dlg.after(100, dlg.lift)

        ctk.CTkLabel(
            dlg,
            text=f"🕸️ Linked Facet Strands ({len(strands)} Connections)",
            font=("Consolas", 13, "bold"),
            text_color=self.theme["ACCENT1"]
        ).pack(padx=16, pady=12)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=self.theme["BG2"], corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        if not strands:
            ctk.CTkLabel(
                scroll,
                text="No active strands connected to this memory node.",
                font=("Consolas", 11, "italic"),
                text_color=self.theme["TXT_MUTED"]
            ).pack(pady=30)
        else:
            for s in strands:
                card = ctk.CTkFrame(scroll, fg_color=self.theme["BG3"], corner_radius=6)
                card.pack(fill="x", pady=3, padx=2)
                
                target_id = s.get("target_id", "")
                wt = s.get("weight", 0.0)
                reason = s.get("reason", "Topological Proximity / Concept Affinity")
                
                ctk.CTkLabel(
                    card,
                    text=f"Target: {target_id} (Coupling: {wt:.3f})",
                    font=("Consolas", 10, "bold"),
                    text_color=self.theme["ACCENT2"]
                ).pack(anchor="w", padx=8, pady=(4, 1))
                
                ctk.CTkLabel(
                    card,
                    text=f"Reason: {reason}",
                    font=("Consolas", 9),
                    text_color=self.theme["TXT"]
                ).pack(anchor="w", padx=8, pady=(0, 4))

    def _open_add_dialog(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Weave New Memory Entry")
        dlg.geometry("500x380")
        dlg.configure(fg_color=self.theme["BG"])
        dlg.after(100, dlg.lift)

        T = self.theme
        ctk.CTkLabel(dlg, text="➕ Weave New 3D Memory", font=("Consolas", 13, "bold"), text_color=T["ACCENT1"]).pack(pady=(16, 8))

        content_box = ctk.CTkTextbox(dlg, height=120, fg_color=T["BG2"], text_color=T["TXT"], font=("Consolas", 11))
        content_box.pack(fill="x", padx=16, pady=6)
        content_box.insert("1.0", "Type the memory content here...")

        opts_row = ctk.CTkFrame(dlg, fg_color="transparent")
        opts_row.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(opts_row, text="Map:", font=("Consolas", 10), text_color=T["TXT"]).pack(side="left", padx=4)
        map_entry = ctk.CTkEntry(opts_row, width=120, height=26, font=("Consolas", 10))
        map_entry.insert(0, "general")
        map_entry.pack(side="left", padx=4)

        ctk.CTkLabel(opts_row, text="Weight (0-1):", font=("Consolas", 10), text_color=T["TXT"]).pack(side="left", padx=6)
        weight_entry = ctk.CTkEntry(opts_row, width=60, height=26, font=("Consolas", 10))
        weight_entry.insert(0, "0.8")
        weight_entry.pack(side="left", padx=4)

        def save_and_close():
            txt = content_box.get("1.0", "end").strip()
            mp = map_entry.get().strip() or "general"
            try:
                wt = float(weight_entry.get().strip())
            except ValueError:
                wt = 0.7
            if txt and len(txt) >= 3:
                self.memory.save_entry(content=txt, map_name=mp, emotional_weight=wt)
                dlg.destroy()
                self._start_fetch()

        save_btn = ctk.CTkButton(
            dlg,
            text="Save & Weave",
            command=save_and_close,
            fg_color=T["SUCCESS"],
            text_color="#000000" if T["mode"] == "dark" else "#ffffff",
            font=("Consolas", 11, "bold"),
            height=30
        )
        save_btn.pack(pady=12)

    def _run_prune(self):
        res = self.memory.prune_memories(min_emotional_weight=0.15)
        self.status_lbl.configure(text=f"Pruned {res.get('pruned_count', 0)} decayed memories.")
        self._start_fetch()


if __name__ == "__main__":
    from core.memory_engine import MemoryCore
    memory = MemoryCore()
    root = ctk.CTk()
    root.title("3D Living Memory Core Viewer")
    ui = MemoryViewer(root, memory_core=memory)
    root.mainloop()
