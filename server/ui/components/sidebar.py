from typing import Callable
import customtkinter as ctk

from client.ui.theme import *

class ServerSidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate: Callable[[str], None]):
        super().__init__(master, fg_color=BG_SIDEBAR, width=240, corner_radius=0)
        self.on_navigate = on_navigate
        self.active_page = "overview"
        self.buttons = {}

        self._build_sidebar()

    def _build_sidebar(self):
        # Top Header Brand
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(20, 16))

        badge = ctk.CTkLabel(
            brand_frame,
            text="WORKER SERVER",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=ACCENT_PURPLE,
            corner_radius=6,
            padx=8,
            pady=2
        )
        badge.pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            brand_frame,
            text="⚡ GPU Render\nStream Studio",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            justify="left"
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame,
            text="Render Worker Node",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        # Divider
        div = ctk.CTkFrame(self, fg_color=BORDER_COLOR, height=1)
        div.pack(fill="x", padx=16, pady=(12, 14))

        # Navigation Items
        self._add_nav_item("overview", "🏠  Overview", "overview")
        self._add_nav_item("render_queue", "📑  Render Queue", "render_queue")
        self._add_nav_item("activity_logs", "📋  Activity Logs", "activity_logs")
        self._add_nav_item("gpu_engine", "🎮  GPU & Engine", "gpu_engine")
        self._add_nav_item("network", "🌐  Network", "network")
        self._add_nav_item("settings", "⚙️  Settings", "settings")

        # Bottom Server Status Indicator
        status_card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )
        status_card.pack(side="bottom", fill="x", padx=16, pady=18)

        ctk.CTkLabel(
            status_card,
            text="SERVER STATUS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w", padx=14, pady=(10, 2))

        self.lbl_server_status_dot = ctk.CTkLabel(
            status_card,
            text="● Running",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT_GREEN
        )
        self.lbl_server_status_dot.pack(anchor="w", padx=14, pady=(0, 2))

        import platform
        os_name = f"{platform.system()} {platform.release()}"
        ctk.CTkLabel(
            status_card,
            text=f"v1.0.0 • {os_name}",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=14, pady=(0, 10))

    def _add_nav_item(self, key: str, label: str, page_name: str):
        btn = ctk.CTkButton(
            self,
            text=label,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
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

