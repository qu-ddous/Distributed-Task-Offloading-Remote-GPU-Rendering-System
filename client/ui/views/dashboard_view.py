import tkinter as tk
from typing import Optional
from pathlib import Path
import customtkinter as ctk

from client.ui.theme import *
from client.ui.components.sparkline import CloudGraphicCanvas, MiniGraphCanvas

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_top_banner()
        self._build_hero_section()
        self._build_stats_grid()
        self._build_architecture_and_readiness_cards()
        self._build_remote_hardware_card()

    def _build_top_banner(self):
        self.banner_frame = ctk.CTkFrame(self, fg_color="#FEE2E2", corner_radius=14, border_width=1, border_color="#FCA5A5")
        self.banner_frame.pack(fill="x", padx=10, pady=(0, 14))

        self.lbl_banner = ctk.CTkLabel(
            self.banner_frame,
            text="🔴 WORKER SERVER OFFLINE: Dosra PC connect nahi hai. Host & Settings se IP connect karein.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT_RED,
            padx=16,
            pady=10
        )
        self.lbl_banner.pack(anchor="w")

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
        box.grid_columnconfigure(0, weight=1)
        box.grid_columnconfigure(1, weight=0)

        # Left Info column
        left_col = ctk.CTkFrame(box, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew")

        top_row = ctk.CTkFrame(left_col, fg_color="transparent")
        top_row.pack(fill="x")

        lbl_badge = ctk.CTkLabel(
            top_row,
            text="✨ CLAY STUDIO ULTRA",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=ACCENT_PURPLE,
            corner_radius=6,
            padx=10,
            pady=3
        )
        lbl_badge.pack(side="left")

        lbl_title = ctk.CTkLabel(
            left_col,
            text="Distributed GPU Remote Transcode Studio",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        lbl_title.pack(anchor="w", pady=(8, 4))

        lbl_desc = ctk.CTkLabel(
            left_col,
            text="Seamlessly offload heavy 1080p/4K video encoding from your thin laptop to dedicated NVIDIA NVENC hardware nodes.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        )
        lbl_desc.pack(anchor="w", pady=(0, 14))

        # Action Buttons
        act_row = ctk.CTkFrame(left_col, fg_color="transparent")
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

        # Right Cloud Graphic column
        right_col = ctk.CTkFrame(box, fg_color="transparent")
        right_col.grid(row=0, column=1, padx=(16, 0), sticky="e")
        self.cloud_art = CloudGraphicCanvas(right_col, width=150, height=110)
        self.cloud_art.pack()

    def _build_stats_grid(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=(0, 16))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Remote Worker Node (Emerald/Mint Clay)
        self.card_worker = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.card_worker.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        w_content = ctk.CTkFrame(self.card_worker, fg_color="transparent")
        w_content.pack(fill="both", expand=True, padx=16, pady=16)

        w_top = ctk.CTkFrame(w_content, fg_color="transparent")
        w_top.pack(fill="x", pady=(0, 6))

        # Icon box
        ic1 = ctk.CTkLabel(w_top, text="🌐", font=ctk.CTkFont(size=18), fg_color="#D1FAE5", corner_radius=10, width=38, height=38)
        ic1.pack(side="left", padx=(0, 10))

        w_title_box = ctk.CTkFrame(w_top, fg_color="transparent")
        w_title_box.pack(side="left", fill="both")
        ctk.CTkLabel(w_title_box, text="REMOTE WORKER", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.lbl_worker_val = ctk.CTkLabel(w_title_box, text="Offline", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_RED)
        self.lbl_worker_val.pack(anchor="w")

        self.lbl_worker_sub = ctk.CTkLabel(w_content, text="Awaiting handshake ping", font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.lbl_worker_sub.pack(anchor="w", pady=(4, 0))

        # Card 2: Hardware Acceleration (Rose/Purple Clay)
        self.card_gpu = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.card_gpu.grid(row=0, column=1, sticky="nsew", padx=4)

        g_content = ctk.CTkFrame(self.card_gpu, fg_color="transparent")
        g_content.pack(fill="both", expand=True, padx=16, pady=16)

        g_top = ctk.CTkFrame(g_content, fg_color="transparent")
        g_top.pack(fill="x", pady=(0, 6))

        # Icon box
        ic2 = ctk.CTkLabel(g_top, text="⚡", font=ctk.CTkFont(size=18), fg_color="#EDE9FE", corner_radius=10, width=38, height=38)
        ic2.pack(side="left", padx=(0, 10))

        g_title_box = ctk.CTkFrame(g_top, fg_color="transparent")
        g_title_box.pack(side="left", fill="both")
        ctk.CTkLabel(g_title_box, text="HARDWARE ACCELERATION", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.lbl_gpu_val = ctk.CTkLabel(g_title_box, text="NVENC Missing", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_ORANGE)
        self.lbl_gpu_val.pack(anchor="w")

        self.lbl_gpu_sub = ctk.CTkLabel(g_content, text="CPU fallback mode available", font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.lbl_gpu_sub.pack(anchor="w", pady=(4, 0))

        # Card 3: Network Latency (Amber Clay)
        self.card_net = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.card_net.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        n_content = ctk.CTkFrame(self.card_net, fg_color="transparent")
        n_content.pack(fill="both", expand=True, padx=16, pady=16)

        n_top = ctk.CTkFrame(n_content, fg_color="transparent")
        n_top.pack(fill="x", pady=(0, 6))

        # Icon box
        ic3 = ctk.CTkLabel(n_top, text="📶", font=ctk.CTkFont(size=18), fg_color="#FEF3C7", corner_radius=10, width=38, height=38)
        ic3.pack(side="left", padx=(0, 10))

        n_title_box = ctk.CTkFrame(n_top, fg_color="transparent")
        n_title_box.pack(side="left", fill="both")
        ctk.CTkLabel(n_title_box, text="NETWORK LATENCY", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w")
        self.lbl_latency_val = ctk.CTkLabel(n_title_box, text="-- ms", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_latency_val.pack(anchor="w")

        self.lbl_latency_sub = ctk.CTkLabel(n_content, text="Gigabit / Wi-Fi LAN active", font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.lbl_latency_sub.pack(anchor="w", pady=(4, 0))

    def _build_architecture_and_readiness_cards(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 16))
        row.grid_columnconfigure((0, 1), weight=1)

        # Left: Architecture Pipeline Card
        arch_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        arch_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(arch_card, text="Architecture Pipeline", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 10))

        steps = [
            ("🛡️", "1. Integrity Hashing", "Client computes chunked SHA-256 for non-repudiation.", "#DBEAFE", ACCENT_BLUE),
            ("⬆️", "2. Fast LAN Offload", "High-throughput multipart streaming directly to worker.", "#EDE9FE", ACCENT_PURPLE),
            ("🎬", "3. NVENC Render", "Dedicated NVIDIA GPU transcode with sub-second feedback.", "#D1FAE5", ACCENT_GREEN),
            ("⬇️", "4. Verified Download", "Secure file retrieval with checksum validation.", "#FFEDD5", ACCENT_ORANGE),
        ]
        for icon, title, desc, bg_c, text_c in steps:
            s_box = ctk.CTkFrame(arch_card, fg_color=BG_CARD_ALT, corner_radius=10)
            s_box.pack(fill="x", padx=18, pady=4)
            r = ctk.CTkFrame(s_box, fg_color="transparent")
            r.pack(fill="x", padx=10, pady=8)

            ic = ctk.CTkLabel(r, text=icon, font=ctk.CTkFont(size=14), fg_color=bg_c, corner_radius=8, width=28, height=28)
            ic.pack(side="left", padx=(0, 10))

            t_box = ctk.CTkFrame(r, fg_color="transparent")
            t_box.pack(side="left", fill="both")
            ctk.CTkLabel(t_box, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color=text_c).pack(anchor="w")
            ctk.CTkLabel(t_box, text=desc, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w")

        ctk.CTkFrame(arch_card, fg_color="transparent", height=12).pack()

        # Right: Hardware Readiness Card
        hw_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        hw_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(hw_card, text="Hardware Readiness Status", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 10))

        # 1. Client Laptop
        s1 = ctk.CTkFrame(hw_card, fg_color=BG_CARD_ALT, corner_radius=10)
        s1.pack(fill="x", padx=18, pady=4)
        r1 = ctk.CTkFrame(s1, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(r1, text="💻", font=ctk.CTkFont(size=14), fg_color="#DBEAFE", corner_radius=8, width=28, height=28).pack(side="left", padx=(0, 10))
        t1 = ctk.CTkFrame(r1, fg_color="transparent")
        t1.pack(side="left", fill="both")
        self.lbl_rd_client = ctk.CTkLabel(t1, text="Client Laptop: Online", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_rd_client.pack(anchor="w")
        self.lbl_rd_client_sub = ctk.CTkLabel(t1, text="Local controller daemon active", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_rd_client_sub.pack(anchor="w")

        # 2. Worker Station
        s2 = ctk.CTkFrame(hw_card, fg_color=BG_CARD_ALT, corner_radius=10)
        s2.pack(fill="x", padx=18, pady=4)
        r2 = ctk.CTkFrame(s2, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(r2, text="🖥️", font=ctk.CTkFont(size=14), fg_color="#D1FAE5", corner_radius=8, width=28, height=28).pack(side="left", padx=(0, 10))
        t2 = ctk.CTkFrame(r2, fg_color="transparent")
        t2.pack(side="left", fill="both")
        self.lbl_rd_worker = ctk.CTkLabel(t2, text="Worker Station: Offline", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_RED)
        self.lbl_rd_worker.pack(anchor="w")
        self.lbl_rd_worker_sub = ctk.CTkLabel(t2, text="Awaiting LAN wire connection", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_rd_worker_sub.pack(anchor="w")

        # 3. Network Interconnect
        s3 = ctk.CTkFrame(hw_card, fg_color=BG_CARD_ALT, corner_radius=10)
        s3.pack(fill="x", padx=18, pady=4)
        r3 = ctk.CTkFrame(s3, fg_color="transparent")
        r3.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(r3, text="📶", font=ctk.CTkFont(size=14), fg_color="#FEF3C7", corner_radius=8, width=28, height=28).pack(side="left", padx=(0, 10))
        t3 = ctk.CTkFrame(r3, fg_color="transparent")
        t3.pack(side="left", fill="both")
        self.lbl_rd_net = ctk.CTkLabel(t3, text="Network Link: Disconnected", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_RED)
        self.lbl_rd_net.pack(anchor="w")
        self.lbl_rd_net_sub = ctk.CTkLabel(t3, text="Connect via Ethernet cable or Wi-Fi", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_rd_net_sub.pack(anchor="w")

        # 4. Failover Safety
        s4 = ctk.CTkFrame(hw_card, fg_color=BG_CARD_ALT, corner_radius=10)
        s4.pack(fill="x", padx=18, pady=4)
        r4 = ctk.CTkFrame(s4, fg_color="transparent")
        r4.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(r4, text="🛡️", font=ctk.CTkFont(size=14), fg_color="#EDE9FE", corner_radius=8, width=28, height=28).pack(side="left", padx=(0, 10))
        t4 = ctk.CTkFrame(r4, fg_color="transparent")
        t4.pack(side="left", fill="both")
        self.lbl_rd_failover = ctk.CTkLabel(t4, text="Failover Safety: Armed", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_rd_failover.pack(anchor="w")
        self.lbl_rd_failover_sub = ctk.CTkLabel(t4, text="Automatic CPU fallback ready", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_rd_failover_sub.pack(anchor="w")

        ctk.CTkFrame(hw_card, fg_color="transparent", height=12).pack()

    def _build_remote_hardware_card(self):
        self.card_remote_specs = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            corner_radius=18,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.card_remote_specs.pack(fill="x", padx=10, pady=(0, 16))

        header = ctk.CTkFrame(self.card_remote_specs, fg_color="transparent")
        header.pack(fill="x", padx=22, pady=(18, 12))

        ctk.CTkLabel(
            header,
            text="🖥️  Remote Server Specifications & Live Hardware Monitor",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        self.lbl_telem_live_badge = ctk.CTkLabel(
            header,
            text="● Node Offline",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ACCENT_RED,
            fg_color="#FEE2E2",
            corner_radius=6,
            padx=10,
            pady=3
        )
        self.lbl_telem_live_badge.pack(side="right")

        # 2x2 Info Grid
        grid = ctk.CTkFrame(self.card_remote_specs, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=(0, 20))
        grid.grid_columnconfigure((0, 1), weight=1)

        # 1. Host Identity & OS
        b1 = ctk.CTkFrame(grid, fg_color=BG_CARD_ALT, corner_radius=12)
        b1.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        ctk.CTkLabel(b1, text="REMOTE MACHINE & OS", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 2))
        self.lbl_hw_host = ctk.CTkLabel(b1, text="Node: Disconnected", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_hw_host.pack(anchor="w", padx=16, pady=(0, 2))
        self.lbl_hw_os = ctk.CTkLabel(b1, text="OS: Awaiting Connection", font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY)
        self.lbl_hw_os.pack(anchor="w", padx=16, pady=(0, 12))

        # 2. Remote CPU & Live Usage
        b2 = ctk.CTkFrame(grid, fg_color=BG_CARD_ALT, corner_radius=12)
        b2.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))
        ctk.CTkLabel(b2, text="REMOTE CPU & COMPUTE LOAD", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 2))
        self.lbl_hw_cpu_name = ctk.CTkLabel(b2, text="Processor: Unknown", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_hw_cpu_name.pack(anchor="w", padx=16, pady=(0, 2))
        self.lbl_hw_cpu_load = ctk.CTkLabel(b2, text="CPU Usage: --%", font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY)
        self.lbl_hw_cpu_load.pack(anchor="w", padx=16, pady=(0, 4))
        self.bar_hw_cpu = ctk.CTkProgressBar(b2, height=8, corner_radius=4, fg_color="#E2E8F0", progress_color=ACCENT_BLUE)
        self.bar_hw_cpu.set(0.0)
        self.bar_hw_cpu.pack(fill="x", padx=16, pady=(0, 12))

        # 3. Remote RAM & Memory
        b3 = ctk.CTkFrame(grid, fg_color=BG_CARD_ALT, corner_radius=12)
        b3.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(b3, text="REMOTE RAM / MEMORY USAGE", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 2))
        self.lbl_hw_ram_val = ctk.CTkLabel(b3, text="Memory: -- / -- GB", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_hw_ram_val.pack(anchor="w", padx=16, pady=(0, 2))
        self.lbl_hw_ram_sub = ctk.CTkLabel(b3, text="RAM Load: --%", font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY)
        self.lbl_hw_ram_sub.pack(anchor="w", padx=16, pady=(0, 4))
        self.bar_hw_ram = ctk.CTkProgressBar(b3, height=8, corner_radius=4, fg_color="#E2E8F0", progress_color=ACCENT_PURPLE)
        self.bar_hw_ram.set(0.0)
        self.bar_hw_ram.pack(fill="x", padx=16, pady=(0, 12))

        # 4. Acceleration GPU / Storage
        b4 = ctk.CTkFrame(grid, fg_color=BG_CARD_ALT, corner_radius=12)
        b4.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(b4, text="HARDWARE ENCODER & STORAGE", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 2))
        self.lbl_hw_gpu_full = ctk.CTkLabel(b4, text="GPU: Awaiting Hardware Query", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_hw_gpu_full.pack(anchor="w", padx=16, pady=(0, 2))
        self.lbl_hw_disk = ctk.CTkLabel(b4, text="Render Cache Storage: -- GB Free", font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY)
        self.lbl_hw_disk.pack(anchor="w", padx=16, pady=(0, 12))

    def on_page_shown(self):
        """Called whenever user switches to the Dashboard tab."""
        self.update_status(
            self.app.is_connected,
            getattr(self.app, "last_latency", 0.0),
            self.app.health_data
        )

    def update_status(self, is_online: bool, latency: float = 0, health_data: Optional[dict] = None):
        if is_online:
            self.banner_frame.configure(fg_color="#D1FAE5", border_color="#86EFAC")
            self.lbl_banner.configure(
                text="✅ WORKER SERVER ONLINE: Remote hardware node connected. Telemetry streaming active.",
                text_color=ACCENT_GREEN
            )
            self.lbl_worker_val.configure(text="Online", text_color=ACCENT_GREEN)
            proto = health_data.get("protocol_version", "v1.0.0") if health_data else "v1.0.0"
            self.lbl_worker_sub.configure(text=f"Protocol {proto} handshake verified")

            lat_color = ACCENT_GREEN if latency < 25 else ACCENT_ORANGE
            self.lbl_latency_val.configure(text=f"{latency:.1f} ms", text_color=lat_color)
            self.lbl_latency_sub.configure(text="Gigabit / Wi-Fi LAN active")

            self.lbl_telem_live_badge.configure(text="● Live Telemetry Active", text_color=ACCENT_GREEN, fg_color="#D1FAE5")

            # Update Readiness Card
            self.lbl_rd_net.configure(text=f"Network Link: {latency:.1f} ms Active", text_color=ACCENT_GREEN)
            self.lbl_rd_net_sub.configure(text="High-throughput LAN Link Verified")

            if health_data:
                ff = health_data.get("ffmpeg", {})
                hw = health_data.get("hardware", {})
                nvenc = ff.get("nvenc_available", False)
                gpu_name = hw.get("gpu_name")

                # Update Stat Card 2
                if nvenc:
                    self.lbl_gpu_val.configure(text="NVENC Ready", text_color=ACCENT_GREEN)
                    self.lbl_gpu_sub.configure(text=gpu_name[:26] if gpu_name else "Dedicated NVIDIA Hardware Node")
                    self.lbl_rd_worker.configure(text=f"Worker Station: {gpu_name[:22] if gpu_name else 'NVENC Ready'}", text_color=ACCENT_GREEN)
                    self.lbl_rd_worker_sub.configure(text="NVIDIA NVENC Hardware Ready")
                else:
                    self.lbl_gpu_val.configure(text="NVENC Missing", text_color=ACCENT_ORANGE)
                    self.lbl_gpu_sub.configure(text="CPU fallback mode available")
                    self.lbl_rd_worker.configure(text="Worker Station: CPU Mode", text_color=ACCENT_ORANGE)
                    self.lbl_rd_worker_sub.configure(text="Multi-Core CPU Fallback Active")

                # Update Detailed Remote Specs Card
                self.lbl_hw_host.configure(text=f"Node: {hw.get('hostname', 'Remote Worker')}")
                self.lbl_hw_os.configure(text=f"OS: {hw.get('os_platform', 'Windows')}")

                cores = hw.get("cpu_cores", 1)
                cpu_name = hw.get("cpu_model", "Standard CPU")
                cpu_pct = hw.get("cpu_percent", 0.0)
                self.lbl_hw_cpu_name.configure(text=f"{cpu_name[:36]} ({cores} Cores)")
                self.lbl_hw_cpu_load.configure(text=f"Live Remote CPU Load: {cpu_pct:.1f}%")
                self.bar_hw_cpu.set(min(1.0, max(0.02, cpu_pct / 100.0)))

                ram_tot = hw.get("ram_total_gb", 0.0)
                ram_used = hw.get("ram_used_gb", 0.0)
                ram_pct = hw.get("ram_percent", 0.0)
                self.lbl_hw_ram_val.configure(text=f"RAM: {ram_used:.1f} GB Used / {ram_tot:.1f} GB Total")
                self.lbl_hw_ram_sub.configure(text=f"Memory Consumption: {ram_pct:.1f}%")
                self.bar_hw_ram.set(min(1.0, max(0.02, ram_pct / 100.0)))

                if nvenc and gpu_name:
                    vram_mb = hw.get("gpu_vram_total_mb")
                    vram_txt = f" ({vram_mb // 1024} GB VRAM)" if vram_mb else ""
                    self.lbl_hw_gpu_full.configure(text=f"GPU: {gpu_name}{vram_txt} [NVENC Ready]", text_color=ACCENT_GREEN)
                else:
                    self.lbl_hw_gpu_full.configure(text="GPU: None / Integrated [CPU Multi-Core Mode Active]", text_color=TEXT_PRIMARY)

                free_bytes = hw.get("disk_free_bytes", 0)
                free_gb = free_bytes / (1024 ** 3)
                self.lbl_hw_disk.configure(text=f"Render Storage: {free_gb:.1f} GB Free on Remote PC")
            else:
                self.lbl_rd_worker.configure(text="Worker Station: Connected", text_color=ACCENT_GREEN)
                self.lbl_rd_worker_sub.configure(text="Remote Node Handshake Verified")
        else:
            self.banner_frame.configure(fg_color="#FEE2E2", border_color="#FCA5A5")
            self.lbl_banner.configure(
                text="🔴 WORKER SERVER OFFLINE: Dosra PC connect nahi hai. Host & Settings se IP connect karein.",
                text_color=ACCENT_RED
            )
            self.lbl_worker_val.configure(text="Offline", text_color=ACCENT_RED)
            self.lbl_worker_sub.configure(text="Check IP, port or start daemon")
            self.lbl_gpu_val.configure(text="NVENC Missing", text_color=ACCENT_ORANGE)
            self.lbl_gpu_sub.configure(text="CPU fallback mode available")
            self.lbl_latency_val.configure(text="-- ms", text_color=TEXT_MUTED)
            self.lbl_latency_sub.configure(text="Gigabit / Wi-Fi LAN active")

            # Update Readiness Card
            self.lbl_rd_worker.configure(text="Worker Station: Offline", text_color=ACCENT_RED)
            self.lbl_rd_worker_sub.configure(text="Awaiting LAN wire connection to Server")
            self.lbl_rd_net.configure(text="Network Link: Disconnected", text_color=ACCENT_RED)
            self.lbl_rd_net_sub.configure(text="Connect via Ethernet cable or Wi-Fi")

            self.lbl_telem_live_badge.configure(text="● Node Offline", text_color=ACCENT_RED, fg_color="#FEE2E2")
            self.lbl_hw_host.configure(text="Node: Disconnected")
            self.lbl_hw_os.configure(text="OS: Awaiting Connection")
            self.lbl_hw_cpu_name.configure(text="Processor: Unknown")
            self.lbl_hw_cpu_load.configure(text="CPU Usage: --%")
            self.bar_hw_cpu.set(0.0)
            self.lbl_hw_ram_val.configure(text="Memory: -- / -- GB")
            self.lbl_hw_ram_sub.configure(text="RAM Load: --%")
            self.bar_hw_ram.set(0.0)
            self.lbl_hw_gpu_full.configure(text="GPU: Awaiting Hardware Query", text_color=TEXT_PRIMARY)
            self.lbl_hw_disk.configure(text="Render Cache Storage: -- GB Free")
