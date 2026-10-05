from typing import Callable
import customtkinter as ctk

from client.ui.theme import *

class SidebarNavigation(ctk.CTkFrame):
    def __init__(self, master, on_navigate: Callable[[str], None]):
        super().__init__(master, fg_color=BG_SIDEBAR, width=230, corner_radius=0)
        self.on_navigate = on_navigate
        self.active_page = "dashboard"
        self.buttons = {}

        self._build_sidebar()

    def _build_sidebar(self):
        # App Brand Header
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(24, 28))

        ctk.CTkLabel(
            brand_frame,
            text="⚡ GPU STUDIO",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame,
            text="Distributed Offload System",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_DIM
        ).pack(anchor="w")

        # Navigation Buttons
        self._add_nav_item("dashboard", "📊 Dashboard", "dashboard")
        self._add_nav_item("render_job", "🎬 New Render Job", "render_job")
        self._add_nav_item("active_job", "📡 Active Job Monitor", "active_job")
        self._add_nav_item("settings", "⚙ Settings & Host", "settings")

        # Bottom System Info Badge
        info_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=8)
        info_frame.pack(side="bottom", fill="x", padx=16, pady=20)

        ctk.CTkLabel(
            info_frame,
            text="CORE ENGINE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            info_frame,
            text="NVIDIA NVENC v1.0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ACCENT_GREEN
        ).pack(anchor="w", padx=12, pady=(0, 10))

    def _add_nav_item(self, key: str, label: str, page_name: str):
        btn = ctk.CTkButton(
            self,
            text=label,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            corner_radius=8,
            fg_color="transparent",
            text_color=TEXT_SECONDARY,
            hover_color=BG_CARD,
            command=lambda: self._select_nav(page_name)
        )
        btn.pack(fill="x", padx=12, pady=4)
        self.buttons[page_name] = btn

    def _select_nav(self, page_name: str):
        self.active_page = page_name
        for name, btn in self.buttons.items():
            if name == page_name:
                btn.configure(fg_color=ACCENT_BLUE, text_color=TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
        self.on_navigate(page_name)

    def set_active(self, page_name: str):
        self._select_nav(page_name)
