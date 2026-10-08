import time
import socket
import customtkinter as ctk

from client.ui.theme import *
from server.ui.components.sparkline import MiniGraphCanvas
from server.app.config import settings
from server.app.services.system_service import SystemService
from server.app.services.connection_tracker import connection_tracker

class NetworkView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self.primary_ip = SystemService.get_primary_ip()
        self.all_ips = SystemService.get_all_lan_ips()
        self._last_bytes = 0
        self._last_time = time.time()
        self._refresh_timer = None

        self._build_top_network_cards()
        self._build_graphs_section()
        self._build_connections_table()
        self._build_firewall_card()

        self._refresh_network_status()

    def on_page_shown(self):
        """Called immediately when user navigates to Network tab."""
        self.primary_ip = SystemService.get_primary_ip()
        self.lbl_worker_ip.configure(text=self.primary_ip)
        self._refresh_network_status(reschedule=False)

    def _copy_ip_to_clipboard(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.primary_ip)
            self.btn_copy_ip.configure(text="✔ Copied!", fg_color=ACCENT_GREEN)
            self.after(2000, lambda: self.btn_copy_ip.configure(text="📋 Copy IP", fg_color=ACCENT_BLUE))
        except Exception:
            pass

    def _build_top_network_cards(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=4, pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1. Connection Daemon Status
        c1 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(c1, text="Daemon Service Status", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_daemon_status = ctk.CTkLabel(c1, text="Listening", font=ctk.CTkFont(size=16, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_daemon_status.pack(anchor="w", padx=16, pady=(0, 2))
        ctk.CTkLabel(c1, text="FastAPI / WebSocket Ready", font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(0, 14))

        # 2. Worker IP Address (Auto-detected LAN IP with Copy Button)
        c2 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c2.grid(row=0, column=1, sticky="nsew", padx=4)

        top2 = ctk.CTkFrame(c2, fg_color="transparent")
        top2.pack(fill="x", padx=16, pady=(14, 2))
        ctk.CTkLabel(top2, text="Detected Worker IP", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        self.btn_copy_ip = ctk.CTkButton(
            top2,
            text="📋 Copy IP",
            font=ctk.CTkFont(size=10, weight="bold"),
            width=70,
            height=22,
            corner_radius=6,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            command=self._copy_ip_to_clipboard
        )
        self.btn_copy_ip.pack(side="right")

        self.lbl_worker_ip = ctk.CTkLabel(c2, text=self.primary_ip, font=ctk.CTkFont(size=16, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_worker_ip.pack(anchor="w", padx=16, pady=(0, 2))
        ctk.CTkLabel(c2, text=f"Port: {settings.PORT} (TCP)", font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(0, 14))

        # 3. Active Clients (Live Dynamic Counter)
        c3 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c3.grid(row=0, column=2, sticky="nsew", padx=4)
        ctk.CTkLabel(c3, text="Active Client Sessions", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_active_clients = ctk.CTkLabel(c3, text="0 Clients", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_active_clients.pack(anchor="w", padx=16, pady=(0, 2))
        self.lbl_active_clients_sub = ctk.CTkLabel(c3, text="Awaiting client connection", font=ctk.CTkFont(size=10), text_color=TEXT_DIM)
        self.lbl_active_clients_sub.pack(anchor="w", padx=16, pady=(0, 14))

        # 4. Total Session Transfers (Live Bytes)
        c4 = ctk.CTkFrame(grid, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c4.grid(row=0, column=3, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(c4, text="Total Data Transferred", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_transfers_val = ctk.CTkLabel(c4, text="0.0 MB", font=ctk.CTkFont(size=16, weight="bold"), text_color=ACCENT_ORANGE)
        self.lbl_transfers_val.pack(anchor="w", padx=16, pady=(0, 2))
        ctk.CTkLabel(c4, text="Session total across network", font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(0, 14))

    def _build_graphs_section(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(0, 14))
        row.grid_columnconfigure((0, 1), weight=1)

        # Left Graph: Network Activity Wave
        c1 = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        top1 = ctk.CTkFrame(c1, fg_color="transparent")
        top1.pack(fill="x", padx=18, pady=(14, 2))
        ctk.CTkLabel(top1, text="Network Requests Rate", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(top1, text="Real-time daemon events", font=ctk.CTkFont(size=10), text_color=TEXT_DIM).pack(side="right")

        self.lbl_lat_val = ctk.CTkLabel(c1, text="Idle", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_PURPLE)
        self.lbl_lat_val.pack(anchor="w", padx=18, pady=(0, 6))

        self.graph_lat = MiniGraphCanvas(c1, width=320, height=80, bg_color=BG_CARD, primary_color=ACCENT_PURPLE)
        self.graph_lat.set_points([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.graph_lat.pack(fill="x", padx=14, pady=(0, 14))

        # Right Graph: Transfer Throughput Wave
        c2 = ctk.CTkFrame(row, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c2.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        top2 = ctk.CTkFrame(c2, fg_color="transparent")
        top2.pack(fill="x", padx=18, pady=(14, 2))
        ctk.CTkLabel(top2, text="Transfer Throughput", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        legend = ctk.CTkFrame(top2, fg_color="transparent")
        legend.pack(side="right")
        ctk.CTkLabel(legend, text="● LAN Traffic", font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT_GREEN).pack(side="left", padx=4)

        self.lbl_thr_val = ctk.CTkLabel(c2, text="0.0 KB/s", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_thr_val.pack(anchor="w", padx=18, pady=(0, 6))

        self.graph_thr = MiniGraphCanvas(c2, width=320, height=80, bg_color=BG_CARD, primary_color=ACCENT_GREEN)
        self.graph_thr.set_points([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.graph_thr.pack(fill="x", padx=14, pady=(0, 14))

    def _build_connections_table(self):
        self.table_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.table_card.pack(fill="x", padx=4, pady=(0, 14))

        top = ctk.CTkFrame(self.table_card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 8))
        ctk.CTkLabel(top, text="Live Client Connections", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")

        btn_clear = ctk.CTkButton(
            top,
            text="🗑️ Clear History",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            width=110,
            fg_color="#F1F5F9",
            text_color=TEXT_SECONDARY,
            hover_color="#E2E8F0",
            corner_radius=8,
            command=self._clear_connections_history
        )
        btn_clear.pack(side="right")

        # Table Header
        h = ctk.CTkFrame(self.table_card, fg_color=BG_CARD_ALT, height=32, corner_radius=6)
        h.pack(fill="x", padx=18, pady=(0, 6))
        h.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(h, text="#", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(h, text="Client IPv4", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=1, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(h, text="Port", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(h, text="Live Status", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=3, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(h, text="Last Activity", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkLabel(h, text="Transferred", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        # Container for dynamic rows
        self.rows_container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.rows_container.pack(fill="x", padx=18, pady=(0, 14))

    def _clear_connections_history(self):
        connection_tracker.clear()
        self._render_connection_rows([])

    def _render_connection_rows(self, connections):
        for widget in self.rows_container.winfo_children():
            widget.destroy()

        if not connections:
            empty_box = ctk.CTkFrame(self.rows_container, fg_color=BG_CARD_ALT, corner_radius=10)
            empty_box.pack(fill="x", pady=6)
            ctk.CTkLabel(
                empty_box,
                text=f"ℹ️ No client devices connected yet. To connect, open Client Studio and set Worker Host to: {self.primary_ip}:{settings.PORT}",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED,
                pady=16
            ).pack()
            return

        now = time.time()
        for idx, conn in enumerate(connections, start=1):
            is_active = conn.get("is_active", False)
            bg_col = "#FFFFFF" if idx % 2 != 0 else BG_CARD_ALT
            row = ctk.CTkFrame(self.rows_container, fg_color=bg_col, corner_radius=6)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            # #
            ctk.CTkLabel(row, text=str(idx), font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).grid(row=0, column=0, padx=6, pady=6, sticky="w")

            # IP
            ctk.CTkLabel(row, text=str(conn["ip"]), font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY).grid(row=0, column=1, padx=6, pady=6, sticky="w")

            # Port
            port_str = str(conn.get("port", "--"))
            ctk.CTkLabel(row, text=port_str, font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).grid(row=0, column=2, padx=6, pady=6, sticky="w")

            # Status pill
            if is_active:
                st_text = "Active"
                st_color = ACCENT_GREEN
                st_bg = "#D1FAE5"
            else:
                st_text = "Idle / History"
                st_color = TEXT_MUTED
                st_bg = "#F1F5F9"

            ctk.CTkLabel(row, text=st_text, font=ctk.CTkFont(size=10, weight="bold"), text_color=st_color, fg_color=st_bg, corner_radius=6, padx=8, pady=2).grid(row=0, column=3, padx=6, pady=6, sticky="w")

            # Last seen
            diff = int(now - conn["last_seen"])
            if diff < 5:
                time_txt = "Just now"
            elif diff < 60:
                time_txt = f"{diff}s ago"
            else:
                time_txt = time.strftime("%H:%M:%S", time.localtime(conn["last_seen"]))
            ctk.CTkLabel(row, text=time_txt, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).grid(row=0, column=4, padx=6, pady=6, sticky="w")

            # Transferred
            b = conn.get("bytes_transferred", 0)
            if b >= 1024 * 1024:
                b_txt = f"{b / (1024 * 1024):.1f} MB"
            elif b >= 1024:
                b_txt = f"{b / 1024:.1f} KB"
            else:
                b_txt = f"{b} B"
            ctk.CTkLabel(row, text=b_txt, font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).grid(row=0, column=5, padx=6, pady=6, sticky="w")

    def _build_firewall_card(self):
        c = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        c.pack(fill="x", padx=4, pady=(0, 14))

        box = ctk.CTkFrame(c, fg_color="transparent")
        box.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(box, text="🔒  Firewall & Port Status", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")

        f_row = ctk.CTkFrame(box, fg_color="transparent")
        f_row.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(f_row, text=f"● Port {settings.PORT} (TCP): Open & Listening", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_GREEN).pack(side="left", padx=(0, 20))
        ctk.CTkLabel(f_row, text="● Network Interface: Active", font=ctk.CTkFont(size=12, weight="bold"), text_color=ACCENT_GREEN).pack(side="left")

    def _refresh_network_status(self, reschedule: bool = True):
        try:
            if not self.winfo_exists():
                return

            tot_bytes = connection_tracker.get_total_transferred_bytes()
            conns = connection_tracker.get_connections_list()
            active_cnt = sum(1 for c in conns if c.get("is_active", False))
            now = time.time()
            dt = max(now - self._last_time, 0.1)

            # Compute real speed
            speed_kb = 0.0
            if self._last_bytes > 0 and tot_bytes >= self._last_bytes:
                speed_kb = (tot_bytes - self._last_bytes) / 1024.0 / dt
            self._last_bytes = tot_bytes
            self._last_time = now

            # 1. Update active clients card & activity graph
            if active_cnt > 0:
                self.lbl_active_clients.configure(text=f"{active_cnt} Client{'s' if active_cnt > 1 else ''}", text_color=ACCENT_GREEN)
                self.lbl_active_clients_sub.configure(text="Communicating with daemon")
                self.lbl_lat_val.configure(text=f"{active_cnt} Active Stream{'s' if active_cnt > 1 else ''}", text_color=ACCENT_GREEN)
                self.graph_lat.add_point(min(100.0, active_cnt * 25.0))
            else:
                self.lbl_active_clients.configure(text="0 Clients", text_color=TEXT_PRIMARY)
                self.lbl_active_clients_sub.configure(text="Awaiting client connection")
                self.lbl_lat_val.configure(text="Idle (Listening)", text_color=TEXT_MUTED)
                self.graph_lat.add_point(0.0)

            # 2. Update throughput & graph
            if speed_kb >= 1024:
                self.lbl_thr_val.configure(text=f"{speed_kb / 1024.0:.1f} MB/s")
            else:
                self.lbl_thr_val.configure(text=f"{speed_kb:.1f} KB/s")
            self.graph_thr.add_point(min(100.0, speed_kb / 10.0))

            # 3. Update total transfers card
            if tot_bytes >= 1024 * 1024 * 1024:
                self.lbl_transfers_val.configure(text=f"{tot_bytes / (1024**3):.2f} GB")
            elif tot_bytes >= 1024 * 1024:
                self.lbl_transfers_val.configure(text=f"{tot_bytes / (1024**2):.1f} MB")
            elif tot_bytes >= 1024:
                self.lbl_transfers_val.configure(text=f"{tot_bytes / 1024:.0f} KB")
            else:
                self.lbl_transfers_val.configure(text=f"{tot_bytes} B")

            # 4. Render connections table
            self._render_connection_rows(conns)

        except Exception:
            pass

        if reschedule:
            # 1000ms if active clients or transfers, 2500ms if idle
            delay = 1000 if (active_cnt > 0 or speed_kb > 0) else 2500
            if self._refresh_timer:
                try:
                    self.after_cancel(self._refresh_timer)
                except Exception:
                    pass
            self._refresh_timer = self.after(delay, self._refresh_network_status)
