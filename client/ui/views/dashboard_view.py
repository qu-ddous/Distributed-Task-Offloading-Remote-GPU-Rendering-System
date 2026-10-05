import threading
from typing import Optional, Dict, Any
from pathlib import Path
import customtkinter as ctk

from client.ui.theme import *
from client.services.network_client import NetworkClient

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_hero_section()
        self._build_stats_grid()
        self._build_quick_actions()

    def _build_hero_section(self):
        hero_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        hero_card.pack(fill="x", padx=10, pady=(0, 15))

        title_box = ctk.CTkFrame(hero_card, fg_color="transparent")
        title_box.pack(side="left", padx=25, pady=22)

        lbl_badge = ctk.CTkLabel(
            title_box,
            text="STUDIO EDITION v1.0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ACCENT_BLUE
        )
        lbl_badge.pack(anchor="w")

        lbl_title = ctk.CTkLabel(
            title_box,
            text="Distributed GPU Render Studio",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        lbl_title.pack(anchor="w", pady=(2, 4))

        lbl_desc = ctk.CTkLabel(
            title_box,
            text="Offload heavy video transcode & render tasks to remote NVIDIA NVENC hardware over LAN.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        lbl_desc.pack(anchor="w")

    def _build_stats_grid(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=(0, 15))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Worker Status
        self.card_worker = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.card_worker.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        ctk.CTkLabel(self.card_worker, text="WORKER NODE", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(16, 4))
        self.lbl_worker_val = ctk.CTkLabel(self.card_worker, text="● Offline", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_RED)
        self.lbl_worker_val.pack(anchor="w", padx=18, pady=(0, 4))
        self.lbl_worker_sub = ctk.CTkLabel(self.card_worker, text="No active handshake", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.lbl_worker_sub.pack(anchor="w", padx=18, pady=(0, 16))

        # Card 2: GPU NVENC
        self.card_gpu = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.card_gpu.grid(row=0, column=1, sticky="nsew", padx=4, pady=0)

        ctk.CTkLabel(self.card_gpu, text="GPU ACCELERATION", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(16, 4))
        self.lbl_gpu_val = ctk.CTkLabel(self.card_gpu, text="NVENC: Unknown", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_gpu_val.pack(anchor="w", padx=18, pady=(0, 4))
        self.lbl_gpu_sub = ctk.CTkLabel(self.card_gpu, text="Connect to inspect hardware", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.lbl_gpu_sub.pack(anchor="w", padx=18, pady=(0, 16))

        # Card 3: Network Latency
        self.card_net = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.card_net.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=0)

        ctk.CTkLabel(self.card_net, text="NETWORK LATENCY", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=18, pady=(16, 4))
        self.lbl_latency_val = ctk.CTkLabel(self.card_net, text="-- ms", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_latency_val.pack(anchor="w", padx=18, pady=(0, 4))
        self.lbl_latency_sub = ctk.CTkLabel(self.card_net, text="LAN round-trip ping", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.lbl_latency_sub.pack(anchor="w", padx=18, pady=(0, 16))

    def _build_quick_actions(self):
        actions_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        actions_card.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(actions_card, text="Quick Navigation", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 12))

        btn_row = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        btn_new_job = ctk.CTkButton(
            btn_row,
            text="⚡ Create New Render Job",
            command=lambda: self.app.navigate_to("render_job"),
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_new_job.pack(side="left", padx=(0, 12))

        btn_monitor = ctk.CTkButton(
            btn_row,
            text="📊 Open Live Monitor",
            command=lambda: self.app.navigate_to("active_job"),
            fg_color="#374151",
            hover_color="#4B5563",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        btn_monitor.pack(side="left", padx=(0, 12))

        btn_settings = ctk.CTkButton(
            btn_row,
            text="⚙ Connection & Settings",
            command=lambda: self.app.navigate_to("settings"),
            fg_color="#374151",
            hover_color="#4B5563",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        btn_settings.pack(side="left")

    def update_status(self, is_online: bool, latency: float = 0, health_data: Optional[dict] = None):
        if is_online:
            self.lbl_worker_val.configure(text="● Online", text_color=ACCENT_GREEN)
            proto = health_data.get("protocol_version", "v1.0.0") if health_data else "v1.0.0"
            self.lbl_worker_sub.configure(text=f"Protocol {proto}")

            self.lbl_latency_val.configure(text=f"{latency:.1f} ms", text_color=ACCENT_GREEN if latency < 20 else ACCENT_YELLOW)
            self.lbl_latency_sub.configure(text="Excellent LAN quality" if latency < 20 else "Normal LAN latency")

            if health_data:
                ff = health_data.get("ffmpeg", {})
                hw = health_data.get("hardware", {})
                nvenc = ff.get("nvenc_available", False)
                if nvenc:
                    gpu_name = hw.get("gpu_name") or "NVIDIA GPU Detected"
                    self.lbl_gpu_val.configure(text="● Ready", text_color=ACCENT_GREEN)
                    self.lbl_gpu_sub.configure(text=gpu_name[:24])
                else:
                    self.lbl_gpu_val.configure(text="● NVENC Missing", text_color=ACCENT_RED)
                    self.lbl_gpu_sub.configure(text="CPU fallback available")
        else:
            self.lbl_worker_val.configure(text="● Offline", text_color=ACCENT_RED)
            self.lbl_worker_sub.configure(text="Connection failed")
            self.lbl_gpu_val.configure(text="NVENC: Unknown", text_color=TEXT_MUTED)
            self.lbl_gpu_sub.configure(text="Connect to inspect hardware")
            self.lbl_latency_val.configure(text="-- ms", text_color=TEXT_MUTED)
            self.lbl_latency_sub.configure(text="LAN round-trip ping")
