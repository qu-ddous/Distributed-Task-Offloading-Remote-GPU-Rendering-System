import customtkinter as ctk

from client.ui.theme import *
from server.ui.log_bus import server_log_bus

class ActivityLogsView(ctk.CTkFrame):
    """
    High-Performance, Zero-Lag Activity Logs View.
    Uses native Tkinter text-tag rendering instead of generating 40+ CTkFrames per second,
    eliminating all scroll-lag while delivering rich badges, search highlights, and real-time event counters.
    """
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self.current_filter = "ALL"
        self._last_log_count = 0

        self._build_filter_bar()
        self._build_logs_console()
        self._refresh_logs()

    def _build_filter_bar(self):
        filter_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        filter_card.pack(fill="x", padx=4, pady=(0, 14))

        top = ctk.CTkFrame(filter_card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=12)

        # Filter Pills with dynamic counters
        self.btn_all = self._create_filter_btn(top, "All (0)", "ALL", ACCENT_BLUE)
        self.btn_info = self._create_filter_btn(top, "Info (0)", "INFO", ACCENT_CYAN)
        self.btn_succ = self._create_filter_btn(top, "Success (0)", "SUCCESS", ACCENT_GREEN)
        self.btn_warn = self._create_filter_btn(top, "Warning (0)", "WARNING", ACCENT_ORANGE)
        self.btn_err = self._create_filter_btn(top, "Error (0)", "ERROR", ACCENT_RED)

        # Clear logs button
        btn_clear = ctk.CTkButton(
            top,
            text="🗑️ Clear",
            font=ctk.CTkFont(size=11),
            height=32,
            width=70,
            fg_color="#F1F5F9",
            text_color=TEXT_SECONDARY,
            hover_color="#E2E8F0",
            corner_radius=8,
            command=self._clear_logs
        )
        btn_clear.pack(side="right", padx=(8, 0))

        # Search box
        self.search_entry = ctk.CTkEntry(
            top,
            placeholder_text="🔍 Search log messages...",
            height=32,
            width=240,
            corner_radius=8,
            border_color=BORDER_COLOR,
            fg_color=BG_INPUT
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda _: self._render_all_logs())

    def _create_filter_btn(self, parent, label, filter_id, color):
        btn = ctk.CTkButton(
            parent,
            text=label,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
            width=92,
            corner_radius=8,
            fg_color=color if filter_id == self.current_filter else BG_CARD_ALT,
            text_color="#FFFFFF" if filter_id == self.current_filter else TEXT_SECONDARY,
            hover_color=color,
            command=lambda: self._set_filter(filter_id)
        )
        btn.pack(side="left", padx=(0, 6))
        return btn

    def _set_filter(self, filter_id):
        self.current_filter = filter_id
        for fid, btn, col in [("ALL", self.btn_all, ACCENT_BLUE), ("INFO", self.btn_info, ACCENT_CYAN), ("SUCCESS", self.btn_succ, ACCENT_GREEN), ("WARNING", self.btn_warn, ACCENT_ORANGE), ("ERROR", self.btn_err, ACCENT_RED)]:
            if fid == self.current_filter:
                btn.configure(fg_color=col, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=BG_CARD_ALT, text_color=TEXT_SECONDARY)
        self._render_all_logs()

    def _build_logs_console(self):
        self.logs_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.logs_card.pack(fill="both", expand=True, padx=4, pady=(0, 14))

        # Header Bar
        t_header = ctk.CTkFrame(self.logs_card, fg_color=BG_CARD_ALT, height=36, corner_radius=8)
        t_header.pack(fill="x", padx=16, pady=(14, 8))
        t_header.grid_columnconfigure(0, weight=1)
        t_header.grid_columnconfigure(1, weight=1)
        t_header.grid_columnconfigure(2, weight=8)

        ctk.CTkLabel(t_header, text="Time", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        ctk.CTkLabel(t_header, text="Level", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=1, padx=12, pady=8, sticky="w")
        ctk.CTkLabel(t_header, text="Event Message / Details", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=2, padx=12, pady=8, sticky="w")

        # Smooth Textbox for Zero-Lag 60 FPS scrolling
        self.txt_logs = ctk.CTkTextbox(
            self.logs_card,
            fg_color="#FFFFFF",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=10,
            border_width=0,
            wrap="word"
        )
        self.txt_logs.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Setup Rich Color Tags for instant rendering (CTkTextbox forbids 'font' in tag_config)
        self.txt_logs.tag_config("time", foreground=TEXT_MUTED)
        self.txt_logs.tag_config("info_tag", foreground="#2563EB", background="#DBEAFE")
        self.txt_logs.tag_config("succ_tag", foreground="#059669", background="#D1FAE5")
        self.txt_logs.tag_config("warn_tag", foreground="#D97706", background="#FEF3C7")
        self.txt_logs.tag_config("err_tag", foreground="#DC2626", background="#FEE2E2")
        self.txt_logs.tag_config("msg", foreground=TEXT_PRIMARY)
        self.txt_logs.tag_config("highlight", background="#FEF08A")

    def _clear_logs(self):
        server_log_bus.logs.clear()
        self._render_all_logs()

    def on_page_shown(self):
        """Called immediately when user navigates to Activity Logs tab."""
        self._refresh_logs(reschedule=False)

    def _refresh_logs(self, reschedule: bool = True):
        logs = list(server_log_bus.logs)
        # Update category count badges
        total = len(logs)
        info_c = sum(1 for l in logs if l["level"] == "INFO" and "success" not in l["message"].lower() and "completed" not in l["message"].lower())
        succ_c = sum(1 for l in logs if l["level"] == "SUCCESS" or "success" in l["message"].lower() or "completed" in l["message"].lower())
        warn_c = sum(1 for l in logs if l["level"] == "WARNING")
        err_c = sum(1 for l in logs if l["level"] == "ERROR")

        self.btn_all.configure(text=f"All ({total})")
        self.btn_info.configure(text=f"Info ({info_c})")
        self.btn_succ.configure(text=f"Success ({succ_c})")
        self.btn_warn.configure(text=f"Warning ({warn_c})")
        self.btn_err.configure(text=f"Error ({err_c})")

        if total != self._last_log_count:
            self._last_log_count = total
            self._render_all_logs()

        if reschedule:
            self.after(1500, self._refresh_logs)

    def _render_all_logs(self):
        logs = list(server_log_bus.logs)
        query = self.search_entry.get().strip().lower()

        self.txt_logs.configure(state="normal")
        self.txt_logs.delete("1.0", "end")

        if not logs:
            self.txt_logs.insert("end", "\n   Awaiting live worker server activity events...\n", "time")
            self.txt_logs.configure(state="disabled")
            return

        for item in reversed(logs):
            lvl = item["level"]
            msg = item["message"]
            is_succ = lvl == "SUCCESS" or "success" in msg.lower() or "completed" in msg.lower()

            # Filter logic
            if self.current_filter != "ALL":
                if self.current_filter == "SUCCESS" and not is_succ:
                    continue
                elif self.current_filter == "INFO" and (is_succ or lvl != "INFO"):
                    continue
                elif self.current_filter == "WARNING" and lvl != "WARNING":
                    continue
                elif self.current_filter == "ERROR" and lvl != "ERROR":
                    continue

            # Query filter
            if query and query not in msg.lower() and query not in item["time"].lower():
                continue

            # Insert Time
            self.txt_logs.insert("end", f" {item['time']}   ", "time")

            # Insert Badge
            if is_succ:
                self.txt_logs.insert("end", " SUCCESS ", "succ_tag")
            elif lvl == "INFO":
                self.txt_logs.insert("end", "  INFO   ", "info_tag")
            elif lvl == "WARNING":
                self.txt_logs.insert("end", " WARNING ", "warn_tag")
            else:
                self.txt_logs.insert("end", "  ERROR  ", "err_tag")

            # Insert Message
            self.txt_logs.insert("end", f"   {msg}\n\n", "msg")

        self.txt_logs.configure(state="disabled")
