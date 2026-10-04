"""
Modern CustomTkinter Desktop Client UI
Distributed Task Offloading & Remote GPU Rendering System
Follows Google Material / Modern Clean Studio aesthetic.
"""

import os
import sys
import time
import threading
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from tkinter import filedialog, messagebox

import customtkinter as ctk

# Set default theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

from client.services.config_manager import config_manager
from client.services.network_client import NetworkClient

# Design Palette Constants
BG_MAIN = "#0F1117"
BG_CARD = "#1A1D27"
BG_INPUT = "#222634"
BORDER_COLOR = "#2D3345"
ACCENT_BLUE = "#3B82F6"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"
ACCENT_YELLOW = "#F59E0B"
TEXT_PRIMARY = "#F9FAFB"
TEXT_MUTED = "#9CA3AF"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GPU Render Stream • Distributed Offloading Studio")
        self.geometry("1100x780")
        self.minsize(980, 680)

        # Load local configuration
        self.config_data = config_manager.load()

        # State Variables
        self.selected_file_path: Optional[Path] = None
        self.computed_checksum: Optional[str] = None
        self.is_connected = False
        self.gpu_ready = False
        self.active_job_id: Optional[str] = None
        self.ws_stop_event = asyncio.Event()

        # Build Layout
        self._init_ui()

    def _init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Top Header Banner
        self._build_header()

        # 2. Main Content Tabs / Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Left Column: Configuration & Job Setup
        self._build_left_panel()

        # Right Column: Live Monitor, Logs & Results
        self._build_right_panel()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        header_frame.grid_columnconfigure(1, weight=1)

        # Title & Subtitle
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        title_label = ctk.CTkLabel(
            title_box,
            text="⚡ GPU Render Stream",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_box,
            text="Low-Power Client ➔ High-Performance NVENC Offloader",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        )
        subtitle_label.pack(anchor="w")

        # Connection Bar on right
        conn_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        conn_box.grid(row=0, column=1, padx=20, pady=12, sticky="e")

        ctk.CTkLabel(conn_box, text="Worker IP:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=(0, 5))
        self.ip_entry = ctk.CTkEntry(conn_box, width=120, placeholder_text="192.168.1.100")
        self.ip_entry.insert(0, str(self.config_data.get("server_host", "127.0.0.1")))
        self.ip_entry.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkLabel(conn_box, text="Port:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=(0, 5))
        self.port_entry = ctk.CTkEntry(conn_box, width=70, placeholder_text="8000")
        self.port_entry.insert(0, str(self.config_data.get("server_port", 8000)))
        self.port_entry.grid(row=0, column=3, padx=(0, 10))

        ctk.CTkLabel(conn_box, text="Token:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=4, padx=(0, 5))
        self.token_entry = ctk.CTkEntry(conn_box, width=100, show="•", placeholder_text="Token")
        self.token_entry.insert(0, str(self.config_data.get("api_token", "")))
        self.token_entry.grid(row=0, column=5, padx=(0, 12))

        self.btn_test_conn = ctk.CTkButton(
            conn_box,
            text="Test Connection",
            command=self._on_test_connection_clicked,
            fg_color=ACCENT_BLUE,
            hover_color="#2563EB",
            width=120,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_test_conn.grid(row=0, column=6)

        # Status indicators underneath header
        self.status_bar_frame = ctk.CTkFrame(header_frame, fg_color=BG_MAIN, corner_radius=8)
        self.status_bar_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 12))
        self.status_bar_frame.grid_columnconfigure(3, weight=1)

        self.lbl_worker_status = ctk.CTkLabel(
            self.status_bar_frame,
            text="● Worker: Not Connected",
            text_color=ACCENT_RED,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_worker_status.grid(row=0, column=0, padx=15, pady=6)

        self.lbl_gpu_status = ctk.CTkLabel(
            self.status_bar_frame,
            text="● NVENC: Unknown",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_gpu_status.grid(row=0, column=1, padx=15, pady=6)

        self.lbl_latency = ctk.CTkLabel(
            self.status_bar_frame,
            text="Latency: -- ms",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12)
        )
        self.lbl_latency.grid(row=0, column=2, padx=15, pady=6)

    def _build_left_panel(self):
        panel = ctk.CTkScrollableFrame(self.main_container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Section 1: File Selection
        sec1_title = ctk.CTkLabel(panel, text="1. Select Input Video", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY)
        sec1_title.pack(anchor="w", padx=15, pady=(15, 8))

        file_btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        file_btn_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.btn_select_file = ctk.CTkButton(
            file_btn_frame,
            text="Browse Video File...",
            command=self._on_browse_video_clicked,
            fg_color="#374151",
            hover_color="#4B5563",
            height=34
        )
        self.btn_select_file.pack(side="left", padx=(0, 10))

        self.lbl_selected_filename = ctk.CTkLabel(file_btn_frame, text="No video selected", text_color=TEXT_MUTED, anchor="w")
        self.lbl_selected_filename.pack(side="left", fill="x", expand=True)

        # File details container
        self.file_details_box = ctk.CTkFrame(panel, fg_color=BG_MAIN, corner_radius=8)
        self.file_details_box.pack(fill="x", padx=15, pady=(0, 15))

        self.lbl_file_size = ctk.CTkLabel(self.file_details_box, text="File Size: --", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_file_size.pack(anchor="w", padx=12, pady=(8, 2))

        self.lbl_file_checksum = ctk.CTkLabel(self.file_details_box, text="SHA-256: --", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_file_checksum.pack(anchor="w", padx=12, pady=(0, 8))

        # Section 2: Render Settings
        sec2_title = ctk.CTkLabel(panel, text="2. Render Configuration", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY)
        sec2_title.pack(anchor="w", padx=15, pady=(10, 8))

        settings_grid = ctk.CTkFrame(panel, fg_color="transparent")
        settings_grid.pack(fill="x", padx=15, pady=(0, 10))
        settings_grid.grid_columnconfigure(0, weight=1)
        settings_grid.grid_columnconfigure(1, weight=1)

        # Resolution
        ctk.CTkLabel(settings_grid, text="Resolution Preset:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.opt_resolution = ctk.CTkOptionMenu(
            settings_grid,
            values=["Original", "720p", "1080p", "1440p", "4K"],
            command=self._on_setting_changed
        )
        self.opt_resolution.set(self.config_data.get("default_resolution", "1080p"))
        self.opt_resolution.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))

        # Bitrate
        ctk.CTkLabel(settings_grid, text="Video Bitrate:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.opt_bitrate = ctk.CTkOptionMenu(
            settings_grid,
            values=["2M", "5M", "8M", "12M", "20M"],
            command=self._on_setting_changed
        )
        self.opt_bitrate.set(self.config_data.get("default_bitrate", "5M"))
        self.opt_bitrate.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 10))

        # NVENC Preset
        ctk.CTkLabel(settings_grid, text="NVENC Encoder Preset:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.opt_preset = ctk.CTkOptionMenu(
            settings_grid,
            values=["p1 (Fastest)", "p2", "p3", "p4 (Medium)", "p5", "p6", "p7 (Slowest)"],
            command=self._on_setting_changed
        )
        self.opt_preset.set("p4 (Medium)")
        self.opt_preset.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=(0, 10))

        # CPU Fallback checkbox
        self.chk_cpu_fallback = ctk.CTkCheckBox(
            settings_grid,
            text="Allow CPU Fallback",
            font=ctk.CTkFont(size=12),
            checkbox_height=20,
            checkbox_width=20
        )
        if self.config_data.get("allow_cpu_fallback", False):
            self.chk_cpu_fallback.select()
        self.chk_cpu_fallback.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(0, 10))

        # Section 3: Output Destination
        sec3_title = ctk.CTkLabel(panel, text="3. Output File & Destination", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY)
        sec3_title.pack(anchor="w", padx=15, pady=(10, 8))

        ctk.CTkLabel(panel, text="Output Filename:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(0, 4))
        self.entry_out_filename = ctk.CTkEntry(panel, placeholder_text="rendered_output.mp4")
        self.entry_out_filename.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(panel, text="Download Directory:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(0, 4))
        dir_frame = ctk.CTkFrame(panel, fg_color="transparent")
        dir_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.entry_out_dir = ctk.CTkEntry(dir_frame)
        self.entry_out_dir.insert(0, str(self.config_data.get("output_dir", str(Path.home() / "Downloads"))))
        self.entry_out_dir.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.btn_browse_dir = ctk.CTkButton(
            dir_frame,
            text="Browse...",
            width=80,
            command=self._on_browse_output_dir_clicked,
            fg_color="#374151"
        )
        self.btn_browse_dir.pack(side="right")

        # Start Render Action Button
        self.btn_start_render = ctk.CTkButton(
            panel,
            text="🚀 Submit & Render Remotely",
            command=self._on_start_render_clicked,
            fg_color=ACCENT_GREEN,
            hover_color="#059669",
            height=46,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.btn_start_render.pack(fill="x", padx=15, pady=(15, 20))

    def _build_right_panel(self):
        panel = ctk.CTkFrame(self.main_container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        panel.grid_rowconfigure(3, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # Monitor Header
        mon_header = ctk.CTkFrame(panel, fg_color="transparent")
        mon_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        mon_header.grid_columnconfigure(0, weight=1)

        mon_title = ctk.CTkLabel(mon_header, text="Active Job Monitor", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY)
        mon_title.grid(row=0, column=0, sticky="w")

        self.btn_cancel_job = ctk.CTkButton(
            mon_header,
            text="Cancel Job",
            command=self._on_cancel_job_clicked,
            fg_color=ACCENT_RED,
            hover_color="#DC2626",
            width=90,
            height=28,
            state="disabled"
        )
        self.btn_cancel_job.grid(row=0, column=1, sticky="e")

        # Status & Progress Box
        prog_box = ctk.CTkFrame(panel, fg_color=BG_MAIN, corner_radius=10)
        prog_box.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(prog_box, height=14, corner_radius=7, fg_color="#2D3345", progress_color=ACCENT_BLUE)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=15, pady=(12, 6))

        # Stats row
        stats_frame = ctk.CTkFrame(prog_box, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=(0, 10))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)

        self.lbl_stage = ctk.CTkLabel(stats_frame, text="Stage: Idle", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_stage.grid(row=0, column=0, sticky="w")

        self.lbl_percent = ctk.CTkLabel(stats_frame, text="0.0%", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_percent.grid(row=0, column=1)

        self.lbl_elapsed = ctk.CTkLabel(stats_frame, text="Elapsed: 00:00", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_elapsed.grid(row=0, column=2)

        self.lbl_eta = ctk.CTkLabel(stats_frame, text="ETA: --", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_eta.grid(row=0, column=3, sticky="e")

        # Results Summary Banner (shown on completion)
        self.result_banner = ctk.CTkFrame(panel, fg_color=BG_MAIN, corner_radius=10)
        self.result_banner.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))

        self.lbl_result_status = ctk.CTkLabel(self.result_banner, text="Ready for submission.", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_result_status.pack(anchor="w", padx=12, pady=(8, 2))

        self.lbl_result_details = ctk.CTkLabel(self.result_banner, text="", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED, justify="left")
        self.lbl_result_details.pack(anchor="w", padx=12, pady=(0, 6))

        self.btn_open_folder = ctk.CTkButton(
            self.result_banner,
            text="📂 Open Output Folder",
            command=self._on_open_folder_clicked,
            fg_color="#374151",
            height=26,
            width=140
        )
        # Hidden until success

        # Live Console Log Box
        console_box = ctk.CTkFrame(panel, fg_color="transparent")
        console_box.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 15))
        console_box.grid_rowconfigure(1, weight=1)
        console_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(console_box, text="Live FFmpeg Worker Logs:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.txt_console = ctk.CTkTextbox(
            console_box,
            fg_color=BG_MAIN,
            text_color="#10B981",
            font=ctk.CTkFont(family="Courier", size=11),
            corner_radius=8,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.txt_console.grid(row=1, column=0, sticky="nsew")

    # ---------------- UI Action Handlers ----------------

    def _append_log(self, text: str):
        self.txt_console.insert("end", text + "\n")
        self.txt_console.see("end")

    def _on_test_connection_clicked(self):
        host = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        token = self.token_entry.get().strip()

        if not host or not port:
            messagebox.showwarning("Validation", "Please provide worker server IP and Port.")
            return

        self.lbl_worker_status.configure(text="● Connecting...", text_color=ACCENT_YELLOW)
        self.btn_test_conn.configure(state="disabled")

        def task():
            net = NetworkClient(host, port, token)
            res = net.ping_and_health()
            self.after(0, lambda: self._process_connection_result(res, host, port, token))

        threading.Thread(target=task, daemon=True).start()

    def _process_connection_result(self, res: Dict[str, Any], host: str, port: str, token: str):
        self.btn_test_conn.configure(state="normal")
        if res.get("success"):
            self.is_connected = True
            data = res.get("data", {})
            ff_info = data.get("ffmpeg", {})
            hw_info = data.get("hardware", {})
            latency = res.get("latency_ms", 0)

            self.lbl_worker_status.configure(text=f"● Worker: Online ({data.get('protocol_version')})", text_color=ACCENT_GREEN)
            self.lbl_latency.configure(text=f"Latency: {latency} ms")

            nvenc = ff_info.get("nvenc_available", False)
            self.gpu_ready = nvenc
            if nvenc:
                gpu_name = hw_info.get("gpu_name") or "NVIDIA NVENC Detected"
                self.lbl_gpu_status.configure(text=f"● NVENC Ready ({gpu_name[:20]})", text_color=ACCENT_GREEN)
            else:
                self.lbl_gpu_status.configure(text="● NVENC: Not Detected", text_color=ACCENT_RED)

            self._append_log(f"[Network] Connected to worker {host}:{port} in {latency}ms.")
            self._append_log(f"[Server] Hardware: GPU={hw_info.get('gpu_name')}, CPU Cores={hw_info.get('cpu_cores')}")

            # Save updated settings
            self.config_data["server_host"] = host
            self.config_data["server_port"] = int(port)
            self.config_data["api_token"] = token
            config_manager.save(self.config_data)
        else:
            self.is_connected = False
            err = res.get("error", "Unknown error")
            self.lbl_worker_status.configure(text="● Worker: Offline", text_color=ACCENT_RED)
            self.lbl_gpu_status.configure(text="● NVENC: Unknown", text_color=TEXT_MUTED)
            self.lbl_latency.configure(text="Latency: -- ms")
            self._append_log(f"[Connection Error] {err}")
            messagebox.showerror("Connection Failed", f"Failed to connect to worker server:\n\n{err}")

    def _on_browse_video_clicked(self):
        filetypes = [
            ("Video Files", "*.mp4 *.mkv *.mov *.avi *.wmv *.flv *.ts"),
            ("All Files", "*.*")
        ]
        chosen = filedialog.askopenfilename(title="Select Video File to Offload", filetypes=filetypes)
        if not chosen:
            return

        path = Path(chosen)
        self.selected_file_path = path
        self.lbl_selected_filename.configure(text=path.name, text_color=TEXT_PRIMARY)

        # Set default output filename
        stem = path.stem
        ext = path.suffix or ".mp4"
        res_str = self.opt_resolution.get()
        default_out = f"{stem}_remote_{res_str}{ext}"
        self.entry_out_filename.delete(0, "end")
        self.entry_out_filename.insert(0, default_out)

        # File size display
        size_bytes = path.stat().st_size
        size_mb = round(size_bytes / (1024 * 1024), 2)
        self.lbl_file_size.configure(text=f"File Size: {size_mb} MB ({size_bytes:,} bytes)")
        self.lbl_file_checksum.configure(text="SHA-256: Calculating checksum...", text_color=ACCENT_YELLOW)

        # Background checksum calculation
        def calc_hash():
            net = NetworkClient()
            sha256 = net.compute_sha256(path)
            self.computed_checksum = sha256
            self.after(0, lambda: self.lbl_file_checksum.configure(
                text=f"SHA-256: {sha256[:16]}...{sha256[-8:]} (Verified)",
                text_color=ACCENT_GREEN
            ))
            self.after(0, lambda: self._append_log(f"[File] Calculated SHA-256: {sha256}"))

        threading.Thread(target=calc_hash, daemon=True).start()

    def _on_browse_output_dir_clicked(self):
        chosen = filedialog.askdirectory(title="Select Output Download Folder")
        if chosen:
            self.entry_out_dir.delete(0, "end")
            self.entry_out_dir.insert(0, chosen)
            self.config_data["output_dir"] = chosen
            config_manager.save(self.config_data)

    def _on_setting_changed(self, _=None):
        if self.selected_file_path:
            stem = self.selected_file_path.stem
            ext = self.selected_file_path.suffix or ".mp4"
            res_str = self.opt_resolution.get()
            self.entry_out_filename.delete(0, "end")
            self.entry_out_filename.insert(0, f"{stem}_remote_{res_str}{ext}")

    def _on_start_render_clicked(self):
        if not self.is_connected:
            messagebox.showwarning("Connection Required", "Please test and confirm connection to the worker server first.")
            return

        if not self.selected_file_path or not self.selected_file_path.exists():
            messagebox.showwarning("File Missing", "Please select a valid input video file.")
            return

        if not self.computed_checksum:
            messagebox.showinfo("Please Wait", "Still calculating SHA-256 checksum for the input video. Try again in a moment.")
            return

        out_name = self.entry_out_filename.get().strip()
        out_dir = Path(self.entry_out_dir.get().strip())
        if not out_name:
            messagebox.showwarning("Filename", "Please specify an output filename.")
            return

        out_dest_file = out_dir / out_name
        if out_dest_file.exists():
            overwrite = messagebox.askyesno(
                "Confirm Overwrite",
                f"The destination file already exists:\n{out_dest_file}\n\nDo you want to overwrite it when completed?"
            )
            if not overwrite:
                return

        # Disable submission UI during active process
        self.btn_start_render.configure(state="disabled")
        self.btn_cancel_job.configure(state="normal")
        self.btn_open_folder.pack_forget()

        # Extract selected values
        preset_raw = self.opt_preset.get().split(" ")[0] # e.g. 'p4'
        res_val = self.opt_resolution.get()
        bitrate_val = self.opt_bitrate.get()
        allow_cpu = bool(self.chk_cpu_fallback.get())

        host = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        token = self.token_entry.get().strip()

        # Launch worker thread
        threading.Thread(
            target=self._run_job_orchestrator,
            args=(host, port, token, res_val, bitrate_val, preset_raw, out_name, out_dir, allow_cpu),
            daemon=True
        ).start()

    def _run_job_orchestrator(
        self, host: str, port: str, token: str,
        resolution: str, bitrate: str, preset: str,
        out_name: str, out_dir: Path, allow_cpu: bool
    ):
        net = NetworkClient(host, port, token)
        start_job_time = time.time()

        # Step 1: Uploading
        self.after(0, lambda: self._update_job_stage("Uploading input video...", 0.0))
        self.after(0, lambda: self._append_log(f"[Upload] Initiating upload to http://{host}:{port}..."))

        def upload_progress(sent, total):
            pct = (sent / total) * 100.0 if total > 0 else 0
            self.after(0, lambda: self._update_upload_progress(pct, sent, total))

        t_up_start = time.time()
        res_upload = net.submit_job(
            input_file=self.selected_file_path,
            checksum=self.computed_checksum,
            resolution=resolution,
            bitrate=bitrate,
            preset=preset,
            output_filename=out_name,
            allow_cpu_fallback=allow_cpu,
            progress_callback=upload_progress
        )
        t_up_duration = round(time.time() - t_up_start, 2)

        if not res_upload.get("success"):
            err = res_upload.get("error", "Unknown error during upload.")
            self.after(0, lambda: self._handle_job_failure(f"Upload Failed: {err}"))
            return

        job_info = res_upload["job"]
        job_id = job_info["job_id"]
        self.active_job_id = job_id
        self.after(0, lambda: self._append_log(f"[Upload] Finished in {t_up_duration}s. Server Job ID: {job_id}"))

        # Step 2: Live WebSocket Monitoring of Rendering
        self.after(0, lambda: self._update_job_stage("Remote GPU Rendering...", 0.0))
        self.ws_stop_event.clear()

        render_complete_event = threading.Event()
        render_result: Dict[str, Any] = {"status": "unknown"}

        def on_ws_message(msg: Dict[str, Any]):
            mtype = msg.get("type")
            if mtype == "progress":
                pct = msg.get("percent", 0.0)
                elapsed = msg.get("elapsed_seconds", 0.0)
                eta = msg.get("eta_seconds")
                speed = msg.get("speed")
                fps = msg.get("fps")
                self.after(0, lambda: self._update_render_progress(pct, elapsed, eta, speed, fps))
            elif mtype == "log":
                log_txt = msg.get("message", "")
                self.after(0, lambda: self._append_log(f"[Worker] {log_txt}"))
            elif mtype == "state":
                st = msg.get("status")
                if st == "completed":
                    render_result["status"] = "completed"
                    render_result["output_checksum"] = msg.get("output_checksum")
                    render_result["render_seconds"] = msg.get("total_render_seconds", 0)
                    render_complete_event.set()
                elif st in ["failed", "cancelled"]:
                    render_result["status"] = st
                    render_result["error"] = msg.get("message") or msg.get("error")
                    render_complete_event.set()
            elif mtype == "error":
                render_result["status"] = "failed"
                render_result["error"] = msg.get("error")
                render_complete_event.set()

        # Run async websocket loop in new loop
        def ws_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(net.listen_websocket(job_id, on_ws_message, self.ws_stop_event))
            loop.close()

        wst = threading.Thread(target=ws_thread, daemon=True)
        wst.start()

        # Wait for render completion or cancellation
        render_complete_event.wait()
        self.ws_stop_event.set()

        if render_result.get("status") != "completed":
            err = render_result.get("error", "Remote rendering failed or cancelled.")
            self.after(0, lambda: self._handle_job_failure(f"Render Error: {err}"))
            return

        # Step 3: Downloading Output Video
        expected_hash = render_result.get("output_checksum")
        t_render_duration = render_result.get("render_seconds", 0)
        self.after(0, lambda: self._update_job_stage("Downloading rendered video...", 0.0))
        self.after(0, lambda: self._append_log(f"[Download] Downloading finished file to {out_dir / out_name}..."))

        def download_progress(received, total):
            pct = (received / total) * 100.0 if total > 0 else 0
            self.after(0, lambda: self._update_download_progress(pct, received, total))

        t_dl_start = time.time()
        dl_res = net.download_output_file(
            job_id=job_id,
            target_path=out_dir / out_name,
            expected_checksum=expected_hash,
            progress_callback=download_progress
        )
        t_dl_duration = round(time.time() - t_dl_start, 2)

        if not dl_res.get("success"):
            err = dl_res.get("error", "Download error.")
            self.after(0, lambda: self._handle_job_failure(f"Download Error: {err}"))
            return

        total_job_time = round(time.time() - start_job_time, 2)
        self.after(0, lambda: self._handle_job_success(
            target_file=out_dir / out_name,
            upload_sec=t_up_duration,
            render_sec=t_render_duration,
            download_sec=t_dl_duration,
            total_sec=total_job_time,
            checksum=dl_res.get("checksum", "")
        ))

    # ---------------- UI State Updaters ----------------

    def _update_job_stage(self, stage_text: str, pct: float):
        self.lbl_stage.configure(text=f"Stage: {stage_text}")
        self.progress_bar.set(pct / 100.0)
        self.lbl_percent.configure(text=f"{pct:.1f}%")

    def _update_upload_progress(self, pct: float, sent: int, total: int):
        self.progress_bar.set(pct / 100.0)
        sent_mb = round(sent / (1024 * 1024), 1)
        total_mb = round(total / (1024 * 1024), 1)
        self.lbl_percent.configure(text=f"{pct:.1f}%")
        self.lbl_stage.configure(text=f"Stage: Uploading ({sent_mb}/{total_mb} MB)")

    def _update_render_progress(self, pct: float, elapsed: float, eta: Optional[float], speed: Optional[str], fps: Optional[float]):
        self.progress_bar.set(pct / 100.0)
        self.lbl_percent.configure(text=f"{pct:.1f}%")
        m, s = divmod(int(elapsed), 60)
        self.lbl_elapsed.configure(text=f"Elapsed: {m:02d}:{s:02d}")

        if eta is not None and eta > 0:
            em, es = divmod(int(eta), 60)
            self.lbl_eta.configure(text=f"ETA: {em:02d}:{es:02d}")
        else:
            self.lbl_eta.configure(text="ETA: Calculating...")

        detail_text = f"Stage: Remote GPU Rendering ({speed or '1.0x'}, {fps or 0:.0f} fps)"
        self.lbl_stage.configure(text=detail_text)

    def _update_download_progress(self, pct: float, received: int, total: int):
        self.progress_bar.set(pct / 100.0)
        rec_mb = round(received / (1024 * 1024), 1)
        tot_mb = round(total / (1024 * 1024), 1)
        self.lbl_percent.configure(text=f"{pct:.1f}%")
        self.lbl_stage.configure(text=f"Stage: Downloading ({rec_mb}/{tot_mb} MB)")

    def _handle_job_failure(self, error_message: str):
        self.btn_start_render.configure(state="normal")
        self.btn_cancel_job.configure(state="disabled")
        self.progress_bar.set(0.0)
        self.lbl_stage.configure(text="Stage: Failed")
        self.lbl_result_status.configure(text="❌ Job Failed", text_color=ACCENT_RED)
        self.lbl_result_details.configure(
            text=f"Reason: {error_message}\nRecovery: Check network connectivity, worker NVENC status, or enable CPU fallback."
        )
        self._append_log(f"[Failure] {error_message}")
        messagebox.showerror("Render Failed", error_message)

    def _handle_job_success(self, target_file: Path, upload_sec: float, render_sec: float, download_sec: float, total_sec: float, checksum: str):
        self.btn_start_render.configure(state="normal")
        self.btn_cancel_job.configure(state="disabled")
        self.progress_bar.set(1.0)
        self.lbl_percent.configure(text="100.0%")
        self.lbl_stage.configure(text="Stage: Completed Successfully")

        self.lbl_result_status.configure(text="✔ Remote Render & Download Complete", text_color=ACCENT_GREEN)
        summary_text = (
            f"Saved: {target_file.name}\n"
            f"Upload: {upload_sec}s | Render: {render_sec}s | Download: {download_sec}s | Total: {total_sec}s\n"
            f"SHA-256 Checksum Verified: {checksum[:20]}..."
        )
        self.lbl_result_details.configure(text=summary_text)
        self.btn_open_folder.pack(anchor="w", padx=12, pady=(0, 10))

        self._append_log(f"[Success] All phases completed in {total_sec}s.")
        self._append_log(f"[Integrity] Local checksum matched remote output SHA-256: {checksum}")
        messagebox.showinfo("Render Success", f"Remote GPU rendering complete!\nSaved to:\n{target_file}")

    def _on_cancel_job_clicked(self):
        if not self.active_job_id:
            return

        confirm = messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the active remote render job?")
        if not confirm:
            return

        self._append_log("[User] Cancelling active render job...")
        host = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        token = self.token_entry.get().strip()
        net = NetworkClient(host, port, token)

        def do_cancel():
            net.cancel_job(self.active_job_id)
            self.ws_stop_event.set()

        threading.Thread(target=do_cancel, daemon=True).start()

    def _on_open_folder_clicked(self):
        folder = Path(self.entry_out_dir.get().strip())
        if folder.exists():
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", str(folder)])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", str(folder)])

if __name__ == "__main__":
    app = App()
    app.mainloop()
