import customtkinter as ctk

from client.ui.theme import *
from server.app.services.job_manager import job_manager

class RenderQueueView(ctk.CTkFrame):
    """
    High-Performance, Zero-Lag Render Queue View.
    Binds real-time jobs without dummy data and renders smoothly.
    """
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller
        self._rendered_rows = {}

        self._build_header_stats()
        self._build_table_container()
        self._refresh_queue()

    def _build_header_stats(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=4, pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_total = self._create_stat_card(grid, 0, "Total Jobs", "0", TEXT_PRIMARY, "📑")
        self.card_proc = self._create_stat_card(grid, 1, "Processing", "0", ACCENT_BLUE, "▶️")
        self.card_comp = self._create_stat_card(grid, 2, "Completed", "0", ACCENT_GREEN, "✅")
        self.card_failed = self._create_stat_card(grid, 3, "Failed", "0", ACCENT_RED, "❌")

    def _create_stat_card(self, parent, col, title, initial_val, color, icon):
        c = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        c.grid(row=0, column=col, sticky="nsew", padx=4)

        top = ctk.CTkFrame(c, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 2))
        ctk.CTkLabel(top, text=f"{icon}  {title}", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED).pack(side="left")

        lbl = ctk.CTkLabel(c, text=initial_val, font=ctk.CTkFont(size=22, weight="bold"), text_color=color)
        lbl.pack(anchor="w", padx=16, pady=(0, 12))
        return lbl

    def _build_table_container(self):
        self.table_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        self.table_card.pack(fill="both", expand=True, padx=4, pady=(0, 14))

        # Filter bar
        filter_bar = ctk.CTkFrame(self.table_card, fg_color="transparent")
        filter_bar.pack(fill="x", padx=18, pady=(16, 12))

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            placeholder_text="🔍 Search jobs by filename, client, or job ID...",
            height=36,
            corner_radius=8,
            border_color=BORDER_COLOR,
            fg_color=BG_INPUT
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.status_filter = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Status", "Completed", "Processing", "Queued", "Failed"],
            height=36,
            corner_radius=8,
            fg_color=BG_CARD_ALT,
            text_color=TEXT_PRIMARY,
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            command=lambda _: self._refresh_queue()
        )
        self.status_filter.pack(side="right")

        # Table Header
        t_header = ctk.CTkFrame(self.table_card, fg_color=BG_CARD_ALT, height=36, corner_radius=8)
        t_header.pack(fill="x", padx=18, pady=(0, 6))
        t_header.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        headers = ["#", "Filename", "Client IP", "Priority", "Status", "Progress", "ETA", "Actions"]
        for idx, h in enumerate(headers):
            ctk.CTkLabel(t_header, text=h, font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).grid(row=0, column=idx, padx=6, pady=8, sticky="w")

        self.rows_scroll = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent")
        self.rows_scroll.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        self.search_entry.bind("<KeyRelease>", lambda _: self._refresh_queue(reschedule=False))
        self._refresh_job = None
        self._refresh_queue()

    def on_page_shown(self):
        """Called immediately when user navigates to Render Queue tab."""
        self._refresh_queue(reschedule=False)

    def _refresh_queue(self, reschedule: bool = True):
        all_jobs = list(job_manager.jobs.values())
        tot = len(all_jobs)
        proc = sum(1 for j in all_jobs if j.status.value in ["rendering", "queued"])
        comp = sum(1 for j in all_jobs if j.status.value == "completed")
        failed = sum(1 for j in all_jobs if j.status.value in ["failed", "cancelled"])

        self.card_total.configure(text=str(tot))
        self.card_proc.configure(text=str(proc))
        self.card_comp.configure(text=str(comp))
        self.card_failed.configure(text=str(failed))

        # Filter by status and search query
        status_filter = self.status_filter.get().strip().lower()
        search_query = self.search_entry.get().strip().lower()

        filtered_jobs = []
        for j in all_jobs:
            st = j.status.value.lower()
            if status_filter != "all status":
                if status_filter == "processing" and st not in ["rendering", "queued"]:
                    continue
                elif status_filter == "completed" and st != "completed":
                    continue
                elif status_filter == "queued" and st != "queued":
                    continue
                elif status_filter == "failed" and st not in ["failed", "cancelled"]:
                    continue

            if search_query:
                fname = getattr(j, "input_filename", "").lower()
                jid = getattr(j, "job_id", "").lower()
                cip = getattr(j, "client_ip", "").lower()
                if search_query not in fname and search_query not in jid and search_query not in cip:
                    continue

            filtered_jobs.append(j)

        current_job_ids = [j.job_id for j in filtered_jobs]
        if getattr(self, "_last_ids", None) != current_job_ids:
            self._last_ids = current_job_ids
            for child in self.rows_scroll.winfo_children():
                child.destroy()
            self._rendered_rows.clear()

            if not filtered_jobs:
                empty_text = "No render jobs match the current filter." if all_jobs else "No render jobs currently in queue.\nWhen client submits jobs, they will appear here in real time."
                empty = ctk.CTkLabel(
                    self.rows_scroll,
                    text=empty_text,
                    font=ctk.CTkFont(size=12),
                    text_color=TEXT_MUTED
                )
                empty.pack(pady=40)
            else:
                for idx, j in enumerate(reversed(filtered_jobs), 1):
                    self._create_job_row(idx, j)
        else:
            # In-place updates without widget destruction
            for j in filtered_jobs:
                if j.job_id in self._rendered_rows:
                    bar, lbl_p, lbl_s, lbl_d = self._rendered_rows[j.job_id]
                    bar.set(j.progress_percent / 100.0)
                    lbl_p.configure(text=f" {j.progress_percent:.0f}%")
                    clr = ACCENT_GREEN if j.status.value == "completed" else (ACCENT_BLUE if j.status.value == "rendering" else ACCENT_RED)
                    bg = "#D1FAE5" if j.status.value == "completed" else ("#DBEAFE" if j.status.value == "rendering" else "#FEE2E2")
                    lbl_s.configure(text=f" {j.status.value.capitalize()} ", text_color=clr, fg_color=bg)
                    bar.configure(progress_color=clr)
                    dur = f"{j.elapsed_seconds:.0f}s" if j.elapsed_seconds else "--:--"
                    lbl_d.configure(text=dur)

        if reschedule:
            # High-speed refresh (500ms) when any job is actively rendering, 1500ms when idle
            delay = 500 if proc > 0 else 1500
            if self._refresh_job:
                try:
                    self.after_cancel(self._refresh_job)
                except Exception:
                    pass
            self._refresh_job = self.after(delay, self._refresh_queue)

    def _create_job_row(self, idx: int, j):
        row = ctk.CTkFrame(self.rows_scroll, fg_color=BG_CARD_ALT if idx % 2 == 0 else "#FFFFFF", corner_radius=6)
        row.pack(fill="x", pady=2)
        row.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        ctk.CTkLabel(row, text=str(idx), font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).grid(row=0, column=0, padx=6, pady=8, sticky="w")
        ctk.CTkLabel(row, text=j.input_filename[:24], font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_PRIMARY).grid(row=0, column=1, padx=6, pady=8, sticky="w")
        client_ip = getattr(j, "client_ip", "127.0.0.1")
        ctk.CTkLabel(row, text=client_ip, font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY).grid(row=0, column=2, padx=6, pady=8, sticky="w")
        ctk.CTkLabel(row, text="Normal", font=ctk.CTkFont(size=10, weight="bold"), text_color=ACCENT_BLUE).grid(row=0, column=3, padx=6, pady=8, sticky="w")

        clr = ACCENT_GREEN if j.status.value == "completed" else (ACCENT_BLUE if j.status.value == "rendering" else ACCENT_RED)
        bg = "#D1FAE5" if j.status.value == "completed" else ("#DBEAFE" if j.status.value == "rendering" else "#FEE2E2")
        s_badge = ctk.CTkLabel(row, text=f" {j.status.value.capitalize()} ", font=ctk.CTkFont(size=10, weight="bold"), text_color=clr, fg_color=bg, corner_radius=6)
        s_badge.grid(row=0, column=4, padx=6, pady=8, sticky="w")

        p_box = ctk.CTkFrame(row, fg_color="transparent")
        p_box.grid(row=0, column=5, padx=6, pady=4, sticky="ew")
        p_bar = ctk.CTkProgressBar(p_box, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=clr)
        p_bar.set(j.progress_percent / 100.0)
        p_bar.pack(side="left", fill="x", expand=True)
        lbl_pct = ctk.CTkLabel(p_box, text=f" {j.progress_percent:.0f}%", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED)
        lbl_pct.pack(side="left")

        dur = f"{j.elapsed_seconds:.0f}s" if j.elapsed_seconds else "--:--"
        lbl_dur = ctk.CTkLabel(row, text=dur, font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        lbl_dur.grid(row=0, column=6, padx=6, pady=8, sticky="w")

        def _cancel(jid=j.job_id):
            import asyncio
            import threading
            def _do():
                try:
                    for loop in [asyncio.get_event_loop()]:
                        if loop.is_running():
                            asyncio.run_coroutine_threadsafe(job_manager.cancel_job(jid), loop)
                            return
                except Exception:
                    pass
                try:
                    new_loop = asyncio.new_event_loop()
                    new_loop.run_until_complete(job_manager.cancel_job(jid))
                    new_loop.close()
                except Exception:
                    pass
            threading.Thread(target=_do, daemon=True).start()

        btn_act = ctk.CTkButton(
            row,
            text="✕" if j.status.value in ["rendering", "queued"] else "✓",
            font=ctk.CTkFont(size=10),
            fg_color=ACCENT_RED if j.status.value in ["rendering", "queued"] else "#94A3B8",
            height=22,
            width=28,
            corner_radius=4,
            command=_cancel if j.status.value in ["rendering", "queued"] else lambda: None
        )
        btn_act.grid(row=0, column=7, padx=6, pady=6, sticky="w")

        self._rendered_rows[j.job_id] = (p_bar, lbl_pct, s_badge, lbl_dur)
