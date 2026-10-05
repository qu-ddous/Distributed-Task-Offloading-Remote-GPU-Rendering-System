from typing import Optional
import customtkinter as ctk

from client.ui.theme import *

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_hero_section()
        self._build_stats_grid()
        self._build_activity_cards()

    def _build_hero_section(self):
        hero = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDER_COLOR
        )
        hero.pack(fill="x", padx=10, pady=(0, 16))

        box = ctk.CTkFrame(hero, fg_color="transparent")
        box.pack(fill="x", padx=26, pady=22)

        top_row = ctk.CTkFrame(box, fg_color="transparent")
        top_row.pack(fill="x")

        lbl_badge = ctk.CTkLabel(
            top_row,
            text="✨ CLAY STUDIO ULTRA",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=ACCENT_BLUE,
            corner_radius=6,
            padx=10,
            pady=3
        )
        lbl_badge.pack(side="left")

        lbl_title = ctk.CTkLabel(
            box,
            text="Distributed GPU Remote Transcode Studio",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        lbl_title.pack(anchor="w", pady=(8, 4))

        lbl_desc = ctk.CTkLabel(
            box,
            text="Seamlessly offload heavy 1080p/4K video encoding from your thin laptop to dedicated NVIDIA NVENC hardware nodes.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        lbl_desc.pack(anchor="w", pady=(0, 14))

        # Quick action pills
        act_row = ctk.CTkFrame(box, fg_color="transparent")
        act_row.pack(fill="x")

        btn_new_job = ctk.CTkButton(
            act_row,
            text="🎬  Start New Render Job",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            corner_radius=10,
            height=38,
            command=lambda: self.app.navigate_to("render_job")
        )
        btn_new_job.pack(side="left", padx=(0, 10))

        btn_bench = ctk.CTkButton(
            act_row,
            text="⚡  Run Benchmark Suite",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=38,
            command=lambda: self.app.navigate_to("benchmarks")
        )
        btn_bench.pack(side="left")

    def _build_stats_grid(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=(0, 16))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Worker Node (Emerald Clay)
        self.card_worker = ctk.CTkFrame(
            grid,
            fg_color=BG_CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.card_worker.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(self.card_worker, text="REMOTE WORKER", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(16, 4))
        self.lbl_worker_val = ctk.CTkLabel(self.card_worker, text="● Offline", font=ctk.CTkFont(size=20, weight="bold"), text_color=ACCENT_RED)
        self.lbl_worker_val.pack(anchor="w", padx=20, pady=(0, 2))
        self.lbl_worker_sub = ctk.CTkLabel(self.card_worker, text="Awaiting handshake ping", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.lbl_worker_sub.pack(anchor="w", padx=20, pady=(0, 16))

        # Card 2: GPU NVENC (Purple Clay)
        self.card_gpu = ctk.CTkFrame(
            grid,
            fg_color=BG_CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.card_gpu.grid(row=0, column=1, sticky="nsew", padx=4)

        ctk.CTkLabel(self.card_gpu, text="HARDWARE ACCELERATION", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(16, 4))
        self.lbl_gpu_val = ctk.CTkLabel(self.card_gpu, text="NVENC: Unknown", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_gpu_val.pack(anchor="w", padx=20, pady=(0, 2))
        self.lbl_gpu_sub = ctk.CTkLabel(self.card_gpu, text="NVIDIA h264_nvenc detection", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.lbl_gpu_sub.pack(anchor="w", padx=20, pady=(0, 16))

        # Card 3: Network Latency (Cyan Clay)
        self.card_net = ctk.CTkFrame(
            grid,
            fg_color=BG_CARD,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.card_net.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(self.card_net, text="NETWORK LATENCY", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(16, 4))
        self.lbl_latency_val = ctk.CTkLabel(self.card_net, text="-- ms", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_latency_val.pack(anchor="w", padx=20, pady=(0, 2))
        self.lbl_latency_sub = ctk.CTkLabel(self.card_net, text="Round-trip handshake ping", font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
        self.lbl_latency_sub.pack(anchor="w", padx=20, pady=(0, 16))

    def _build_activity_cards(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 16))
        row.grid_columnconfigure((0, 1), weight=1)

        # Left Info: System Architecture
        arch_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        arch_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(arch_card, text="Architecture Pipeline", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 8))

        steps = [
            ("1. Integrity Hashing", "Client computes chunked SHA-256 for non-repudiation.", ACCENT_BLUE),
            ("2. Fast LAN Offload", "High-throughput multipart streaming directly to worker.", ACCENT_PURPLE),
            ("3. NVENC Render", "Dedicated NVIDIA GPU transcode with sub-second feedback.", ACCENT_GREEN),
            ("4. Verified Download", "Download stream with cryptographic SHA-256 validation.", ACCENT_ORANGE),
        ]
        for title, desc, clr in steps:
            s_box = ctk.CTkFrame(arch_card, fg_color=BG_CARD_ALT, corner_radius=10)
            s_box.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(s_box, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=clr).pack(anchor="w", padx=12, pady=(6, 1))
            ctk.CTkLabel(s_box, text=desc, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(0, 6))

        # Bottom space
        ctk.CTkFrame(arch_card, fg_color="transparent", height=10).pack()

        # Right Info: Hardware Requirements
        hw_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        hw_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(hw_card, text="Hardware Readiness", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 8))

        specs = [
            ("Client Laptop", "Any lightweight CPU (Python 3.11+, Tkinter, CustomTkinter)", "#1E293B"),
            ("Worker Station", "NVIDIA RTX/GTX GPU, Driver 520+, FFmpeg 6.0+ compiled with nvenc", "#1E293B"),
            ("Network Interconnect", "Gigabit Ethernet or Wi-Fi 6 for maximum file transfer speed", "#1E293B"),
            ("Failover Safety", "Optional CPU fallback (libx264) when GPU is unavailable", "#1E293B"),
        ]
        for title, desc, clr in specs:
            s_box = ctk.CTkFrame(hw_card, fg_color=BG_CARD_ALT, corner_radius=10)
            s_box.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(s_box, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=12, pady=(6, 1))
            ctk.CTkLabel(s_box, text=desc, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(0, 6))

        ctk.CTkFrame(hw_card, fg_color="transparent", height=10).pack()

    def update_status(self, is_online: bool, latency: float = 0, health_data: Optional[dict] = None):
        if is_online:
            self.lbl_worker_val.configure(text="● Online", text_color=ACCENT_GREEN)
            proto = health_data.get("protocol_version", "v1.0.0") if health_data else "v1.0.0"
            self.lbl_worker_sub.configure(text=f"Protocol {proto} handshake verified")

            self.lbl_latency_val.configure(text=f"{latency:.1f} ms", text_color=ACCENT_GREEN if latency < 25 else ACCENT_ORANGE)
            self.lbl_latency_sub.configure(text="Gigabit / Wi-Fi LAN active")

            if health_data:
                ff = health_data.get("ffmpeg", {})
                hw = health_data.get("hardware", {})
                nvenc = ff.get("nvenc_available", False)
                if nvenc:
                    gpu_name = hw.get("gpu_name") or "NVIDIA GPU Detected"
                    self.lbl_gpu_val.configure(text="● Ready", text_color=ACCENT_GREEN)
                    self.lbl_gpu_sub.configure(text=gpu_name[:28])
                else:
                    self.lbl_gpu_val.configure(text="● NVENC Missing", text_color=ACCENT_RED)
                    self.lbl_gpu_sub.configure(text="CPU fallback mode available")
        else:
            self.lbl_worker_val.configure(text="● Offline", text_color=ACCENT_RED)
            self.lbl_worker_sub.configure(text="Check IP, port or start daemon")
            self.lbl_gpu_val.configure(text="NVENC: Unknown", text_color=TEXT_MUTED)
            self.lbl_gpu_sub.configure(text="Connect to inspect hardware")
            self.lbl_latency_val.configure(text="-- ms", text_color=TEXT_MUTED)
            self.lbl_latency_sub.configure(text="Round-trip handshake ping")

