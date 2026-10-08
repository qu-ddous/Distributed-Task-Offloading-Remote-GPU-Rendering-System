import customtkinter as ctk

from client.ui.theme import *
from server.ui.config_manager import server_config_manager

class ServerSettingsView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller
        self.config_data = server_config_manager.load()

        self._build_subtabs_header()
        self._build_settings_form()

    def on_page_shown(self):
        """Called immediately when user navigates to Settings tab."""
        self.config_data = server_config_manager.load()
        self.opt_max_jobs.set(str(self.config_data.get("max_concurrent_jobs", 3)))
        self.opt_res.set(self.config_data.get("default_resolution", "1920 x 1080 (1080p)"))
        self.opt_bitrate.set(self.config_data.get("default_bitrate", "5 Mbps"))
        self.opt_preset.set(self.config_data.get("default_preset", "P4 - Balanced"))
        self.opt_cont.set(self.config_data.get("default_container", "MP4 (H.264)"))

    def _build_subtabs_header(self):
        nav_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        nav_box.pack(fill="x", padx=4, pady=(0, 14))

        top = ctk.CTkFrame(nav_box, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=10)

        # Tab Pills matching image 1
        tabs = [
            ("⚙️ Server Settings", True),
            ("🎬 Render Defaults", False),
            ("📁 Storage & Files", False),
            ("🔒 Security", False)
        ]
        for t_label, is_act in tabs:
            btn = ctk.CTkButton(
                top,
                text=t_label,
                font=ctk.CTkFont(size=11, weight="bold"),
                height=32,
                corner_radius=8,
                fg_color=ACCENT_BLUE if is_act else "transparent",
                text_color="#FFFFFF" if is_act else TEXT_SECONDARY,
                hover_color=ACCENT_BLUE_HOVER if is_act else "#D8E2F0"
            )
            btn.pack(side="left", padx=(0, 8))

    def _build_settings_form(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(0, 14))
        row.grid_columnconfigure((0, 1), weight=1)

        # Left Column: Server Startup & Files
        left_box = ctk.CTkFrame(row, fg_color="transparent")
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        # 1. Server Configuration
        c1 = ctk.CTkFrame(left_box, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c1.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(c1, text="🖥️  Server Startup", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(16, 12))

        # Start automatically switch
        self.sw_auto = ctk.CTkSwitch(c1, text="Start server automatically on Windows startup", font=ctk.CTkFont(size=11, weight="bold"), progress_color=ACCENT_BLUE)
        self.sw_auto.pack(anchor="w", padx=18, pady=4)

        # Minimize to tray
        self.sw_tray = ctk.CTkSwitch(c1, text="Minimize to system tray", font=ctk.CTkFont(size=11, weight="bold"), progress_color=ACCENT_BLUE)
        self.sw_tray.pack(anchor="w", padx=18, pady=4)

        # Auto-reconnect
        self.sw_reconn = ctk.CTkSwitch(c1, text="Auto-reconnect on network loss", font=ctk.CTkFont(size=11, weight="bold"), progress_color=ACCENT_BLUE)
        self.sw_reconn.select()
        self.sw_reconn.pack(anchor="w", padx=18, pady=4)

        # Max concurrent jobs
        ctk.CTkLabel(c1, text="Max concurrent jobs:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18, pady=(8, 2))
        self.opt_max_jobs = ctk.CTkOptionMenu(
            c1,
            values=["1", "2", "3", "4"],
            height=34,
            corner_radius=8,
            fg_color=BG_CARD_ALT,
            text_color=TEXT_PRIMARY,
            button_color="#E2E8F0"
        )
        self.opt_max_jobs.set(str(self.config_data.get("max_concurrent_jobs", 3)))
        self.opt_max_jobs.pack(fill="x", padx=18, pady=(0, 16))

        # 2. Storage & Temporary Folders
        c2 = ctk.CTkFrame(left_box, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c2.pack(fill="x")

        ctk.CTkLabel(c2, text="📁  Storage & Files", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(16, 12))

        # Output Folder
        ctk.CTkLabel(c2, text="Output folder:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18)
        self.ent_out = ctk.CTkEntry(c2, height=34, corner_radius=8, fg_color=BG_INPUT, border_color=BORDER_COLOR)
        self.ent_out.insert(0, self.config_data.get("output_folder", "C:\\RenderCache\\output"))
        self.ent_out.pack(fill="x", padx=18, pady=(2, 8))

        # Temp Folder
        ctk.CTkLabel(c2, text="Temp folder:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18)
        self.ent_temp = ctk.CTkEntry(c2, height=34, corner_radius=8, fg_color=BG_INPUT, border_color=BORDER_COLOR)
        self.ent_temp.insert(0, self.config_data.get("temp_folder", "C:\\RenderCache\\temp"))
        self.ent_temp.pack(fill="x", padx=18, pady=(2, 8))

        # Auto clean
        self.sw_clean = ctk.CTkSwitch(c2, text="Automatically clean temp files after delivery", font=ctk.CTkFont(size=11, weight="bold"), progress_color=ACCENT_BLUE)
        if self.config_data.get("auto_clean_temp", True):
            self.sw_clean.select()
        self.sw_clean.pack(anchor="w", padx=18, pady=(4, 18))

        # Right Column: Render Defaults & Other Settings
        right_box = ctk.CTkFrame(row, fg_color="transparent")
        right_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # 3. Render Defaults
        c3 = ctk.CTkFrame(right_box, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c3.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(c3, text="🎬  Render Defaults", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(16, 12))

        # Default Resolution
        ctk.CTkLabel(c3, text="Default resolution:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18)
        self.opt_res = ctk.CTkOptionMenu(c3, values=["1920 x 1080 (1080p)", "2560 x 1440 (1440p)", "3840 x 2160 (4K)", "Original"], height=34, corner_radius=8, fg_color=BG_CARD_ALT, text_color=TEXT_PRIMARY, button_color="#E2E8F0")
        self.opt_res.set(self.config_data.get("default_resolution", "1920 x 1080 (1080p)"))
        self.opt_res.pack(fill="x", padx=18, pady=(2, 8))

        # Default Bitrate
        ctk.CTkLabel(c3, text="Default video bitrate:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18)
        self.opt_bitrate = ctk.CTkOptionMenu(c3, values=["5 Mbps", "8 Mbps", "15 Mbps", "25 Mbps"], height=34, corner_radius=8, fg_color=BG_CARD_ALT, text_color=TEXT_PRIMARY, button_color="#E2E8F0")
        self.opt_bitrate.set(self.config_data.get("default_bitrate", "5 Mbps"))
        self.opt_bitrate.pack(fill="x", padx=18, pady=(2, 8))

        # Encoder Preset
        ctk.CTkLabel(c3, text="Encoder preset:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18)
        self.opt_preset = ctk.CTkOptionMenu(c3, values=["P1 - Fastest", "P4 - Balanced", "P7 - Best Quality"], height=34, corner_radius=8, fg_color=BG_CARD_ALT, text_color=TEXT_PRIMARY, button_color="#E2E8F0")
        self.opt_preset.set(self.config_data.get("default_preset", "P4 - Balanced"))
        self.opt_preset.pack(fill="x", padx=18, pady=(2, 8))

        # Default Container
        ctk.CTkLabel(c3, text="Default container:", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18)
        self.opt_cont = ctk.CTkOptionMenu(c3, values=["MP4 (H.264)", "MKV (HEVC)", "MOV (ProRes)"], height=34, corner_radius=8, fg_color=BG_CARD_ALT, text_color=TEXT_PRIMARY, button_color="#E2E8F0")
        self.opt_cont.set(self.config_data.get("default_container", "MP4 (H.264)"))
        self.opt_cont.pack(fill="x", padx=18, pady=(2, 16))

        # 4. Other Settings
        c4 = ctk.CTkFrame(right_box, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c4.pack(fill="x")

        ctk.CTkLabel(c4, text="⚙️  Other Settings", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(16, 12))

        self.sw_cpu = ctk.CTkSwitch(c4, text="Enable CPU fallback (Use CPU when GPU is unavailable)", font=ctk.CTkFont(size=11, weight="bold"), progress_color=ACCENT_BLUE)
        if self.config_data.get("allow_cpu_fallback", True):
            self.sw_cpu.select()
        self.sw_cpu.pack(anchor="w", padx=18, pady=4)

        # Log retention
        ctk.CTkLabel(c4, text="Log retention (days):", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=18, pady=(8, 2))
        self.ent_ret = ctk.CTkEntry(c4, height=34, corner_radius=8, fg_color=BG_INPUT, border_color=BORDER_COLOR)
        self.ent_ret.insert(0, str(self.config_data.get("log_retention_days", 30)))
        self.ent_ret.pack(fill="x", padx=18, pady=(0, 16))

        # Bottom Action Bar
        bottom_box = ctk.CTkFrame(self, fg_color="transparent")
        bottom_box.pack(fill="x", padx=4, pady=10)

        btn_restore = ctk.CTkButton(
            bottom_box,
            text="🔄 Restore Defaults",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8,
            height=36,
            width=150,
            command=self._restore_defaults
        )
        btn_restore.pack(side="left")

        btn_save = ctk.CTkButton(
            bottom_box,
            text="💾 Save Settings",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            corner_radius=8,
            height=36,
            width=150,
            command=self._save_settings
        )
        btn_save.pack(side="right")

        self.lbl_save_status = ctk.CTkLabel(bottom_box, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_save_status.pack(side="right", padx=12)

    def _restore_defaults(self):
        self.ent_out.delete(0, "end")
        self.ent_out.insert(0, "C:\\RenderCache\\output")
        self.ent_temp.delete(0, "end")
        self.ent_temp.insert(0, "C:\\RenderCache\\temp")
        self.opt_res.set("1920 x 1080 (1080p)")
        self.opt_bitrate.set("5 Mbps")
        self.opt_preset.set("P4 - Balanced")
        self.opt_cont.set("MP4 (H.264)")
        self.opt_max_jobs.set("3")
        self.sw_clean.select()
        self.sw_cpu.select()
        self.lbl_save_status.configure(text="Defaults restored! Click Save.", text_color=ACCENT_BLUE)

    def _save_settings(self):
        self.config_data["output_folder"] = self.ent_out.get().strip()
        self.config_data["temp_folder"] = self.ent_temp.get().strip()
        self.config_data["default_resolution"] = self.opt_res.get()
        self.config_data["default_bitrate"] = self.opt_bitrate.get()
        self.config_data["default_preset"] = self.opt_preset.get()
        self.config_data["default_container"] = self.opt_cont.get()
        self.config_data["max_concurrent_jobs"] = int(self.opt_max_jobs.get())
        self.config_data["auto_clean_temp"] = bool(self.sw_clean.get())
        self.config_data["allow_cpu_fallback"] = bool(self.sw_cpu.get())

        server_config_manager.save(self.config_data)
        self.lbl_save_status.configure(text="Settings saved successfully!", text_color=ACCENT_GREEN)
        self.after(3000, lambda: self.lbl_save_status.configure(text=""))
