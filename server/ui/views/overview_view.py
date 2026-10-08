import time
import customtkinter as ctk

from client.ui.theme import *
from server.ui.components.sparkline import MiniGraphCanvas
from server.app.services.system_service import SystemService
from server.app.services.job_manager import job_manager
from server.ui.log_bus import server_log_bus
from server.app.config import settings

class ServerOverviewView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_metric_cards()
        self._build_middle_row()
        self._build_bottom_row()

        # Instantly pre-seed static hardware info on frame 0 (<5ms)
        try:
            static = SystemService.get_static_specs()
            self.lbl_cpu_status.configure(text=f"{static['cpu_model'][:26]} ({static['cpu_cores']}C)")
            self.lbl_sys_ram.configure(text=f"-- / {static['ram_total_gb']} GB")
            self.lbl_net_sub.configure(text=f"{static['primary_ip']}:{settings.PORT}")
        except Exception:
            pass

        self._last_act_count = 0
        self._refresh_telemetry()

    def on_page_shown(self):
        """Immediately update telemetry when navigated to."""
        self._refresh_telemetry()

    def _build_metric_cards(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=4, pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # 1. GPU Utilization
        c1 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        
        top1 = ctk.CTkFrame(c1, fg_color="transparent")
        top1.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(top1, text="🖥️ GPU Utilization", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")
        
        self.lbl_gpu_val = ctk.CTkLabel(c1, text="--%", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_gpu_val.pack(anchor="w", padx=14, pady=(0, 2))

        self.lbl_gpu_name = ctk.CTkLabel(c1, text="Querying Hardware...", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_gpu_name.pack(anchor="w", padx=14, pady=(0, 6))

        self.bar_gpu = ctk.CTkProgressBar(c1, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=ACCENT_BLUE)
        self.bar_gpu.set(0.0)
        self.bar_gpu.pack(fill="x", padx=14, pady=(0, 12))

        # 2. GPU VRAM Usage
        c2 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c2.grid(row=0, column=1, sticky="nsew", padx=4)

        top2 = ctk.CTkFrame(c2, fg_color="transparent")
        top2.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(top2, text="💾 GPU VRAM Usage", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        self.lbl_vram_val = ctk.CTkLabel(c2, text="-- / -- GB", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_vram_val.pack(anchor="w", padx=14, pady=(0, 2))

        self.lbl_vram_pct = ctk.CTkLabel(c2, text="--% used", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_vram_pct.pack(anchor="w", padx=14, pady=(0, 6))

        self.bar_vram = ctk.CTkProgressBar(c2, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=ACCENT_GREEN)
        self.bar_vram.set(0.0)
        self.bar_vram.pack(fill="x", padx=14, pady=(0, 12))

        # 3. GPU Temperature
        c3 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c3.grid(row=0, column=2, sticky="nsew", padx=4)

        top3 = ctk.CTkFrame(c3, fg_color="transparent")
        top3.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(top3, text="🌡️ GPU Temperature", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        self.lbl_temp_val = ctk.CTkLabel(c3, text="-- °C", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_temp_val.pack(anchor="w", padx=14, pady=(0, 2))

        self.lbl_temp_status = ctk.CTkLabel(c3, text="Normal Range", font=ctk.CTkFont(size=11), text_color=ACCENT_ORANGE)
        self.lbl_temp_status.pack(anchor="w", padx=14, pady=(0, 6))

        self.bar_temp = ctk.CTkProgressBar(c3, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=ACCENT_ORANGE)
        self.bar_temp.set(0.3)
        self.bar_temp.pack(fill="x", padx=14, pady=(0, 12))

        # 4. CPU Fallback / Usage
        c4 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c4.grid(row=0, column=3, sticky="nsew", padx=4)

        top4 = ctk.CTkFrame(c4, fg_color="transparent")
        top4.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(top4, text="⚙️ CPU Load", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        self.lbl_cpu_val = ctk.CTkLabel(c4, text="--%", font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_cpu_val.pack(anchor="w", padx=14, pady=(0, 2))

        self.lbl_cpu_status = ctk.CTkLabel(c4, text="Multi-Core Ready", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_cpu_status.pack(anchor="w", padx=14, pady=(0, 6))

        self.bar_cpu = ctk.CTkProgressBar(c4, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=ACCENT_PURPLE)
        self.bar_cpu.set(0.05)
        self.bar_cpu.pack(fill="x", padx=14, pady=(0, 12))

        # 5. Network Latency
        c5 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c5.grid(row=0, column=4, sticky="nsew", padx=(6, 0))

        top5 = ctk.CTkFrame(c5, fg_color="transparent")
        top5.pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(top5, text="📶 Network Daemon", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        self.lbl_net_val = ctk.CTkLabel(c5, text="Online", font=ctk.CTkFont(size=20, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_net_val.pack(anchor="w", padx=14, pady=(0, 2))

        real_ip = SystemService.get_primary_ip()
        self.lbl_net_sub = ctk.CTkLabel(c5, text=f"{real_ip}:{settings.PORT}", font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_net_sub.pack(anchor="w", padx=14, pady=(0, 6))

        self.bar_net = ctk.CTkProgressBar(c5, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=ACCENT_GREEN)
        self.bar_net.set(1.0)
        self.bar_net.pack(fill="x", padx=14, pady=(0, 12))

    def _build_middle_row(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(0, 14))
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        # Left Card: Active Render Job
        self.active_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.active_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        top = ctk.CTkFrame(self.active_card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 4))
        
        ctk.CTkLabel(top, text="📄  Active Render Job", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_active_badge = ctk.CTkLabel(
            top,
            text="IDLE / READY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color="#64748B",
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.lbl_active_badge.pack(side="right")

        self.lbl_active_file = ctk.CTkLabel(
            self.active_card,
            text="No render job active. Ready for client submission.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.lbl_active_file.pack(anchor="w", padx=18, pady=(4, 2))

        self.lbl_active_meta = ctk.CTkLabel(
            self.active_card,
            text="Awaiting video tasks from connected client studio...",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.lbl_active_meta.pack(anchor="w", padx=18, pady=(0, 8))

        # Progress bar
        p_row = ctk.CTkFrame(self.active_card, fg_color="transparent")
        p_row.pack(fill="x", padx=18, pady=(0, 8))
        self.bar_active = ctk.CTkProgressBar(p_row, height=8, corner_radius=4, fg_color="#E2E8F0", progress_color=ACCENT_BLUE)
        self.bar_active.set(0.0)
        self.bar_active.pack(side="left", fill="x", expand=True)
        self.lbl_pct_val = ctk.CTkLabel(p_row, text=" 0%", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_pct_val.pack(side="left")

        # Stage box
        self.stage_box = ctk.CTkFrame(self.active_card, fg_color=BG_CARD_ALT, corner_radius=10)
        self.stage_box.pack(fill="x", padx=18, pady=(0, 10))
        self.lbl_stage_txt = ctk.CTkLabel(self.stage_box, text="● Worker daemon listening on port 8000", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY)
        self.lbl_stage_txt.pack(anchor="w", padx=12, pady=6)

        # Meta pills
        meta_row = ctk.CTkFrame(self.active_card, fg_color="transparent")
        meta_row.pack(fill="x", padx=18, pady=(0, 14))
        self.lbl_meta_elapsed = self._add_meta_pill(meta_row, "🕒 Elapsed Time", "--:--")
        self.lbl_meta_total = self._add_meta_pill(meta_row, "⏱ Total Time", "--:--")
        self.lbl_meta_output = self._add_meta_pill(meta_row, "📁 Cache Storage", "storage/jobs")

        # Right Card: Render Queue Preview
        self.queue_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.queue_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        q_top = ctk.CTkFrame(self.queue_card, fg_color="transparent")
        q_top.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(q_top, text="📋  Render Queue", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_q_summary = ctk.CTkLabel(q_top, text="0 jobs", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_q_summary.pack(side="right")

        self.queue_list_container = ctk.CTkFrame(self.queue_card, fg_color="transparent")
        self.queue_list_container.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _add_meta_pill(self, parent, title, val):
        box = ctk.CTkFrame(parent, fg_color=BG_CARD_ALT, corner_radius=8)
        box.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(box, text=f"{title}: ", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(side="left", padx=(8, 0), pady=4)
        lbl = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_PRIMARY)
        lbl.pack(side="left", padx=(0, 8), pady=4)
        return lbl

    def _build_bottom_row(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(0, 14))
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        # Left Card: Recent Activity
        self.activity_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.activity_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        act_top = ctk.CTkFrame(self.activity_card, fg_color="transparent")
        act_top.pack(fill="x", padx=18, pady=(14, 8))
        ctk.CTkLabel(act_top, text="🕒  Recent Activity", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(act_top, text="Live Events", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="right")

        self.activity_container = ctk.CTkFrame(self.activity_card, fg_color="transparent")
        self.activity_container.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # Right Card: System Resources Overview
        self.sys_res_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.sys_res_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        res_top = ctk.CTkFrame(self.sys_res_card, fg_color="transparent")
        res_top.pack(fill="x", padx=18, pady=(14, 10))
        ctk.CTkLabel(res_top, text="🖥️  System Resources", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")

        self._add_resource_row("GPU Usage:", "lbl_sys_gpu", "bar_sys_gpu", ACCENT_BLUE, "0%")
        self._add_resource_row("VRAM Usage:", "lbl_sys_vram", "bar_sys_vram", ACCENT_GREEN, "0.0 / 0.0 GB")
        self._add_resource_row("GPU Temperature:", "lbl_sys_temp", "bar_sys_temp", ACCENT_ORANGE, "-- °C")
        self._add_resource_row("CPU Usage:", "lbl_sys_cpu", "bar_sys_cpu", ACCENT_PURPLE, "0%")
        self._add_resource_row("System Memory:", "lbl_sys_ram", "bar_sys_ram", ACCENT_CYAN, "0.0 / 0.0 GB")

        # Technical Console Card at the very bottom
        self.console_card = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=14, border_width=1, border_color="#334155")
        self.console_card.pack(fill="x", padx=4, pady=(0, 14))

        con_top = ctk.CTkFrame(self.console_card, fg_color="transparent")
        con_top.pack(fill="x", padx=16, pady=(10, 6))

        ctk.CTkLabel(
            con_top,
            text=">_ Technical Console (FFmpeg / NVENC Logs)",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(side="left")

        btn_clear = ctk.CTkButton(
            con_top,
            text="Clear Logs",
            font=ctk.CTkFont(size=11),
            fg_color="#1E293B",
            hover_color="#334155",
            text_color="#94A3B8",
            height=24,
            width=80,
            command=self._clear_console
        )
        btn_clear.pack(side="right")

        self.txt_console = ctk.CTkTextbox(
            self.console_card,
            fg_color="#020617",
            text_color="#4ADE80",
            font=ctk.CTkFont(family="Consolas", size=11),
            height=130,
            corner_radius=8
        )
        self.txt_console.pack(fill="x", padx=14, pady=(0, 14))
        self.txt_console.insert("end", "[Worker Server Daemon Initialized]\nWaiting for rendering tasks from connected clients...\n")

    def _add_resource_row(self, label: str, lbl_attr: str, bar_attr: str, color: str, initial_val: str):
        box = ctk.CTkFrame(self.sys_res_card, fg_color="transparent")
        box.pack(fill="x", padx=18, pady=3)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")
        
        lbl = ctk.CTkLabel(top, text=initial_val, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        lbl.pack(side="right")
        setattr(self, lbl_attr, lbl)

        bar = ctk.CTkProgressBar(box, height=7, corner_radius=3, fg_color="#E2E8F0", progress_color=color)
        bar.set(0.0)
        bar.pack(fill="x", pady=(2, 3))
        setattr(self, bar_attr, bar)

    def _clear_console(self):
        self.txt_console.delete("1.0", "end")
        server_log_bus.clear()

    def _refresh_telemetry(self):
        def _fetch_worker():
            try:
                telem = SystemService.get_hardware_telemetry()
                detailed_gpu = SystemService.get_detailed_gpu_info()
            except Exception:
                telem = {}
                detailed_gpu = {}
            try:
                self.after(0, lambda: self._apply_telemetry_ui(telem, detailed_gpu))
            except Exception:
                pass

        import threading
        threading.Thread(target=_fetch_worker, daemon=True).start()

    def _apply_telemetry_ui(self, telem: dict, detailed_gpu: dict):
        try:
            if not self.winfo_exists():
                return
            gpu_detected = telem.get("gpu_detected", False) or detailed_gpu.get("gpu_detected", False)
            gpu_name = telem.get("gpu_name") or detailed_gpu.get("name")
            gpu_util = telem.get("gpu_util_percent") if telem.get("gpu_util_percent") is not None else detailed_gpu.get("gpu_util_percent")
            vram_total = telem.get("gpu_vram_total_mb") or detailed_gpu.get("vram_total_mb")
            vram_used = telem.get("gpu_vram_used_mb") or detailed_gpu.get("vram_used_mb")

            if gpu_detected and gpu_name:
                self.lbl_gpu_name.configure(text=gpu_name[:26])
                if gpu_util is not None:
                    self.lbl_gpu_val.configure(text=f"{gpu_util:.0f}%")
                    self.bar_gpu.set(min(1.0, gpu_util / 100.0))
                    self.lbl_sys_gpu.configure(text=f"{gpu_util:.0f}%")
                    self.bar_sys_gpu.set(min(1.0, gpu_util / 100.0))
                
                if vram_total and vram_used:
                    tot_gb = vram_total / 1024
                    used_gb = vram_used / 1024
                    pct = (used_gb / tot_gb) * 100 if tot_gb > 0 else 0
                    self.lbl_vram_val.configure(text=f"{used_gb:.1f} / {tot_gb:.1f} GB")
                    self.lbl_vram_pct.configure(text=f"{pct:.0f}% used")
                    self.bar_vram.set(min(1.0, pct / 100.0))
                    self.lbl_sys_vram.configure(text=f"{used_gb:.1f} / {tot_gb:.1f} GB ({pct:.0f}%)")
                    self.bar_sys_vram.set(min(1.0, pct / 100.0))
            else:
                self.lbl_gpu_name.configure(text="CPU Mode (No NVIDIA GPU)")
                self.lbl_gpu_val.configure(text="N/A")
                self.lbl_sys_gpu.configure(text="N/A (CPU Mode)")
                self.lbl_vram_val.configure(text="Shared RAM")
                self.lbl_vram_pct.configure(text="System Memory")
                self.lbl_sys_vram.configure(text="Shared System RAM")

            # Temperature updates
            temp = detailed_gpu.get("temperature_c")
            if temp:
                self.lbl_temp_val.configure(text=f"{temp} °C")
                self.lbl_sys_temp.configure(text=f"{temp} °C")
                self.bar_temp.set(min(1.0, temp / 100.0))
                self.bar_sys_temp.set(min(1.0, temp / 100.0))
            else:
                self.lbl_temp_val.configure(text="Normal")
                self.lbl_sys_temp.configure(text="Normal Range")
                self.bar_temp.set(0.35)
                self.bar_sys_temp.set(0.35)

            cpu_pct = telem.get("cpu_percent", 0.0)
            self.lbl_cpu_val.configure(text=f"{cpu_pct:.0f}%")
            self.lbl_sys_cpu.configure(text=f"{cpu_pct:.1f}%")
            self.bar_sys_cpu.set(min(1.0, max(0.02, cpu_pct / 100.0)))

            ram_pct = telem.get("ram_percent", 0.0)
            ram_used_gb = telem.get("ram_used_gb", 0.0)
            ram_tot_gb = telem.get("ram_total_gb", 0.0)
            self.lbl_sys_ram.configure(text=f"{ram_used_gb:.1f} / {ram_tot_gb:.1f} GB ({ram_pct:.0f}%)")
            self.bar_sys_ram.set(min(1.0, max(0.02, ram_pct / 100.0)))

            # Live Render Job binding
            jobs = list(job_manager.jobs.values())
            self.lbl_q_summary.configure(text=f"{len(jobs)} jobs")

            active_j = None
            for j in reversed(jobs):
                if j.status.value in ["rendering", "queued"]:
                    active_j = j
                    break

            if active_j:
                self.lbl_active_badge.configure(
                    text=active_j.status.value.upper(),
                    fg_color=ACCENT_BLUE if active_j.status.value == "rendering" else ACCENT_ORANGE
                )
                self.lbl_active_file.configure(text=active_j.input_filename)
                self.lbl_active_meta.configure(text=f"Job ID: {active_j.job_id} • Preset: {active_j.preset} • {active_j.resolution}")
                self.bar_active.set(active_j.progress_percent / 100.0)
                self.lbl_pct_val.configure(text=f" {active_j.progress_percent:.0f}%")
                self.stage_box.configure(fg_color="#DBEAFE")
                self.lbl_stage_txt.configure(text=f"● Encoding: {active_j.progress_percent:.1f}% • Speed: {active_j.speed or '--'}", text_color=ACCENT_BLUE)
                sec = int(active_j.elapsed_seconds)
                self.lbl_meta_elapsed.configure(text=f"{sec // 60:02d}:{sec % 60:02d}")
                if active_j.eta_seconds:
                    eta_sec = int(active_j.eta_seconds)
                    self.lbl_meta_total.configure(text=f"{eta_sec // 60:02d}:{eta_sec % 60:02d}")
                else:
                    self.lbl_meta_total.configure(text="Calculating...")
                self.lbl_meta_output.configure(text=active_j.output_filename[:18])
            elif jobs:
                last_j = jobs[-1]
                clr = ACCENT_GREEN if last_j.status.value == "completed" else ACCENT_RED
                self.lbl_active_badge.configure(text=last_j.status.value.upper(), fg_color=clr)
                self.lbl_active_file.configure(text=last_j.input_filename)
                self.lbl_active_meta.configure(text=f"Job ID: {last_j.job_id} • Finished")
                self.bar_active.set(1.0 if last_j.status.value == "completed" else 0.0)
                self.lbl_pct_val.configure(text=" 100%" if last_j.status.value == "completed" else " 0%")
                self.stage_box.configure(fg_color="#D1FAE5" if last_j.status.value == "completed" else "#FEE2E2")
                self.lbl_stage_txt.configure(text=f"● Job finished with status: {last_j.status.value.capitalize()}", text_color=clr)
                sec = int(last_j.elapsed_seconds)
                self.lbl_meta_elapsed.configure(text=f"{sec // 60:02d}:{sec % 60:02d}")
                self.lbl_meta_total.configure(text=f"{sec // 60:02d}:{sec % 60:02d}")
                self.lbl_meta_output.configure(text=last_j.output_filename[:18])

            # Populate Render Queue preview cards
            for child in self.queue_list_container.winfo_children():
                child.destroy()
            if not jobs:
                ctk.CTkLabel(self.queue_list_container, text="No jobs in queue. Ready for client tasks.", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(pady=16)
            else:
                for qj in reversed(jobs[-4:]):
                    q_row = ctk.CTkFrame(self.queue_list_container, fg_color=BG_CARD_ALT, corner_radius=8)
                    q_row.pack(fill="x", pady=2)
                    q_row.grid_columnconfigure(0, weight=4)
                    q_row.grid_columnconfigure(1, weight=2)
                    q_row.grid_columnconfigure(2, weight=1)
                    ctk.CTkLabel(q_row, text=qj.input_filename[:18], font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY).grid(row=0, column=0, padx=8, pady=4, sticky="w")
                    clr = ACCENT_GREEN if qj.status.value == "completed" else (ACCENT_BLUE if qj.status.value == "rendering" else ACCENT_RED)
                    bg = "#D1FAE5" if qj.status.value == "completed" else ("#DBEAFE" if qj.status.value == "rendering" else "#FEE2E2")
                    ctk.CTkLabel(q_row, text=f" {qj.status.value.capitalize()} ", font=ctk.CTkFont(size=10, weight="bold"), text_color=clr, fg_color=bg, corner_radius=6).grid(row=0, column=1, padx=4, pady=4)
                    ctk.CTkLabel(q_row, text=f"{qj.progress_percent:.0f}%", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=2, padx=8, pady=4, sticky="e")

            # Update live activity events smoothly
            logs = list(server_log_bus.logs)
            if len(logs) != self._last_act_count:
                self._last_act_count = len(logs)
                for child in self.activity_container.winfo_children():
                    child.destroy()
                
                recent = logs[-4:]
                if not recent:
                    empty = ctk.CTkLabel(self.activity_container, text="Awaiting activity events...", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
                    empty.pack(pady=20)
                else:
                    for l in reversed(recent):
                        item = ctk.CTkFrame(self.activity_container, fg_color=BG_CARD_ALT, corner_radius=8)
                        item.pack(fill="x", pady=2)
                        item.grid_columnconfigure(0, weight=2)
                        item.grid_columnconfigure(1, weight=2)
                        item.grid_columnconfigure(2, weight=8)

                        lvl = l["level"]
                        msg = l["message"]
                        is_succ = lvl == "SUCCESS" or "success" in msg.lower() or "completed" in msg.lower()
                        clr = ACCENT_GREEN if is_succ else (ACCENT_BLUE if lvl == "INFO" else ACCENT_RED)
                        bg = "#D1FAE5" if is_succ else ("#DBEAFE" if lvl == "INFO" else "#FEE2E2")
                        lvl_txt = "SUCCESS" if is_succ else lvl

                        ctk.CTkLabel(item, text=l["time"], font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).grid(row=0, column=0, padx=6, pady=6, sticky="w")
                        ctk.CTkLabel(item, text=f" {lvl_txt} ", font=ctk.CTkFont(size=10, weight="bold"), text_color=clr, fg_color=bg, corner_radius=6).grid(row=0, column=1, padx=4, pady=6, sticky="w")
                        ctk.CTkLabel(item, text=msg[:45], font=ctk.CTkFont(size=10), text_color=TEXT_PRIMARY).grid(row=0, column=2, padx=4, pady=6, sticky="w")

        except Exception:
            pass

        has_active = any(j.status.value in ["rendering", "queued"] for j in job_manager.jobs.values())
        next_tick = 500 if has_active else 1500
        self.after(next_tick, self._refresh_telemetry)
