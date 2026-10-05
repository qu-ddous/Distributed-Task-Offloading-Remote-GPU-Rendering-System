from typing import Callable
import customtkinter as ctk

from client.ui.theme import *

class SidebarNavigation(ctk.CTkFrame):
    def __init__(self, master, on_navigate: Callable[[str], None]):
        super().__init__(master, fg_color=BG_SIDEBAR, width=240, corner_radius=0)
        self.on_navigate = on_navigate
        self.active_page = "dashboard"
        self.buttons = {}

        self._build_sidebar()

    def _build_sidebar(self):
        # App Brand Header with shiny badge
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(24, 20))

        badge = ctk.CTkLabel(
            brand_frame,
            text="CLAY STUDIO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=ACCENT_PURPLE,
            corner_radius=6,
            padx=8,
            pady=2
        )
        badge.pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            brand_frame,
            text="⚡ GPU Stream",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame,
            text="Task Offloading Studio",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w")

        # Divider line
        div = ctk.CTkFrame(self, fg_color=BORDER_COLOR, height=1)
        div.pack(fill="x", padx=16, pady=(0, 14))

        # Navigation Category
        ctk.CTkLabel(
            self,
            text="MAIN WORKFLOW",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w", padx=20, pady=(0, 6))

        # Nav Buttons (Vibrant clay cards)
        self._add_nav_item("dashboard", "📊  Dashboard", "dashboard")
        self._add_nav_item("render_job", "🎬  New Render Job", "render_job")
        self._add_nav_item("active_job", "📡  Live Monitor", "active_job")

        ctk.CTkLabel(
            self,
            text="SYSTEM & TOOLS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w", padx=20, pady=(16, 6))

        self._add_nav_item("benchmarks", "⚡  Benchmarks", "benchmarks")
        self._add_nav_item("settings", "⚙️  Host & Settings", "settings")

        # Bottom System Info Clay Card
        info_card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )
        info_card.pack(side="bottom", fill="x", padx=16, pady=20)

        ctk.CTkLabel(
            info_card,
            text="ENGINE STATUS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            info_card,
            text="● NVENC Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_GREEN
        ).pack(anchor="w", padx=14, pady=(0, 10))

    def _add_nav_item(self, key: str, label: str, page_name: str):
        btn = ctk.CTkButton(
            self,
            text=label,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=44,
            corner_radius=10,
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color="#D8E2F0",
            command=lambda: self.select_nav(page_name)
        )
        btn.pack(fill="x", padx=14, pady=3)
        self.buttons[page_name] = btn

    def select_nav(self, page_name: str):
        self.active_page = page_name
        for name, btn in self.buttons.items():
            if name == page_name:
                btn.configure(
                    fg_color=ACCENT_BLUE,
                    text_color="#FFFFFF",
                    hover_color=ACCENT_BLUE_HOVER
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=TEXT_SECONDARY,
                    hover_color="#D8E2F0"
                )
        self.on_navigate(page_name)

