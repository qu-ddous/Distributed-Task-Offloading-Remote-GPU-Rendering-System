import threading
from tkinter import messagebox
import customtkinter as ctk

from client.ui.theme import *
from client.services.network_client import NetworkClient

class SettingsView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_connection_card()
        self._build_defaults_card()
        self._build_save_button()

    def _build_connection_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        ctk.CTkLabel(card, text="Remote Worker Host Connection", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=22, pady=(18, 4))
        ctk.CTkLabel(card, text="Specify the GPU worker's LAN IP address, port, and security token.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=22, pady=(0, 16))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=(0, 18))
        grid.grid_columnconfigure(0, weight=3)
        grid.grid_columnconfigure(1, weight=1)

        # Worker Host IP
        ctk.CTkLabel(grid, text="Worker IPv4 Address", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.entry_host = ctk.CTkEntry(grid, placeholder_text="192.168.1.150", fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=36, text_color=TEXT_PRIMARY)
        self.entry_host.insert(0, str(self.app.config_data.get("server_host", "127.0.0.1")))
        self.entry_host.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 14))

        # Port
        ctk.CTkLabel(grid, text="Port", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.entry_port = ctk.CTkEntry(grid, placeholder_text="8000", fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=36, text_color=TEXT_PRIMARY)
        self.entry_port.insert(0, str(self.app.config_data.get("server_port", 8000)))
        self.entry_port.grid(row=1, column=1, sticky="ew", pady=(0, 14))

        # API Token
        ctk.CTkLabel(grid, text="Shared API Secret Token (X-API-Token)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.entry_token = ctk.CTkEntry(grid, show="•", placeholder_text="Enter secret token matching worker .env", fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=36, text_color=TEXT_PRIMARY)
        self.entry_token.insert(0, str(self.app.config_data.get("api_token", "")))
        self.entry_token.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # Test Handshake button
        self.btn_test = ctk.CTkButton(
            card,
            text="🔄  Test Handshake & Capabilities",
            command=self._on_test_handshake_clicked,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            corner_radius=10,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_test.pack(anchor="w", padx=22, pady=(0, 20))

    def _build_defaults_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        ctk.CTkLabel(card, text="Default Render Preferences", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=22, pady=(18, 4))
        ctk.CTkLabel(card, text="Set preferred resolution and fallback settings for new render tasks.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(anchor="w", padx=22, pady=(0, 16))

        row1 = ctk.CTkFrame(card, fg_color="transparent")
        row1.pack(fill="x", padx=22, pady=(0, 14))
        row1.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(row1, text="Default Resolution", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.opt_def_res = ctk.CTkOptionMenu(row1, values=["Original", "720p", "1080p", "1440p", "4K"], fg_color="#F1F5F9", button_color="#E2E8F0", button_hover_color="#CBD5E1", text_color=TEXT_PRIMARY, corner_radius=10, height=36)
        self.opt_def_res.set(self.app.config_data.get("default_resolution", "1080p"))
        self.opt_def_res.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(row1, text="Default Bitrate", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.opt_def_bitrate = ctk.CTkOptionMenu(row1, values=["2M", "5M", "8M", "12M", "20M"], fg_color="#F1F5F9", button_color="#E2E8F0", button_hover_color="#CBD5E1", text_color=TEXT_PRIMARY, corner_radius=10, height=36)
        self.opt_def_bitrate.set(self.app.config_data.get("default_bitrate", "5M"))
        self.opt_def_bitrate.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        self.chk_fallback = ctk.CTkCheckBox(card, text="Default to CPU fallback if NVENC unavailable", font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY, checkbox_height=22, checkbox_width=22, corner_radius=6, fg_color=ACCENT_BLUE)
        if self.app.config_data.get("allow_cpu_fallback", False):
            self.chk_fallback.select()
        self.chk_fallback.pack(anchor="w", padx=22, pady=(10, 20))

    def _build_save_button(self):
        btn_save = ctk.CTkButton(
            self,
            text="💾  Save Application Preferences",
            command=self._on_save_clicked,
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            corner_radius=14,
            height=46,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_save.pack(fill="x", padx=10, pady=(0, 20))

    def _on_test_handshake_clicked(self):
        host = self.entry_host.get().strip()
        port = self.entry_port.get().strip()
        token = self.entry_token.get().strip()

        if not host or not port:
            messagebox.showwarning("Validation", "Please provide worker IPv4 address and port.")
            return

        self.btn_test.configure(state="disabled", text="Testing Handshake...")

        def task():
            net = NetworkClient(host, port, token)
            res = net.ping_and_health()
            self.after(0, lambda: self._process_handshake(res, host, port, token))

        threading.Thread(target=task, daemon=True).start()

    def _process_handshake(self, res: dict, host: str, port: str, token: str):
        self.btn_test.configure(state="normal", text="🔄  Test Handshake & Capabilities")
        if res.get("success"):
            data = res.get("data", {})
            lat = res.get("latency_ms", 0)
            self.app.on_connection_success(host, int(port), token, lat, data)
            messagebox.showinfo("Handshake Successful", f"Worker at {host}:{port} is reachable!\nRound-trip Latency: {lat} ms\nProtocol: {data.get('protocol_version')}")
        else:
            err = res.get("error", "Unknown connection failure")
            self.app.on_connection_failure(err)
            messagebox.showerror("Handshake Failed", f"Could not reach worker at {host}:{port}:\n\n{err}")

    def _on_save_clicked(self):
        self.app.config_data["server_host"] = self.entry_host.get().strip()
        try:
            self.app.config_data["server_port"] = int(self.entry_port.get().strip())
        except ValueError:
            self.app.config_data["server_port"] = 8000
        self.app.config_data["api_token"] = self.entry_token.get().strip()
        self.app.config_data["default_resolution"] = self.opt_def_res.get()
        self.app.config_data["default_bitrate"] = self.opt_def_bitrate.get()
        self.app.config_data["allow_cpu_fallback"] = bool(self.chk_fallback.get())

        self.app.save_config()
        messagebox.showinfo("Saved", "Settings successfully saved to client_settings.json.")

