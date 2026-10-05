"""
Modern Multi-Page Desktop Client Studio
Distributed Task Offloading & Remote GPU Rendering System
Features full Claymorphism Light aesthetic, tactile sidebar navigation,
real-time status header, and independent multi-page views.
"""

import sys
import threading
from pathlib import Path
from typing import Dict, Any, Optional

import customtkinter as ctk

# Explicit Light Theme Mode
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

from client.ui.theme import *
from client.ui.components.sidebar import SidebarNavigation
from client.ui.components.topbar import TopbarHeader
from client.ui.views.dashboard_view import DashboardView
from client.ui.views.render_job_view import RenderJobView
from client.ui.views.active_job_view import ActiveJobView
from client.ui.views.benchmarks_view import BenchmarksView
from client.ui.views.settings_view import SettingsView

from client.services.config_manager import config_manager
from client.services.network_client import NetworkClient

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GPU Render Stream Studio • Claymorphism Edition")
        self.geometry("1200x820")
        self.minsize(1060, 720)
        self.configure(fg_color=BG_MAIN)

        # Set application icon if exists
        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        # Load persisted settings
        self.config_data = config_manager.load()

        # Global system state
        self.is_connected = False
        self.gpu_ready = False
        self.health_data: Optional[Dict[str, Any]] = None

        # Build Master Layout
        self._init_layout()

        # Perform background handshake on startup
        self.after(300, self._startup_connection_check)

    def _init_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Left Sidebar Navigation
        self.sidebar = SidebarNavigation(self, on_navigate=self.navigate_to)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # 2. Topbar Status Header
        self.topbar = TopbarHeader(self, on_quick_connect=self._startup_connection_check)
        self.topbar.grid(row=0, column=1, sticky="ew")

        # 3. Main Page Host Container (Independent Views)
        self.page_container = ctk.CTkFrame(self, fg_color="transparent")
        self.page_container.grid(row=1, column=1, sticky="nsew", padx=22, pady=(16, 20))
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        # 4. Instantiate Multi-Page Views
        self.views = {
            "dashboard": DashboardView(self.page_container, self),
            "render_job": RenderJobView(self.page_container, self),
            "active_job": ActiveJobView(self.page_container, self),
            "benchmarks": BenchmarksView(self.page_container, self),
            "settings": SettingsView(self.page_container, self)
        }

        # Pack initial view
        self.current_view_widget = None
        self.navigate_to("dashboard")

    def navigate_to(self, page_name: str):
        if page_name not in self.views:
            return

        # Hide current active view widget if any
        if self.current_view_widget:
            self.current_view_widget.grid_forget()

        # Show target view widget cleanly
        target_view = self.views[page_name]
        target_view.grid(row=0, column=0, sticky="nsew")
        self.current_view_widget = target_view

        # Update topbar title
        titles = {
            "dashboard": "Dashboard Overview",
            "render_job": "Create New Remote Render Job",
            "active_job": "Live Job Telemetry & Logs",
            "benchmarks": "Performance & Benchmark Suite",
            "settings": "Host Connection & Settings"
        }
        self.topbar.set_title(titles.get(page_name, "Studio"))

        # Update sidebar active button styling
        for name, btn in self.sidebar.buttons.items():
            if name == page_name:
                btn.configure(fg_color=ACCENT_BLUE, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)

    def _startup_connection_check(self):
        host = self.config_data.get("server_host", "127.0.0.1")
        port = self.config_data.get("server_port", 8000)
        token = self.config_data.get("api_token", "")

        def task():
            net = NetworkClient(host, port, token)
            res = net.ping_and_health()
            self.after(0, lambda: self._process_handshake_result(res, host, port, token))

        threading.Thread(target=task, daemon=True).start()

    def _process_handshake_result(self, res: dict, host: str, port: int, token: str):
        if res.get("success"):
            lat = res.get("latency_ms", 0)
            data = res.get("data", {})
            self.on_connection_success(host, port, token, lat, data)
        else:
            self.on_connection_failure(res.get("error", "Offline"))

    def on_connection_success(self, host: str, port: int, token: str, latency: float, health_data: dict):
        self.is_connected = True
        self.health_data = health_data
        ff = health_data.get("ffmpeg", {})
        self.gpu_ready = ff.get("nvenc_available", False)
        proto = health_data.get("protocol_version", "v1.0.0")

        self.topbar.set_status(True, latency, proto)
        self.views["dashboard"].update_status(True, latency, health_data)

    def on_connection_failure(self, err_msg: str):
        self.is_connected = False
        self.health_data = None
        self.gpu_ready = False

        self.topbar.set_status(False)
        self.views["dashboard"].update_status(False)

    def start_render_job(self, params: Dict[str, Any]):
        # Switch to Active Job monitor page and trigger workflow
        self.navigate_to("active_job")
        threading.Thread(target=self.views["active_job"].run_render_flow, args=(params,), daemon=True).start()

    def save_config(self):
        config_manager.save(self.config_data)

if __name__ == "__main__":
    app = App()
    app.mainloop()

