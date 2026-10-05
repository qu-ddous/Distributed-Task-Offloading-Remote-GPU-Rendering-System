import time
import threading
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

from client.ui.theme import *
from client.services.network_client import NetworkClient

class BenchmarksView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._build_header_card()
        self._build_comparison_tool()
        self._build_formula_guide()

    def _build_header_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(fill="x", padx=24, pady=20)

        badge = ctk.CTkLabel(
            box,
            text="BENCHMARK LAB",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#FFFFFF",
            fg_color=ACCENT_ORANGE,
            corner_radius=6,
            padx=8,
            pady=2
        )
        badge.pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            box,
            text="GPU Speedup & Overhead Calculator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            box,
            text="Compare Local Laptop CPU rendering versus Remote NVIDIA NVENC offloading with exact mathematical formulas.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

    def _build_comparison_tool(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        ctk.CTkLabel(card, text="Speedup Measurement Calculator", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(18, 12))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=(0, 18))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Inputs
        ctk.CTkLabel(grid, text="Local CPU Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.entry_local_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=36)
        self.entry_local_t.insert(0, "180.0")
        self.entry_local_t.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(grid, text="Upload Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.entry_up_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=36)
        self.entry_up_t.insert(0, "4.2")
        self.entry_up_t.grid(row=1, column=1, sticky="ew", padx=6)

        ctk.CTkLabel(grid, text="Remote GPU Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=2, sticky="w", pady=(0, 4))
        self.entry_render_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=36)
        self.entry_render_t.insert(0, "18.5")
        self.entry_render_t.grid(row=1, column=2, sticky="ew", padx=6)

        ctk.CTkLabel(grid, text="Download Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=3, sticky="w", pady=(0, 4))
        self.entry_dl_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=36)
        self.entry_dl_t.insert(0, "1.1")
        self.entry_dl_t.grid(row=1, column=3, sticky="ew", padx=(6, 0))

        # Calculate Button
        btn_calc = ctk.CTkButton(
            card,
            text="⚡  Compute Speedup & Network Overhead",
            command=self._on_compute_clicked,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            corner_radius=10,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn_calc.pack(anchor="w", padx=24, pady=(0, 16))

        # Results Display Card inside
        self.res_box = ctk.CTkFrame(card, fg_color=BG_CARD_ALT, corner_radius=14)
        self.res_box.pack(fill="x", padx=24, pady=(0, 20))

        self.lbl_speedup = ctk.CTkLabel(self.res_box, text="Speedup Factor: --", font=ctk.CTkFont(size=18, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_speedup.pack(anchor="w", padx=18, pady=(14, 4))

        self.lbl_details = ctk.CTkLabel(self.res_box, text="Enter timing measurements above to evaluate offloading performance.", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_details.pack(anchor="w", padx=18, pady=(0, 14))

    def _build_formula_guide(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkLabel(card, text="Evaluation Principles & Equations", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=24, pady=(18, 10))

        f1 = "• Remote Total Time = T_upload + T_remote_render + T_download"
        f2 = "• Speedup Factor = T_local_render / Remote Total Time"
        f3 = "• Network Overhead Ratio = (T_upload + T_download) / Remote Total Time * 100%"

        for text in [f1, f2, f3]:
            ctk.CTkLabel(card, text=text, font=ctk.CTkFont(family="Consolas", size=12), text_color=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=3)

        ctk.CTkLabel(
            card,
            text="Note: Very short clips (<10s) may see Speedup < 1.0x due to network transfer overhead.\nLonger and higher-resolution videos (1080p/4K) typically achieve 3x to 10x net speedup.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(anchor="w", padx=24, pady=(10, 20))

    def _on_compute_clicked(self):
        try:
            t_loc = float(self.entry_local_t.get())
            t_up = float(self.entry_up_t.get())
            t_rend = float(self.entry_render_t.get())
            t_dl = float(self.entry_dl_t.get())

            t_rem_total = t_up + t_rend + t_dl
            if t_rem_total <= 0:
                return

            speedup = t_loc / t_rem_total
            overhead = t_up + t_dl
            overhead_pct = (overhead / t_rem_total) * 100.0

            color = ACCENT_GREEN if speedup >= 1.0 else ACCENT_RED
            self.lbl_speedup.configure(text=f"Speedup Factor: {speedup:.2f}x ({'Faster' if speedup >= 1.0 else 'Slower'} than Local)", text_color=color)

            msg = (
                f"Remote Total Time: {t_rem_total:.2f}s (vs Local: {t_loc:.2f}s)\n"
                f"Network Overhead: {overhead:.2f}s ({overhead_pct:.1f}% of total job duration)\n"
                f"Net Time Saved: {t_loc - t_rem_total:.2f} seconds"
            )
            self.lbl_details.configure(text=msg)
        except ValueError:
            messagebox.showwarning("Validation", "Please enter valid numeric time values.")

