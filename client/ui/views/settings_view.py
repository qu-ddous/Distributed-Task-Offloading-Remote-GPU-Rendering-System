from pathlib import Path
from tkinter import messagebox, filedialog
import customtkinter as ctk

from client.ui.theme import *
from client.services.network_client import NetworkClient

class SettingsView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_connection_card()
        self._build_defaults_card()
        self._build_watch_folder_card()

    def on_page_shown(self):
        """Called whenever user switches to the Settings tab."""
        curr_host = self.app.config_data.get("server_host", "127.0.0.1")
        curr_port = self.app.config_data.get("server_port", 8000)
        self._update_badge(self.app.is_connected, curr_host, curr_port)

    def _build_connection_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=22, pady=(18, 4))

        ic = ctk.CTkLabel(h_row, text="🌐", font=ctk.CTkFont(size=16), fg_color="#DBEAFE", corner_radius=8, width=34, height=34)
        ic.pack(side="left", padx=(0, 12))

        t_box = ctk.CTkFrame(h_row, fg_color="transparent")
        t_box.pack(side="left", fill="both")
        ctk.CTkLabel(t_box, text="Remote Worker Host Connection", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(t_box, text="Specify the GPU worker's LAN IP address, port, and security token.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=(14, 18))
        grid.grid_columnconfigure(0, weight=3)
        grid.grid_columnconfigure(1, weight=1)

        # Worker Host IP
        ctk.CTkLabel(grid, text="Worker IPv4 Address", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.entry_host = ctk.CTkEntry(grid, placeholder_text="192.168.1.150", fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY)
        self.entry_host.insert(0, str(self.app.config_data.get("server_host", "127.0.0.1")))
        self.entry_host.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))

        # Port
        ctk.CTkLabel(grid, text="Port", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.entry_port = ctk.CTkEntry(grid, placeholder_text="8000", fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY)
        self.entry_port.insert(0, str(self.app.config_data.get("server_port", 8000)))
        self.entry_port.grid(row=1, column=1, sticky="ew", pady=(0, 14))

        # API Token
        ctk.CTkLabel(grid, text="Shared API Secret Token (X-API-Token)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.entry_token = ctk.CTkEntry(grid, show="•", placeholder_text="Enter secret token matching worker .env", fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY)
        self.entry_token.insert(0, str(self.app.config_data.get("api_token", "")))
        self.entry_token.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # Action row (Buttons & Verified Badge)
        act_row = ctk.CTkFrame(card, fg_color="transparent")
        act_row.pack(fill="x", padx=22, pady=(0, 20))

        self.btn_test = ctk.CTkButton(
            act_row,
            text="🔄  Test & Connect",
            command=self._on_test_handshake_clicked,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            corner_radius=10,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_test.pack(side="left", padx=(0, 8))

        self.btn_disconnect = ctk.CTkButton(
            act_row,
            text="🔌  Disconnect",
            command=self._on_disconnect_clicked,
            fg_color="#FEE2E2",
            hover_color="#FECACA",
            text_color=ACCENT_RED,
            corner_radius=10,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_disconnect.pack(side="left", padx=(0, 8))

        self.btn_reset = ctk.CTkButton(
            act_row,
            text="🗑️  Reset Connection",
            command=self._on_reset_connection_clicked,
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color=TEXT_SECONDARY,
            corner_radius=10,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_reset.pack(side="left")

        curr_host = self.app.config_data.get("server_host", "127.0.0.1")
        curr_port = self.app.config_data.get("server_port", 8000)
        self.lbl_verified_badge = ctk.CTkLabel(
            act_row,
            text=f"✔ Connected: {curr_host}:{curr_port}" if self.app.is_connected else "● Disconnected",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT_GREEN if self.app.is_connected else ACCENT_RED,
            fg_color="#D1FAE5" if self.app.is_connected else "#FEE2E2",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.lbl_verified_badge.pack(side="right")

    def _update_badge(self, is_online: bool, host: str = "", port: Any = ""):
        if is_online:
            self.lbl_verified_badge.configure(
                text=f"✔ Connected: {host}:{port}",
                text_color=ACCENT_GREEN,
                fg_color="#D1FAE5"
            )
        else:
            self.lbl_verified_badge.configure(
                text="● Disconnected",
                text_color=ACCENT_RED,
                fg_color="#FEE2E2"
            )

    def _build_defaults_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=22, pady=(18, 4))

        ic = ctk.CTkLabel(h_row, text="⚙️", font=ctk.CTkFont(size=16), fg_color="#EDE9FE", corner_radius=8, width=34, height=34)
        ic.pack(side="left", padx=(0, 12))

        t_box = ctk.CTkFrame(h_row, fg_color="transparent")
        t_box.pack(side="left", fill="both")
        ctk.CTkLabel(t_box, text="Default Render Preferences", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(t_box, text="Set preferred resolution and fallback settings for new render tasks.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w")

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=22, pady=(14, 14))
        row1.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row1, text="Default Resolution", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.opt_def_res = ctk.CTkOptionMenu(row1, values=["Original", "720p", "1080p", "1440p", "4K"], fg_color="#F1F5F9", button_color="#E2E8F0", button_hover_color="#CBD5E1", text_color=TEXT_PRIMARY, corner_radius=10, height=38)
        self.opt_def_res.set(self.app.config_data.get("default_resolution", "Original"))
        self.opt_def_res.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(row1, text="Default Bitrate", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.opt_def_bitrate = ctk.CTkOptionMenu(row1, values=["2M", "5M", "8M", "12M", "20M"], fg_color="#F1F5F9", button_color="#E2E8F0", button_hover_color="#CBD5E1", text_color=TEXT_PRIMARY, corner_radius=10, height=38)
        self.opt_def_bitrate.set(self.app.config_data.get("default_bitrate", "5M"))
        self.opt_def_bitrate.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        self.chk_fallback = ctk.CTkCheckBox(card, text="Default to CPU fallback if NVENC unavailable", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY, checkbox_height=22, checkbox_width=22, corner_radius=6, fg_color=ACCENT_BLUE)
        if self.app.config_data.get("allow_cpu_fallback", True):
            self.chk_fallback.select()
        self.chk_fallback.pack(anchor="w", padx=22, pady=(0, 16))

        btn_save = ctk.CTkButton(
            card,
            text="💾  Save & Verify Connection Preferences",
            command=self._on_save_clicked,
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            corner_radius=12,
            height=42,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_save.pack(fill="x", padx=22, pady=(0, 20))

    def _build_watch_folder_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 20))

        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=22, pady=(18, 4))

        ic = ctk.CTkLabel(h_row, text="📁", font=ctk.CTkFont(size=16), fg_color="#D1FAE5", corner_radius=8, width=34, height=34)
        ic.pack(side="left", padx=(0, 12))

        t_box = ctk.CTkFrame(h_row, fg_color="transparent")
        t_box.pack(side="left", fill="both")
        ctk.CTkLabel(t_box, text="3rd-Party Editor Watch Folder (Auto-Offload)", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(t_box, text="Export directly from Premiere Pro, DaVinci Resolve, Blender, or HandBrake into this folder.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w")

        self.chk_watch_enabled = ctk.CTkCheckBox(card, text="Enable 3rd-Party Watch Folder Automation", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_PRIMARY, checkbox_height=22, checkbox_width=22, corner_radius=6, fg_color=ACCENT_BLUE)
        if self.app.config_data.get("watch_folder_enabled", False):
            self.chk_watch_enabled.select()
        self.chk_watch_enabled.pack(anchor="w", padx=22, pady=(14, 10))

        dir_row = ctk.CTkFrame(card, fg_color="transparent")
        dir_row.pack(fill="x", padx=22, pady=(0, 16))

        self.entry_watch_dir = ctk.CTkEntry(dir_row, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY)
        default_watch = str(Path.home() / "Videos" / "RenderWatch_In")
        self.entry_watch_dir.insert(0, str(self.app.config_data.get("watch_folder_path", default_watch)))
        self.entry_watch_dir.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_browse_watch = ctk.CTkButton(
            dir_row,
            text="Browse...",
            width=95,
            height=38,
            corner_radius=10,
            command=self._on_browse_watch_dir,
            fg_color="#E2E8F0",
            hover_color="#CBD5E1",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_browse_watch.pack(side="right")

    def _on_browse_watch_dir(self):
        chosen = filedialog.askdirectory(title="Select 3rd-Party Export Watch Folder")
        if chosen:
            self.entry_watch_dir.delete(0, "end")
            self.entry_watch_dir.insert(0, chosen)

    def _on_disconnect_clicked(self):
        self.app.disconnect_server()
        self._update_badge(False)
        messagebox.showinfo("Disconnected", "Server disconnected successfully. Client Studio is now in Offline mode.")

    def _on_reset_connection_clicked(self):
        self.entry_host.delete(0, "end")
        self.entry_host.insert(0, "127.0.0.1")
        self.entry_port.delete(0, "end")
        self.entry_port.insert(0, "8000")
        self.entry_token.delete(0, "end")
        self.app.disconnect_server()
        self._update_badge(False)
        messagebox.showinfo("Reset", "Host reset to 127.0.0.1:8000. Click 'Test & Connect' to verify.")

    def _on_test_handshake_clicked(self):
        host = self.entry_host.get().strip()
        port = self.entry_port.get().strip()
        token = self.entry_token.get().strip()

        if not host or not port:
            messagebox.showwarning("Validation", "Please provide worker IPv4 address and port.")
            return

        self.app._user_manually_disconnected = False
        self.btn_test.configure(state="disabled", text="Testing...")

        import threading
        def task():
            net = NetworkClient(host, port, token)
            res = net.ping_and_health()
            self.after(0, lambda: self._process_handshake(res, host, port, token))

        threading.Thread(target=task, daemon=True).start()

    def _process_handshake(self, res: dict, host: str, port: str, token: str):
        self.btn_test.configure(state="normal", text="🔄  Test & Connect")
        if res.get("success"):
            data = res.get("data", {})
            lat = res.get("latency_ms", 0)
            p_int = int(port) if str(port).isdigit() else 8000
            self.app.on_connection_success(host, p_int, token, lat, data)
            self._update_badge(True, host, port)
            messagebox.showinfo("Handshake Successful", f"Worker at {host}:{port} is online & reachable!\n\nRound-trip Latency: {lat} ms\nProtocol: {data.get('protocol_version')}")
        else:
            err = res.get("error", "Unknown connection failure")
            self.app.on_connection_failure(err)
            self._update_badge(False)
            messagebox.showerror("Handshake Failed", f"Could not connect to worker at {host}:{port}:\n\n{err}\n\nMake sure the worker server is running and the IP address is correct.")

    def _on_save_clicked(self):
        new_host = self.entry_host.get().strip()
        try:
            new_port = int(self.entry_port.get().strip())
        except ValueError:
            new_port = 8000
        new_token = self.entry_token.get().strip()

        self.app.config_data["server_host"] = new_host
        self.app.config_data["server_port"] = new_port
        self.app.config_data["api_token"] = new_token
        self.app.config_data["default_resolution"] = self.opt_def_res.get()
        self.app.config_data["default_bitrate"] = self.opt_def_bitrate.get()
        self.app.config_data["allow_cpu_fallback"] = bool(self.chk_fallback.get())
        self.app.config_data["watch_folder_enabled"] = bool(self.chk_watch_enabled.get())
        self.app.config_data["watch_folder_path"] = self.entry_watch_dir.get().strip()

        self.app.save_config()
        self.app.restart_watch_service()
        self.app._user_manually_disconnected = False

        # Real-time handshake check against saved host to ensure status reflects actual reality
        net = NetworkClient(new_host, new_port, new_token)
        res = net.ping_and_health()
        if res.get("success"):
            data = res.get("data", {})
            lat = res.get("latency_ms", 0)
            self.app.on_connection_success(new_host, new_port, new_token, lat, data)
            self._update_badge(True, new_host, new_port)
            messagebox.showinfo("Saved & Connected", f"Settings saved! Successfully verified connection with worker at {new_host}:{new_port} ({lat} ms).")
        else:
            err = res.get("error", "Host unreachable")
            self.app.on_connection_failure(err)
            self._update_badge(False)
            messagebox.showwarning(
                "Saved (Worker Offline)",
                f"Settings saved to client_settings.json.\n\nHowever, could NOT reach worker at {new_host}:{new_port}.\nConnection status is now OFFLINE.\n\nError: {err}"
            )
