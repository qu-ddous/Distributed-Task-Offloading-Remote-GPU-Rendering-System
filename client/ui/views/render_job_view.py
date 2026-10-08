import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional
import customtkinter as ctk

from client.ui.theme import *
from client.services.network_client import NetworkClient

class RenderJobView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self.selected_file_path: Optional[Path] = None
        self.computed_checksum: Optional[str] = None
        self.current_task_mode = "video" # "video", "python", "batch"

        self._build_banner_section()
        self._build_task_mode_selector()
        self._build_file_picker_section()
        self._build_render_config_section()
        self._build_output_destination_section()
        self._build_submit_section()
        self.update_connection_status(self.app.is_connected)

    def on_page_shown(self):
        """Called whenever user switches to the New Render Job tab."""
        self.update_connection_status(self.app.is_connected)

    def _build_banner_section(self):
        self.banner_frame = ctk.CTkFrame(self, fg_color="#FEE2E2", corner_radius=14, border_width=1, border_color="#FCA5A5")
        self.banner_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_server_banner = ctk.CTkLabel(
            self.banner_frame,
            text="🔴 WORKER SERVER OFFLINE: Jab tak dosra PC connect nahi hoga, tab tak render submit nahi ho sakta.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT_RED,
            padx=16,
            pady=10
        )
        self.lbl_server_banner.pack(anchor="w")

    def _build_task_mode_selector(self):
        mode_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        mode_card.pack(fill="x", padx=10, pady=(0, 14))

        box = ctk.CTkFrame(mode_card, fg_color="transparent")
        box.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(box, text="Task Profile:", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(side="left", padx=(0, 12))

        self.btn_mode_video = ctk.CTkButton(
            box,
            text="🎬  Video Transcode (GPU)",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            corner_radius=8,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            command=lambda: self._set_task_mode("video")
        )
        self.btn_mode_video.pack(side="left", padx=(0, 8))

        self.btn_mode_python = ctk.CTkButton(
            box,
            text="🧠  Python / AI Model (100% Server)",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            corner_radius=8,
            fg_color=BG_CARD_ALT,
            text_color=TEXT_SECONDARY,
            hover_color="#DBEAFE",
            command=lambda: self._set_task_mode("python")
        )
        self.btn_mode_python.pack(side="left", padx=(0, 8))

        self.btn_mode_batch = ctk.CTkButton(
            box,
            text="⚡  Batch / Shell Script",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=32,
            corner_radius=8,
            fg_color=BG_CARD_ALT,
            text_color=TEXT_SECONDARY,
            hover_color="#DBEAFE",
            command=lambda: self._set_task_mode("batch")
        )
        self.btn_mode_batch.pack(side="left")

    def _set_task_mode(self, mode: str):
        self.current_task_mode = mode
        # Reset button styles
        buttons = [("video", self.btn_mode_video), ("python", self.btn_mode_python), ("batch", self.btn_mode_batch)]
        for m, btn in buttons:
            if m == mode:
                btn.configure(fg_color=ACCENT_BLUE, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=BG_CARD_ALT, text_color=TEXT_SECONDARY)

        if mode == "video":
            self.lbl_card1_title.configure(text="1. Select Video to Offload")
            self.btn_select_file.configure(text="📁  Browse Video File...")
            self.lbl_config_title.configure(text="2. Transcode & Output Settings")
            self.video_config_frame.pack(fill="x", padx=22, pady=(0, 20))
            self.compute_config_frame.pack_forget()
            self.lbl_out_name_title.configure(text="Output Video Filename")
        elif mode == "python":
            self.lbl_card1_title.configure(text="1. Select Python Script to Offload")
            self.btn_select_file.configure(text="🐍  Browse Python (.py)...")
            self.lbl_config_title.configure(text="2. Remote Compute & Hardware Profile")
            self.video_config_frame.pack_forget()
            self.compute_config_frame.pack(fill="x", padx=22, pady=(0, 20))
            self.lbl_out_name_title.configure(text="Result / Artifact Filename")
        else:
            self.lbl_card1_title.configure(text="1. Select Batch / Script to Offload")
            self.btn_select_file.configure(text="📜  Browse Script (.bat/.ps1)...")
            self.lbl_config_title.configure(text="2. Remote Shell Execution Profile")
            self.video_config_frame.pack_forget()
            self.compute_config_frame.pack(fill="x", padx=22, pady=(0, 20))
            self.lbl_out_name_title.configure(text="Execution Log Filename")

        self.update_connection_status(self.app.is_connected)
        self._on_setting_changed()

    def update_connection_status(self, is_online: bool):
        if is_online:
            self.banner_frame.configure(fg_color="#D1FAE5", border_color="#86EFAC")
            self.lbl_server_banner.configure(
                text="✅ WORKER SERVER ONLINE: Remote compute node connected. Task direct offload ho sakta hai.",
                text_color=ACCENT_GREEN
            )
            submit_labels = {
                "video": "🚀  Submit & Render on Remote GPU",
                "python": "🧠  Submit & Run / Train on Server Hardware",
                "batch": "⚡  Submit & Execute Script on Server"
            }
            btn_txt = submit_labels.get(getattr(self, "current_task_mode", "video"), "🚀  Submit Task to Server")
            self.btn_submit.configure(
                state="normal",
                fg_color=ACCENT_GREEN,
                hover_color=ACCENT_GREEN_HOVER,
                text_color="#FFFFFF",
                text=btn_txt
            )
        else:
            self.banner_frame.configure(fg_color="#FEE2E2", border_color="#FCA5A5")
            self.lbl_server_banner.configure(
                text="🔴 WORKER SERVER OFFLINE: Dosra PC connect nahi hai. Host & Settings mein ja kar connect karein.",
                text_color=ACCENT_RED
            )
            self.btn_submit.configure(
                state="disabled",
                fg_color="#CBD5E1",
                text_color="#64748B",
                text="🔒 Worker Server Disconnected (Connect in Host & Settings)"
            )

    def _build_file_picker_section(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        # Header with blue badge
        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=22, pady=(18, 12))

        self.ic_card1 = ctk.CTkLabel(h_row, text="📁", font=ctk.CTkFont(size=15), fg_color="#DBEAFE", corner_radius=8, width=32, height=32)
        self.ic_card1.pack(side="left", padx=(0, 10))

        self.lbl_card1_title = ctk.CTkLabel(h_row, text="1. Select Video to Offload", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_card1_title.pack(side="left")

        # Two-column content (Button on left, details on right)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(0, 20))
        row.grid_columnconfigure(0, weight=0)
        row.grid_columnconfigure(1, weight=1)

        self.btn_select_file = ctk.CTkButton(
            row,
            text="📁  Browse Video File...",
            command=self._on_browse_clicked,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            height=44,
            width=210,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_select_file.grid(row=0, column=0, sticky="nw", padx=(0, 16))

        # File metadata clay box on right
        self.stats_box = ctk.CTkFrame(row, fg_color=BG_CARD_ALT, corner_radius=12)
        self.stats_box.grid(row=0, column=1, sticky="nsew")

        self.lbl_filename = ctk.CTkLabel(
            self.stats_box,
            text="No file selected yet",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.lbl_filename.pack(fill="x", padx=16, pady=(12, 2))

        self.lbl_file_size = ctk.CTkLabel(
            self.stats_box,
            text="File Size: --",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            anchor="w"
        )
        self.lbl_file_size.pack(fill="x", padx=16, pady=(0, 4))

        self.lbl_checksum = ctk.CTkLabel(
            self.stats_box,
            text="● SHA-256 Checksum: Awaiting file selection",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_DIM,
            anchor="w"
        )
        self.lbl_checksum.pack(fill="x", padx=16, pady=(0, 12))

    def _build_render_config_section(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        # Header with purple badge
        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=22, pady=(18, 12))

        ic = ctk.CTkLabel(h_row, text="⚙️", font=ctk.CTkFont(size=15), fg_color="#EDE9FE", corner_radius=8, width=32, height=32)
        ic.pack(side="left", padx=(0, 10))

        self.lbl_config_title = ctk.CTkLabel(h_row, text="2. Transcode & Output Settings", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_config_title.pack(side="left")

        # 1. Video Transcode Configuration Frame
        self.video_config_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.video_config_frame.pack(fill="x", padx=22, pady=(0, 20))
        self.video_config_frame.grid_columnconfigure((0, 1), weight=1)

        # Resolution
        ctk.CTkLabel(self.video_config_frame, text="Resolution Preset", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.opt_resolution = ctk.CTkOptionMenu(
            self.video_config_frame,
            values=["Original", "720p", "1080p", "1440p", "4K"],
            command=self._on_setting_changed,
            fg_color="#F1F5F9",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=38
        )
        self.opt_resolution.set(self.app.config_data.get("default_resolution", "Original"))
        self.opt_resolution.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))

        # Bitrate
        ctk.CTkLabel(self.video_config_frame, text="Video Target Bitrate", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.opt_bitrate = ctk.CTkOptionMenu(
            self.video_config_frame,
            values=["2M", "5M", "8M", "12M", "20M"],
            command=self._on_setting_changed,
            fg_color="#F1F5F9",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=38
        )
        self.opt_bitrate.set(self.app.config_data.get("default_bitrate", "5M"))
        self.opt_bitrate.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 14))

        # NVENC Preset
        ctk.CTkLabel(self.video_config_frame, text="NVENC Encoder Preset", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.opt_preset = ctk.CTkOptionMenu(
            self.video_config_frame,
            values=["p1 (Fastest)", "p2", "p3", "p4 (Medium)", "p5", "p6", "p7 (Slowest)"],
            command=self._on_setting_changed,
            fg_color="#F1F5F9",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=38
        )
        self.opt_preset.set("p4 (Medium)")
        self.opt_preset.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 6))

        # CPU Fallback Checkbox
        self.chk_cpu = ctk.CTkCheckBox(
            self.video_config_frame,
            text="Allow CPU Fallback (libx264 if NVENC absent)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_SECONDARY,
            checkbox_height=22,
            checkbox_width=22,
            corner_radius=6,
            fg_color=ACCENT_BLUE
        )
        if self.app.config_data.get("allow_cpu_fallback", True):
            self.chk_cpu.select()
        self.chk_cpu.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(12, 6))

        # 2. General Compute & AI Script Configuration Frame
        self.compute_config_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.compute_config_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.compute_config_frame, text="Execution Acceleration Profile", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.opt_accel = ctk.CTkOptionMenu(
            self.compute_config_frame,
            values=["Auto-Detect (CUDA GPU / PyTorch)", "Dedicated NVIDIA GPU Preferred", "Server Multi-Core CPU High-Performance"],
            fg_color="#F1F5F9",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=38
        )
        self.opt_accel.set("Auto-Detect (CUDA GPU / PyTorch)")
        self.opt_accel.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))

        ctk.CTkLabel(self.compute_config_frame, text="Output Artifact Delivery", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.opt_out_mode = ctk.CTkOptionMenu(
            self.compute_config_frame,
            values=["Capture Live Execution Log & Output Files", "Standard Script Output Stream"],
            fg_color="#F1F5F9",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=38
        )
        self.opt_out_mode.set("Capture Live Execution Log & Output Files")
        self.opt_out_mode.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 14))

    def _build_output_destination_section(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        # Header with green badge
        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=22, pady=(18, 12))

        ic = ctk.CTkLabel(h_row, text="📁", font=ctk.CTkFont(size=15), fg_color="#D1FAE5", corner_radius=8, width=32, height=32)
        ic.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(h_row, text="3. Output File & Location", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")

        self.lbl_out_name_title = ctk.CTkLabel(card, text="Output Video Filename", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY)
        self.lbl_out_name_title.pack(anchor="w", padx=22, pady=(0, 4))
        self.entry_out_name = ctk.CTkEntry(
            card,
            placeholder_text="rendered_video.mp4",
            fg_color=BG_INPUT,
            border_color=BORDER_COLOR,
            corner_radius=10,
            height=38,
            text_color=TEXT_PRIMARY
        )
        self.entry_out_name.pack(fill="x", padx=22, pady=(0, 14))

        ctk.CTkLabel(card, text="Download Directory", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=22, pady=(0, 4))
        dir_row = ctk.CTkFrame(card, fg_color="transparent")
        dir_row.pack(fill="x", padx=22, pady=(0, 20))

        self.entry_out_dir = ctk.CTkEntry(
            dir_row,
            fg_color=BG_INPUT,
            border_color=BORDER_COLOR,
            corner_radius=10,
            height=38,
            text_color=TEXT_PRIMARY
        )
        self.entry_out_dir.insert(0, str(self.app.config_data.get("output_dir", str(Path.home() / "Downloads"))))
        self.entry_out_dir.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse_dir = ctk.CTkButton(
            dir_row,
            text="Browse...",
            width=95,
            height=38,
            corner_radius=10,
            command=self._on_browse_dir_clicked,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_browse_dir.pack(side="right")

    def _build_submit_section(self):
        self.btn_submit = ctk.CTkButton(
            self,
            text="🚀  Submit & Render on Remote GPU",
            command=self._on_submit_clicked,
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            height=48,
            corner_radius=14,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.btn_submit.pack(fill="x", padx=10, pady=(0, 20))

    def _on_browse_clicked(self):
        if self.current_task_mode == "video":
            filetypes = [
                ("Video Files", "*.mp4 *.mkv *.mov *.avi *.wmv *.flv *.ts"),
                ("All Files", "*.*")
            ]
            title = "Select Video to Offload"
        elif self.current_task_mode == "python":
            filetypes = [
                ("Python Scripts & AI Models", "*.py *.pyw *.ipynb"),
                ("All Files", "*.*")
            ]
            title = "Select Python Script to Offload"
        else:
            filetypes = [
                ("Script / Batch Files", "*.bat *.cmd *.ps1"),
                ("All Files", "*.*")
            ]
            title = "Select Script / Batch to Offload"

        chosen = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if not chosen:
            return

        p = Path(chosen)
        self.selected_file_path = p
        self.lbl_filename.configure(text=p.name, text_color=TEXT_PRIMARY)

        # Set default output filename based on active mode
        self._on_setting_changed()

        # Size & SHA-256
        sz = p.stat().st_size
        self.lbl_file_size.configure(text=f"File Size: {sz / (1024*1024):.2f} MB ({sz:,} bytes)" if sz >= 1024*1024 else f"File Size: {sz / 1024:.1f} KB ({sz:,} bytes)")
        self.lbl_checksum.configure(text="SHA-256 Checksum: Computing checksum...", text_color=ACCENT_ORANGE)

        def calc():
            net = NetworkClient()
            h = net.compute_sha256(p)
            self.computed_checksum = h
            self.after(0, lambda: self.lbl_checksum.configure(
                text=f"✔ SHA-256 Checksum: {h[:16]}...{h[-8:]} (Verified)",
                text_color=ACCENT_GREEN
            ))
        threading.Thread(target=calc, daemon=True).start()

    def _on_browse_dir_clicked(self):
        chosen = filedialog.askdirectory(title="Select Download Directory")
        if chosen:
            self.entry_out_dir.delete(0, "end")
            self.entry_out_dir.insert(0, chosen)
            self.app.config_data["output_dir"] = chosen
            self.app.save_config()

    def _on_setting_changed(self, _=None):
        if self.selected_file_path:
            stem = self.selected_file_path.stem
            if self.current_task_mode == "video":
                ext = self.selected_file_path.suffix or ".mp4"
                res_str = self.opt_resolution.get()
                self.entry_out_name.delete(0, "end")
                self.entry_out_name.insert(0, f"{stem}_remote_{res_str}{ext}")
            elif self.current_task_mode == "python":
                self.entry_out_name.delete(0, "end")
                self.entry_out_name.insert(0, f"{stem}_execution.log")
            else:
                self.entry_out_name.delete(0, "end")
                self.entry_out_name.insert(0, f"{stem}_result.log")

    def _on_submit_clicked(self):
        if not self.app.is_connected:
            messagebox.showwarning("Connection Required", "Please connect to the worker server first (Test Connection in Dashboard or Settings).")
            self.app.navigate_to("dashboard")
            return

        if not self.selected_file_path or not self.selected_file_path.exists():
            messagebox.showwarning("File Missing", "Please select a valid input file to offload.")
            return

        if not self.computed_checksum:
            messagebox.showinfo("Please Wait", "Still calculating SHA-256 checksum for the file. Try again in a few moments.")
            return

        out_name = self.entry_out_name.get().strip()
        out_dir = Path(self.entry_out_dir.get().strip())
        if not out_name:
            messagebox.showwarning("Filename", "Please specify an output filename.")
            return

        dest_file = out_dir / out_name
        if dest_file.exists():
            if not messagebox.askyesno("Confirm Overwrite", f"File exists:\n{dest_file}\n\nOverwrite when finished?"):
                return

        job_params = {
            "input_file": self.selected_file_path,
            "checksum": self.computed_checksum,
            "resolution": self.opt_resolution.get(),
            "bitrate": self.opt_bitrate.get(),
            "preset": self.opt_preset.get().split(" ")[0],
            "output_name": out_name,
            "output_dir": out_dir,
            "allow_cpu": bool(self.chk_cpu.get()),
            "task_mode": self.current_task_mode
        }

        self.app.start_render_job(job_params)
