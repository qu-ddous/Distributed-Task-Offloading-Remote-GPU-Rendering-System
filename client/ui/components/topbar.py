from typing import Callable
import customtkinter as ctk

from client.ui.theme import *

class TopbarHeader(ctk.CTkFrame):
    def __init__(self, master, on_quick_connect: Callable[[], None]):
        super().__init__(master, fg_color=BG_CARD, height=65, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        self.on_quick_connect = on_quick_connect

        self._build_header()

    def _build_header(self):
        self.pack_propagate(False)

        # Left Page Title & Breadcrumb
        left_box = ctk.CTkFrame(self, fg_color="transparent")
        left_box.pack(side="left", padx=26, pady=12)

        self.lbl_page_title = ctk.CTkLabel(
            left_box,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.lbl_page_title.pack(anchor="w")

        # Right Status Pills (Tactile Clay Badges)
        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.pack(side="right", padx=22, pady=12)

        self.pill_worker = ctk.CTkLabel(
            right_box,
            text="● Worker Offline",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_RED,
            fg_color="#FEE2E2",
            corner_radius=8,
            padx=12,
            pady=4
        )
        self.pill_worker.pack(side="left", padx=(0, 10))

        self.pill_latency = ctk.CTkLabel(
            right_box,
            text="Latency: --",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED,
            fg_color="#F1F5F9",
            corner_radius=8,
            padx=12,
            pady=4
        )
        self.pill_latency.pack(side="left", padx=(0, 12))

        self.btn_ping = ctk.CTkButton(
            right_box,
            text="🔄 Re-Check",
            width=90,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color=TEXT_SECONDARY,
            command=self.on_quick_connect
        )
        self.btn_ping.pack(side="left")

    def set_title(self, title: str):
        self.lbl_page_title.configure(text=title)

    def set_status(self, is_online: bool, latency: float = 0, protocol: str = "v1.0.0"):
        if is_online:
            self.pill_worker.configure(
                text=f"● Worker Online ({protocol})",
                text_color=ACCENT_GREEN,
                fg_color="#D1FAE5"
            )
            lat_color = ACCENT_GREEN if latency < 25 else ACCENT_ORANGE
            lat_bg = "#D1FAE5" if latency < 25 else "#FFEDD5"
            self.pill_latency.configure(
                text=f"Latency: {latency:.1f}ms",
                text_color=lat_color,
                fg_color=lat_bg
            )
        else:
            self.pill_worker.configure(
                text="● Worker Offline",
                text_color=ACCENT_RED,
                fg_color="#FEE2E2"
            )
            self.pill_latency.configure(
                text="Latency: --",
                text_color=TEXT_MUTED,
                fg_color="#F1F5F9"
            )

