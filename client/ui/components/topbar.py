from typing import Callable, Optional
import customtkinter as ctk

from client.ui.theme import *

class TopbarHeader(ctk.CTkFrame):
    def __init__(self, master, on_quick_connect: Callable[[], None], on_active_job_click: Optional[Callable[[], None]] = None):
        super().__init__(master, fg_color=BG_CARD, height=65, corner_radius=0, border_width=1, border_color=BORDER_COLOR)
        self.on_quick_connect = on_quick_connect
        self.on_active_job_click = on_active_job_click

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
        self.right_box = ctk.CTkFrame(self, fg_color="transparent")
        self.right_box.pack(side="right", padx=22, pady=12)

        self.btn_job_indicator = ctk.CTkButton(
            self.right_box,
            text="⚡ Job In Progress...",
            command=self._on_active_job_pill_clicked,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFFFFF",
            fg_color=ACCENT_PURPLE,
            hover_color=ACCENT_PURPLE_HOVER,
            corner_radius=8,
            height=32
        )
        # Initially hidden until a job starts

        self.pill_worker = ctk.CTkLabel(
            self.right_box,
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
            self.right_box,
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
            self.right_box,
            text="🔄 Re-Check",
            width=95,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color=TEXT_SECONDARY,
            command=self.on_quick_connect
        )
        self.btn_ping.pack(side="left")

    def _on_active_job_pill_clicked(self):
        if self.on_active_job_click:
            self.on_active_job_click()

    def set_job_active(self, is_active: bool, text: str = "⚡ Job In Progress..."):
        try:
            if is_active:
                self.btn_job_indicator.configure(text=text)
                if not self.btn_job_indicator.winfo_ismapped():
                    self.btn_job_indicator.pack(side="left", before=self.pill_worker, padx=(0, 10))
            else:
                if self.btn_job_indicator.winfo_ismapped():
                    self.btn_job_indicator.pack_forget()
        except Exception:
            pass

    def set_title(self, title: str):
        self.lbl_page_title.configure(text=title)

    def set_status(self, is_online: bool, latency: float = 0, host_info: str = ""):
        if is_online:
            txt = f"● Connected ({host_info})" if host_info else "● Worker Online"
            self.pill_worker.configure(
                text=txt,
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
