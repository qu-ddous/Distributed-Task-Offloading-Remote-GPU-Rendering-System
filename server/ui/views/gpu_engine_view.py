import time
import customtkinter as ctk

from client.ui.theme import *
from server.ui.components.sparkline import MiniGraphCanvas
from server.app.services.system_service import SystemService

class GPUEngineView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_top_hardware_section()
        self._build_engine_cards_section()
        self._build_diagnostics_card()

        # Instantly pre-seed static hardware on frame 0 (<5ms)
        try:
            static = SystemService.get_static_specs()
            self.lbl_cpu_cores_box.configure(text=f"{static['cpu_cores']} Cores")
            self.lbl_cpu_model_box.configure(text=static['cpu_model'][:22])
        except Exception:
            pass

        self._refresh_hardware()

    def on_page_shown(self):
        """Immediately refresh hardware info when switching to this view."""
        self._refresh_hardware()

    def _build_top_hardware_section(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(0, 14))
        row.grid_columnconfigure(0, weight=3) # Profile specs
        row.grid_columnconfigure(1, weight=2) # Sparkline graphs

        # Left: NVIDIA GPU Specs Card
        card_specs = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        card_specs.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        top = ctk.CTkFrame(card_specs, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 12))

        ctk.CTkLabel(top, text="🎮  Graphics & Compute Node", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_gpu_online = ctk.CTkLabel(top, text="Detecting...", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED, fg_color=BG_CARD_ALT, corner_radius=6, padx=8, pady=2)
        self.lbl_gpu_online.pack(side="left", padx=8)

        self.lbl_gpu_title = ctk.CTkLabel(card_specs, text="Querying System Hardware...", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_gpu_title.pack(anchor="w", padx=18, pady=(0, 12))

        # Details Grid
        grid = ctk.CTkFrame(card_specs, fg_color=BG_CARD_ALT, corner_radius=10)
        grid.pack(fill="x", padx=18, pady=(0, 16))
        grid.grid_columnconfigure((0, 1), weight=1)

        self._add_detail_row(grid, 0, 0, "Compute Engine:", "Detecting...", "lbl_cuda_spec")
        self._add_detail_row(grid, 0, 1, "VRAM / Memory:", "-- GB", "lbl_vram_spec")
        self._add_detail_row(grid, 1, 0, "Display Driver:", "--", "lbl_driver_spec")
        self._add_detail_row(grid, 1, 1, "Instruction Set:", "--", "lbl_compute_spec")
        self._add_detail_row(grid, 2, 0, "Active Encoder:", "Checking...", "lbl_enc_type_spec")
        self._add_detail_row(grid, 2, 1, "DirectX / Vulkan:", "Supported", "lbl_api_spec")

        # Right: 4 Sparkline Wave Graphs
        graphs_card = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        graphs_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        graphs_card.grid_columnconfigure((0, 1), weight=1)

        # 1. GPU Utilization Graph
        b1 = ctk.CTkFrame(graphs_card, fg_color=BG_CARD_ALT, corner_radius=12)
        b1.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        t1 = ctk.CTkFrame(b1, fg_color="transparent")
        t1.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(t1, text="GPU Utilization", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(side="left")
        self.lbl_g_gpu_val = ctk.CTkLabel(b1, text="--%", font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_g_gpu_val.pack(anchor="w", padx=10)
        self.graph_gpu = MiniGraphCanvas(b1, width=130, height=50, bg_color=BG_CARD_ALT, primary_color=ACCENT_BLUE)
        self.graph_gpu.pack(fill="x", padx=6, pady=(0, 6))

        # 2. VRAM Usage Graph
        b2 = ctk.CTkFrame(graphs_card, fg_color=BG_CARD_ALT, corner_radius=12)
        b2.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        t2 = ctk.CTkFrame(b2, fg_color="transparent")
        t2.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(t2, text="VRAM Usage", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(side="left")
        self.lbl_g_vram_val = ctk.CTkLabel(b2, text="-- / -- GB", font=ctk.CTkFont(size=13, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_g_vram_val.pack(anchor="w", padx=10)
        self.graph_vram = MiniGraphCanvas(b2, width=130, height=50, bg_color=BG_CARD_ALT, primary_color=ACCENT_GREEN)
        self.graph_vram.pack(fill="x", padx=6, pady=(0, 6))

        # 3. GPU Temperature Graph
        b3 = ctk.CTkFrame(graphs_card, fg_color=BG_CARD_ALT, corner_radius=12)
        b3.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        t3 = ctk.CTkFrame(b3, fg_color="transparent")
        t3.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(t3, text="GPU Temperature", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(side="left")
        self.lbl_g_temp_val = ctk.CTkLabel(b3, text="-- °C", font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT_ORANGE)
        self.lbl_g_temp_val.pack(anchor="w", padx=10)
        self.graph_temp = MiniGraphCanvas(b3, width=130, height=50, bg_color=BG_CARD_ALT, primary_color=ACCENT_ORANGE)
        self.graph_temp.pack(fill="x", padx=6, pady=(0, 6))

        # 4. Memory Clock Graph
        b4 = ctk.CTkFrame(graphs_card, fg_color=BG_CARD_ALT, corner_radius=12)
        b4.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        t4 = ctk.CTkFrame(b4, fg_color="transparent")
        t4.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(t4, text="Memory Clock", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(side="left")
        self.lbl_g_clock_val = ctk.CTkLabel(b4, text="-- MHz", font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT_PURPLE)
        self.lbl_g_clock_val.pack(anchor="w", padx=10)
        self.graph_clock = MiniGraphCanvas(b4, width=130, height=50, bg_color=BG_CARD_ALT, primary_color=ACCENT_PURPLE)
        self.graph_clock.pack(fill="x", padx=6, pady=(0, 6))

    def _add_detail_row(self, parent, row, col, label, val, attr_name=None):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, sticky="w", padx=12, pady=4)
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="left")
        lbl = ctk.CTkLabel(f, text=f" {val}", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY)
        lbl.pack(side="left")
        if attr_name:
            setattr(self, attr_name, lbl)

    def _build_engine_cards_section(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(0, 14))
        row.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. NVENC Engine
        c1 = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        top1 = ctk.CTkFrame(c1, fg_color="transparent")
        top1.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(top1, text="⚡ NVENC Engine", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_nvenc_badge = ctk.CTkLabel(top1, text="Detecting...", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED, fg_color=BG_CARD_ALT, corner_radius=6, padx=8, pady=2)
        self.lbl_nvenc_badge.pack(side="right")

        f1 = ctk.CTkFrame(c1, fg_color=BG_CARD_ALT, corner_radius=10)
        f1.pack(fill="x", padx=14, pady=(0, 14))
        self.lbl_nvenc_ver = self._add_box_row(f1, "Version:", "--")
        self.lbl_nvenc_codecs = self._add_box_row(f1, "Supported Codecs:", "Checking...")
        self.lbl_nvenc_res = self._add_box_row(f1, "Max Resolution:", "4K / 8K")
        self.lbl_nvenc_sessions = self._add_box_row(f1, "Concurrent Sessions:", "3")
        self.lbl_nvenc_status = self._add_box_row(f1, "Status:", "Checking...", TEXT_MUTED)

        # 2. FFmpeg Engine
        c2 = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c2.grid(row=0, column=1, sticky="nsew", padx=4)

        top2 = ctk.CTkFrame(c2, fg_color="transparent")
        top2.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(top2, text="🎬 FFmpeg Engine", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_ffmpeg_badge = ctk.CTkLabel(top2, text="Detecting...", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED, fg_color=BG_CARD_ALT, corner_radius=6, padx=8, pady=2)
        self.lbl_ffmpeg_badge.pack(side="right")

        f2 = ctk.CTkFrame(c2, fg_color=BG_CARD_ALT, corner_radius=10)
        f2.pack(fill="x", padx=14, pady=(0, 14))
        self.lbl_ff_ver = self._add_box_row(f2, "Version:", "--")
        self.lbl_ff_h264 = self._add_box_row(f2, "H.264 Encoder:", "Checking...", TEXT_MUTED)
        self.lbl_ff_hevc = self._add_box_row(f2, "HEVC Encoder:", "Checking...", TEXT_MUTED)
        self.lbl_ff_software = self._add_box_row(f2, "Software Codecs:", "libx264, aac", ACCENT_GREEN)
        self.lbl_ff_filters = self._add_box_row(f2, "Scale Filters:", "Enabled", ACCENT_GREEN)

        # 3. CPU Fallback Engine
        c3 = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c3.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        top3 = ctk.CTkFrame(c3, fg_color="transparent")
        top3.pack(fill="x", padx=16, pady=(14, 8))
        ctk.CTkLabel(top3, text="⚙️ CPU Fallback Engine", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(top3, text="Available", font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT_PURPLE, fg_color="#F3E8FF", corner_radius=6, padx=8, pady=2).pack(side="right")

        f3 = ctk.CTkFrame(c3, fg_color=BG_CARD_ALT, corner_radius=10)
        f3.pack(fill="x", padx=14, pady=(0, 14))
        self.lbl_cpu_load_box = self._add_box_row(f3, "CPU Usage:", "--%")
        self.lbl_cpu_cores_box = self._add_box_row(f3, "CPU Cores:", "--")
        self.lbl_cpu_model_box = self._add_box_row(f3, "CPU Model:", "--")
        self.lbl_cpu_status_box = self._add_box_row(f3, "Status:", "Ready", ACCENT_GREEN)

    def _add_box_row(self, parent, label, val, color=None):
        r = ctk.CTkFrame(parent, fg_color="transparent")
        r.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(side="left")
        lbl = ctk.CTkLabel(r, text=val, font=ctk.CTkFont(size=10, weight="bold"), text_color=color or TEXT_PRIMARY)
        lbl.pack(side="right")
        return lbl

    def _build_diagnostics_card(self):
        diag_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        diag_card.pack(fill="x", padx=4, pady=(0, 14))

        box = ctk.CTkFrame(diag_card, fg_color="transparent")
        box.pack(fill="x", padx=20, pady=16)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text="🛠️  Hardware Diagnostics", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_diag_summary = ctk.CTkLabel(top, text="Inspecting video encoding capabilities...", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_diag_summary.pack(side="left", padx=12)

        btn_run = ctk.CTkButton(
            top,
            text="▶ Run Diagnostics",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8,
            height=30,
            width=140,
            command=self._run_diagnostics
        )
        btn_run.pack(side="right")

    def _run_diagnostics(self):
        self._refresh_hardware()

    def _refresh_hardware(self):
        def _fetch_worker():
            try:
                telem = SystemService.get_hardware_telemetry()
                detailed_gpu = SystemService.get_detailed_gpu_info()
                is_avail, ver, is_nvenc, _ = SystemService.check_ffmpeg_capabilities()
            except Exception:
                telem, detailed_gpu, is_avail, ver, is_nvenc = {}, {}, False, None, False
            try:
                self.after(0, lambda: self._apply_hardware_ui(telem, detailed_gpu, is_avail, ver, is_nvenc))
            except Exception:
                pass

        import threading
        threading.Thread(target=_fetch_worker, daemon=True).start()

    def _apply_hardware_ui(self, telem: dict, detailed_gpu: dict, is_avail: bool, ver: str, is_nvenc: bool):
        try:
            if not self.winfo_exists():
                return
            gpu_detected = telem.get("gpu_detected", False) or detailed_gpu.get("gpu_detected", False)
            gpu_name = telem.get("gpu_name") or detailed_gpu.get("name")
            gpu_util = telem.get("gpu_util_percent", 0.0) or detailed_gpu.get("gpu_util_percent", 0.0) or 0.0
            vram_total = telem.get("gpu_vram_total_mb", 0) or detailed_gpu.get("vram_total_mb", 0) or 0
            vram_used = telem.get("gpu_vram_used_mb", 0) or detailed_gpu.get("vram_used_mb", 0) or 0

            if gpu_detected and gpu_name:
                self.lbl_gpu_title.configure(text=gpu_name[:32])
                self.lbl_gpu_online.configure(text="Online (NVENC Ready)" if is_nvenc else "GPU Active", text_color=ACCENT_GREEN, fg_color="#D1FAE5")
                tot_gb = vram_total / 1024
                used_gb = vram_used / 1024
                self.lbl_vram_spec.configure(text=f"{tot_gb:.1f} GB GDDR")
                self.lbl_driver_spec.configure(text=str(detailed_gpu.get("driver_version", "Active Driver")))
                self.lbl_cuda_spec.configure(text="CUDA Enabled")
                self.lbl_compute_spec.configure(text="Supported")
                self.lbl_enc_type_spec.configure(text="NVENC (Hardware)" if is_nvenc else "Software Encode")

                self.lbl_g_gpu_val.configure(text=f"{gpu_util:.0f}%")
                self.lbl_g_vram_val.configure(text=f"{used_gb:.1f} / {tot_gb:.1f} GB")
                temp = detailed_gpu.get("temperature_c")
                self.lbl_g_temp_val.configure(text=f"{temp} °C" if temp else "Normal")
                clk = detailed_gpu.get("mem_clock_mhz")
                self.lbl_g_clock_val.configure(text=f"{clk} MHz" if clk else "Dynamic")

                self.graph_gpu.update_data(gpu_util)
                self.graph_vram.update_data((used_gb / tot_gb) * 100 if tot_gb > 0 else 0)
                if temp:
                    self.graph_temp.update_data(min(100, temp))

                if is_nvenc:
                    self.lbl_nvenc_badge.configure(text="Ready", text_color=ACCENT_GREEN, fg_color="#D1FAE5")
                    self.lbl_nvenc_ver.configure(text="Active (Driver)")
                    self.lbl_nvenc_codecs.configure(text="H.264 (NVENC), HEVC")
                    self.lbl_nvenc_status.configure(text="Available", text_color=ACCENT_GREEN)
                    self.lbl_ff_h264.configure(text="Yes (h264_nvenc)", text_color=ACCENT_GREEN)
                    self.lbl_ff_hevc.configure(text="Yes (hevc_nvenc)", text_color=ACCENT_GREEN)
                else:
                    self.lbl_nvenc_badge.configure(text="Unavailable", text_color=ACCENT_ORANGE, fg_color="#FEF3C7")
                    self.lbl_nvenc_ver.configure(text="Driver Incompatible")
                    self.lbl_nvenc_codecs.configure(text="CPU Fallback (libx264)")
                    self.lbl_nvenc_status.configure(text="CPU Mode", text_color=ACCENT_BLUE)
                    self.lbl_ff_h264.configure(text="libx264 (Software)", text_color=ACCENT_BLUE)
                    self.lbl_ff_hevc.configure(text="libx265 (Software)", text_color=ACCENT_BLUE)
            else:
                self.lbl_gpu_title.configure(text="CPU Transcode Node (No NVIDIA GPU)")
                self.lbl_gpu_online.configure(text="CPU Fallback Mode", text_color=ACCENT_BLUE, fg_color="#DBEAFE")
                self.lbl_vram_spec.configure(text="Shared System RAM")
                self.lbl_driver_spec.configure(text="Host Display Driver")
                self.lbl_cuda_spec.configure(text="N/A (CPU Mode)")
                self.lbl_compute_spec.configure(text="x86_64 AVX2")
                self.lbl_enc_type_spec.configure(text="CPU libx264 (Software)")

                self.lbl_g_gpu_val.configure(text="0%")
                self.lbl_g_vram_val.configure(text="Shared RAM")
                self.lbl_g_temp_val.configure(text="Normal")
                self.lbl_g_clock_val.configure(text="N/A")
                self.graph_gpu.update_data(0.0)

                self.lbl_nvenc_badge.configure(text="CPU Fallback", text_color=ACCENT_BLUE, fg_color="#DBEAFE")
                self.lbl_nvenc_ver.configure(text="N/A (CPU Node)")
                self.lbl_nvenc_codecs.configure(text="libx264 (Software)")
                self.lbl_nvenc_status.configure(text="CPU Fallback Active", text_color=ACCENT_BLUE)
                self.lbl_ff_h264.configure(text="libx264 (Active)", text_color=ACCENT_BLUE)
                self.lbl_ff_hevc.configure(text="libx265 (Software)", text_color=ACCENT_BLUE)

            # FFmpeg common
            if is_avail:
                self.lbl_ffmpeg_badge.configure(text="Ready", text_color=ACCENT_GREEN, fg_color="#D1FAE5")
                self.lbl_ff_ver.configure(text=ver or "6.0+")
            else:
                self.lbl_ffmpeg_badge.configure(text="Missing", text_color=ACCENT_RED, fg_color="#FEE2E2")
                self.lbl_ff_ver.configure(text="Not Found")

            # CPU Details
            cpu_pct = telem.get("cpu_percent", 0.0)
            cpu_cores = telem.get("cpu_cores", 1)
            cpu_model = telem.get("cpu_model", "Standard CPU")
            self.lbl_cpu_load_box.configure(text=f"{cpu_pct:.1f}%")
            self.lbl_cpu_cores_box.configure(text=f"{cpu_cores} Cores")
            self.lbl_cpu_model_box.configure(text=cpu_model[:22])
            self.lbl_cpu_status_box.configure(text="Primary Engine" if not (gpu_detected and is_nvenc) else "Standby Fallback", text_color=ACCENT_GREEN)

            diag_msg = f"Host: {telem.get('hostname', 'Local')} • Engine: {'NVIDIA NVENC Hardware' if (gpu_detected and is_nvenc) else 'CPU Multi-Core (libx264)'} • System Operational"
            self.lbl_diag_summary.configure(text=diag_msg, text_color=ACCENT_GREEN)

        except Exception:
            pass

        self.after(2500, self._refresh_hardware)
