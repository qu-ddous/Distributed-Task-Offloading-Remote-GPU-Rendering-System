from typing import Callable, Optional
import customtkinter as ctk

from client.ui.theme import *

class TopbarHeader(ctk.CTkFrame):
    def __init__(self, master, on_quick_connect: Callable[[], None]):
        super().__init__(master, fg_color=BG_CARD, height=60, corner_radius=0)
        self.on_quick_connect = on_quick_connect

        self._build_header()

    def _build_header(self):
        self.pack_propagate(False)

        # Left Title
        self.lbl_page_title = ctk.CTkLabel(
            self,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.lbl_page_title.pack(side="left", padx=24, pady=16)

        # Right Status Indicators
        right_box = ctk.CTkFrame(self, fg_color="transparent")
        right_box.pack(side="right", padx=20, pady=12)

        self.lbl_conn_indicator = ctk.CTkLabel(
            right_box,
            text="● Worker: Offline",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_RED
        )
        self.lbl_conn_indicator.pack(side="left", padx=(0, 14))

        self.lbl_latency_indicator = ctk.CTkLabel(
            right_box,
            text="Latency: --",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        self.lbl_latency_indicator.pack(side="left", padx=(0, 14))

        self.btn_ping = ctk.CTkButton(
            right_box,
            text="🔄 Re-Check",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2A3144",
            hover_color="#374151",
            command=self.on_quick_connect
        )
        self.btn_ping.pack(side="left")

    def set_title(self, title: str):
        self.lbl_page_title.configure(text=title)

    def set_status(self, is_online: bool, latency: float = 0, protocol: str = "v1.0.0"):
        if is_online:
            self.lbl_conn_indicator.configure(text=f"● Worker: Online ({protocol})", text_color=ACCENT_GREEN)
            self.lbl_latency_indicator.configure(text=f"Latency: {latency:.1f}ms", text_color=TEXT_SECONDARY)
        else:
            self.lbl_conn_indicator.configure(text="● Worker: Offline", text_color=ACCENT_RED)
            self.lbl_latency_indicator.configure(text="Latency: --", text_color=TEXT_MUTED)
