import sys
import threading
from pathlib import Path
import customtkinter as ctk

# Explicit Light Mode Theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

from client.ui.theme import *
from server.ui.components.sidebar import ServerSidebar
from server.ui.components.topbar import ServerTopbar
from server.ui.components.smooth_scroll import enable_fast_smooth_scroll

from server.ui.views.overview_view import ServerOverviewView
from server.ui.views.render_queue_view import RenderQueueView
from server.ui.views.activity_logs_view import ActivityLogsView
from server.ui.views.gpu_engine_view import GPUEngineView
from server.ui.views.network_view import NetworkView
from server.ui.views.settings_view import ServerSettingsView

class ServerApp(ctk.CTk):
    def __init__(self, uvicorn_server_instance=None):
        super().__init__()

        self.title("GPU Render Stream Studio • Worker Server (v1.0.0)")
        self.geometry("1240x840")
        self.minsize(1080, 720)
        self.configure(fg_color=BG_MAIN)

        self.uvicorn_server = uvicorn_server_instance
        self.is_server_active = True

        # Set application icon if exists
        icon_path = Path(__file__).resolve().parent.parent.parent / "client" / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        self._init_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Sidebar Navigation
        self.sidebar = ServerSidebar(self, on_navigate=self.navigate_to)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # 2. Topbar Status Header
        self.topbar = ServerTopbar(self, on_toggle_server=self.toggle_server_state)
        self.topbar.grid(row=0, column=1, sticky="ew")

        # 3. Main Page Host Container
        self.page_container = ctk.CTkFrame(self, fg_color="transparent")
        self.page_container.grid(row=1, column=1, sticky="nsew", padx=22, pady=(16, 20))
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        # 4. Multi-Page Views (Cached Notebook Stack pattern)
        self.views = {
            "overview": ServerOverviewView(self.page_container, self),
            "render_queue": RenderQueueView(self.page_container, self),
            "activity_logs": ActivityLogsView(self.page_container, self),
            "gpu_engine": GPUEngineView(self.page_container, self),
            "network": NetworkView(self.page_container, self),
            "settings": ServerSettingsView(self.page_container, self)
        }

        # Enable smooth scroll on scrollable frames
        for view in self.views.values():
            if isinstance(view, ctk.CTkScrollableFrame):
                enable_fast_smooth_scroll(view, scroll_factor=2)

        self.current_view_widget = None
        self.navigate_to("overview")

    def navigate_to(self, page_name: str):
        if page_name not in self.views:
            return

        target_view = self.views[page_name]
        if self.current_view_widget == target_view:
            return

        # Un-grid previous view completely to prevent canvas overlap and restore 100% exact layout gaps
        if self.current_view_widget:
            self.current_view_widget.grid_forget()

        # Display target view cleanly
        target_view.grid(row=0, column=0, sticky="nsew")
        self.current_view_widget = target_view

        # Immediately refresh target view to avoid blank or stale state
        if hasattr(target_view, "on_page_shown"):
            try:
                target_view.on_page_shown()
            except Exception:
                pass

        headers = {
            "overview": ("GPU Worker Server", "Dedicated NVIDIA GPU render node for remote video processing"),
            "render_queue": ("Render Queue", "Manage and monitor all render jobs in the queue"),
            "activity_logs": ("Activity Logs", "Detailed event logs from the worker server"),
            "gpu_engine": ("GPU & Engine", "GPU hardware status and video encoding capabilities"),
            "network": ("Network", "Network connection status and client communication"),
            "settings": ("Settings", "Configure worker server behavior and preferences")
        }
        title, sub = headers.get(page_name, ("Worker Server", "Node"))
        self.topbar.set_header_text(title, sub)

        for name, btn in self.sidebar.buttons.items():
            if name == page_name:
                btn.configure(fg_color=ACCENT_BLUE, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)

    def toggle_server_state(self):
        from server.app.server_state import server_state
        self.is_server_active = not self.is_server_active
        server_state.is_active = self.is_server_active
        self.topbar.set_server_running_state(self.is_server_active)
        if self.is_server_active:
            self.sidebar.lbl_server_status_dot.configure(text="● Running", text_color=ACCENT_GREEN)
        else:
            self.sidebar.lbl_server_status_dot.configure(text="● Stopped", text_color=ACCENT_RED)

    def _on_close(self):
        if self.uvicorn_server:
            self.uvicorn_server.should_exit = True
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = ServerApp()
    app.mainloop()

