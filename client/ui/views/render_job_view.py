import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

from client.ui.theme import *
from client.services.network_client import NetworkClient

class RenderJobView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self.selected_file_path: Optional[Path] = None
        self.computed_checksum: Optional[str] = None

        self._build_file_picker_section()
        self._build_render_config_section()
        self._build_output_destination_section()
        self._build_submit_section()

    def _build_file_picker_section(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(card, text="1. Source Video Selection", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 8))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 12))

        self.btn_select_file = ctk.CTkButton(
            row,
            text="📁 Browse Video...",
            command=self._on_browse_clicked,
            fg_color="#374151",
            hover_color="#4B5563",
            height=36,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_select_file.pack(side="left", padx=(0, 12))

        self.lbl_filename = ctk.CTkLabel(row, text="No video selected", text_color=TEXT_MUTED, font=ctk.CTkFont(size=13))
        self.lbl_filename.pack(side="left", fill="x", expand=True)

        # File stats banner inside card
        self.stats_box = ctk.CTkFrame(card, fg_color=BG_MAIN, corner_radius=10)
        self.stats_box.pack(fill="x", padx=20, pady=(0, 16))

        self.lbl_file_size = ctk.CTkLabel(self.stats_box, text="File Size: --", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_file_size.pack(anchor="w", padx=14, pady=(10, 2))

        self.lbl_checksum = ctk.CTkLabel(self.stats_box, text="SHA-256 Checksum: --", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_checksum.pack(anchor="w", padx=14, pady=(0, 10))

    def _build_render_config_section(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(card, text="2. Transcoding & Render Settings", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 12))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 16))
        grid.grid_columnconfigure((0, 1), weight=1)

        # Resolution
        ctk.CTkLabel(grid, text="Resolution Preset", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.opt_resolution = ctk.CTkOptionMenu(
            grid,
            values=["Original", "720p", "1080p", "1440p", "4K"],
            command=self._on_setting_changed,
            fg_color=BG_INPUT,
            button_color="#374151"
        )
        self.opt_resolution.set(self.app.config_data.get("default_resolution", "1080p"))
        self.opt_resolution.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))

        # Bitrate
        ctk.CTkLabel(grid, text="Video Target Bitrate", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.opt_bitrate = ctk.CTkOptionMenu(
            grid,
            values=["2M", "5M", "8M", "12M", "20M"],
            command=self._on_setting_changed,
            fg_color=BG_INPUT,
            button_color="#374151"
        )
        self.opt_bitrate.set(self.app.config_data.get("default_bitrate", "5M"))
        self.opt_bitrate.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 12))

        # NVENC Preset
        ctk.CTkLabel(grid, text="NVENC Encoder Preset", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.opt_preset = ctk.CTkOptionMenu(
            grid,
            values=["p1 (Fastest)", "p2", "p3", "p4 (Medium)", "p5", "p6", "p7 (Slowest)"],
            command=self._on_setting_changed,
            fg_color=BG_INPUT,
            button_color="#374151"
        )
        self.opt_preset.set("p4 (Medium)")
        self.opt_preset.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(0, 12))

        # CPU Fallback
        self.chk_cpu = ctk.CTkCheckBox(
            grid,
            text="Allow CPU Fallback (libx264 if NVENC absent)",
            font=ctk.CTkFont(size=12),
            checkbox_height=20,
            checkbox_width=20
        )
        if self.app.config_data.get("allow_cpu_fallback", False):
            self.chk_cpu.select()
        self.chk_cpu.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(0, 12))

    def _build_output_destination_section(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(card, text="3. Output Filename & Directory", font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(16, 12))

        ctk.CTkLabel(card, text="Output Video Name", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(0, 4))
        self.entry_out_name = ctk.CTkEntry(card, placeholder_text="rendered_video.mp4", fg_color=BG_INPUT, border_color=BORDER_COLOR)
        self.entry_out_name.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(card, text="Download Destination Directory", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=(0, 4))
        dir_row = ctk.CTkFrame(card, fg_color="transparent")
        dir_row.pack(fill="x", padx=20, pady=(0, 16))

        self.entry_out_dir = ctk.CTkEntry(dir_row, fg_color=BG_INPUT, border_color=BORDER_COLOR)
        self.entry_out_dir.insert(0, str(self.app.config_data.get("output_dir", str(Path.home() / "Downloads"))))
        self.entry_out_dir.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse_dir = ctk.CTkButton(
            dir_row,
            text="Browse...",
            width=80,
            command=self._on_browse_dir_clicked,
            fg_color="#374151"
        )
        btn_browse_dir.pack(side="right")

    def _build_submit_section(self):
        self.btn_submit = ctk.CTkButton(
            self,
            text="🚀 Offload to Remote GPU Worker",
            command=self._on_submit_clicked,
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            height=46,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.btn_submit.pack(fill="x", padx=10, pady=(0, 20))

    def _on_browse_clicked(self):
        filetypes = [
            ("Video Files", "*.mp4 *.mkv *.mov *.avi *.wmv *.flv *.ts"),
            ("All Files", "*.*")
        ]
        chosen = filedialog.askopenfilename(title="Select Video to Offload", filetypes=filetypes)
        if not chosen:
            return

        p = Path(chosen)
        self.selected_file_path = p
        self.lbl_filename.configure(text=p.name, text_color=TEXT_PRIMARY)

        # Set output filename
        stem = p.stem
        ext = p.suffix or ".mp4"
        res_str = self.opt_resolution.get()
        self.entry_out_name.delete(0, "end")
        self.entry_out_name.insert(0, f"{stem}_remote_{res_str}{ext}")

        # Size
        sz = p.stat().st_size
        self.lbl_file_size.configure(text=f"File Size: {sz / (1024*1024):.2f} MB ({sz:,} bytes)")
        self.lbl_checksum.configure(text="SHA-256 Checksum: Computing in background...", text_color=ACCENT_YELLOW)

        def calc():
            net = NetworkClient()
            h = net.compute_sha256(p)
            self.computed_checksum = h
            self.after(0, lambda: self.lbl_checksum.configure(
                text=f"SHA-256 Checksum: {h[:16]}...{h[-8:]} (Verified)",
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
            ext = self.selected_file_path.suffix or ".mp4"
            res_str = self.opt_resolution.get()
            self.entry_out_name.delete(0, "end")
            self.entry_out_name.insert(0, f"{stem}_remote_{res_str}{ext}")

    def _on_submit_clicked(self):
        if not self.app.is_connected:
            messagebox.showwarning("Connection Required", "Please connect to the worker server first (Test Connection in Dashboard or Settings).")
            self.app.navigate_to("dashboard")
            return

        if not self.selected_file_path or not self.selected_file_path.exists():
            messagebox.showwarning("File Missing", "Please select a valid input video file.")
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

        # Prepare parameters
        job_params = {
            "input_file": self.selected_file_path,
            "checksum": self.computed_checksum,
            "resolution": self.opt_resolution.get(),
            "bitrate": self.opt_bitrate.get(),
            "preset": self.opt_preset.get().split(" ")[0],
            "output_name": out_name,
            "output_dir": out_dir,
            "allow_cpu": bool(self.chk_cpu.get())
        }

        # Navigate to Active Job monitor and dispatch
        self.app.start_render_job(job_params)
