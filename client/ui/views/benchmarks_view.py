import os
import sys
import time
import shutil
import tempfile
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from tkinter import messagebox
import customtkinter as ctk

from client.ui.theme import *
from client.ui.components.sparkline import BenchmarkBarCanvas
from client.services.network_client import NetworkClient

class BenchmarksView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self._bench_running = False

        self._build_header_card()
        self._build_live_benchmark_card()
        self._build_recent_job_card()
        self._build_calculator_card()
        self._build_formula_guide()

    def on_page_shown(self):
        """Called whenever the user navigates to the Benchmarks view."""
        self._refresh_recent_job_card()

    def _build_header_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(fill="x", padx=26, pady=20)
        box.grid_columnconfigure(0, weight=1)
        box.grid_columnconfigure(1, weight=0)

        left_b = ctk.CTkFrame(box, fg_color="transparent")
        left_b.grid(row=0, column=0, sticky="w")

        badge = ctk.CTkLabel(
            left_b,
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
            left_b,
            text="Hardware Performance & Speedup Suite",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_b,
            text="Measure real-time Local Laptop CPU rendering versus Remote NVIDIA NVENC offloading with exact mathematical formulas.",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(2, 0))

        # Right Bar Illustration
        right_b = ctk.CTkFrame(box, fg_color="transparent")
        right_b.grid(row=0, column=1, sticky="e", padx=(14, 0))
        self.hdr_chart = BenchmarkBarCanvas(right_b, width=170, height=65)
        self.hdr_chart.pack()

    def _build_live_benchmark_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=24, pady=(18, 8))

        ic = ctk.CTkLabel(h_row, text="⚡", font=ctk.CTkFont(size=15), fg_color="#FEF3C7", corner_radius=8, width=32, height=32)
        ic.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            h_row,
            text="Live Hardware Benchmark Suite (Automated)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        desc = (
            "Runs a standardized automated comparison: Generates a 1080p test payload, measures your Local Laptop's CPU transcode "
            "(libx264), offloads to the Remote Server over LAN wire (h264_nvenc), and calculates exact speedup."
        )
        ctk.CTkLabel(
            card,
            text=desc,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=700
        ).pack(anchor="w", padx=24, pady=(0, 14))

        # Action bar
        act_row = ctk.CTkFrame(card, fg_color="transparent")
        act_row.pack(fill="x", padx=24, pady=(0, 12))

        self.btn_run_bench = ctk.CTkButton(
            act_row,
            text="▶  Run Live Hardware Benchmark",
            command=self._start_live_benchmark,
            fg_color=ACCENT_ORANGE,
            hover_color="#D97706",
            corner_radius=10,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_run_bench.pack(side="left", padx=(0, 14))

        self.lbl_bench_status = ctk.CTkLabel(
            act_row,
            text="● Idle - Ready for live benchmark",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_MUTED
        )
        self.lbl_bench_status.pack(side="left")

        # Progress bar
        self.bench_prog = ctk.CTkProgressBar(card, height=8, corner_radius=4, fg_color="#E2E8F0", progress_color=ACCENT_ORANGE)
        self.bench_prog.set(0.0)
        self.bench_prog.pack(fill="x", padx=24, pady=(0, 12))

        # Real-time console log stream
        self.txt_bench_log = ctk.CTkTextbox(
            card,
            height=100,
            fg_color="#0A0F1D",
            text_color="#FCD34D",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=10,
            border_width=1,
            border_color="#1E293B"
        )
        self.txt_bench_log.pack(fill="x", padx=24, pady=(0, 18))
        self.txt_bench_log.insert("end", "Awaiting live benchmark start. Click 'Run Live Hardware Benchmark' above to execute.\n")

    def _build_recent_job_card(self):
        self.card_recent = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        self.card_recent.pack(fill="x", padx=10, pady=(0, 16))

        h_row = ctk.CTkFrame(self.card_recent, fg_color="transparent")
        h_row.pack(fill="x", padx=24, pady=(18, 10))

        ic = ctk.CTkLabel(h_row, text="🎬", font=ctk.CTkFont(size=15), fg_color="#EDE9FE", corner_radius=8, width=32, height=32)
        ic.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            h_row,
            text="Latest Video Render Job Metrics",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(side="left")

        self.lbl_recent_info = ctk.CTkLabel(
            self.card_recent,
            text="No video renders completed yet in this session. Submit a job from 'New Render Job' to inspect production metrics.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        self.lbl_recent_info.pack(anchor="w", padx=24, pady=(0, 14))

        self.btn_load_recent = ctk.CTkButton(
            self.card_recent,
            text="📥  Load Production Metrics into Calculator",
            command=self._load_recent_into_calculator,
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color=TEXT_PRIMARY,
            corner_radius=10,
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled"
        )
        self.btn_load_recent.pack(anchor="w", padx=24, pady=(0, 18))

    def _refresh_recent_job_card(self):
        last = getattr(self.app, "last_render_benchmark", None)
        if not last:
            self.lbl_recent_info.configure(
                text="No video renders completed yet in this session. Submit a job from 'New Render Job' to inspect production metrics."
            )
            self.btn_load_recent.configure(state="disabled")
            return

        in_name = last.get("input_name", "Unknown")
        in_size = last.get("input_size_mb", 0.0)
        t_up = last.get("upload_sec", 0.0)
        t_rend = last.get("render_sec", 0.0)
        t_dl = last.get("download_sec", 0.0)
        t_tot = last.get("total_sec", 0.0)

        info_txt = (
            f"File: {in_name} ({in_size} MB)\n"
            f"• Upload Time: {t_up:.2f}s  |  • Remote GPU Render: {t_rend:.2f}s  |  • Download: {t_dl:.2f}s  |  • Total Remote Time: {t_tot:.2f}s"
        )
        self.lbl_recent_info.configure(text=info_txt, text_color=TEXT_PRIMARY)
        self.btn_load_recent.configure(state="normal")

    def _load_recent_into_calculator(self):
        last = getattr(self.app, "last_render_benchmark", None)
        if not last:
            return

        t_up = last.get("upload_sec", 0.0)
        t_rend = last.get("render_sec", 0.0)
        t_dl = last.get("download_sec", 0.0)

        self.entry_up_t.delete(0, "end")
        self.entry_up_t.insert(0, f"{t_up:.2f}")

        self.entry_render_t.delete(0, "end")
        self.entry_render_t.insert(0, f"{t_rend:.2f}")

        self.entry_dl_t.delete(0, "end")
        self.entry_dl_t.insert(0, f"{t_dl:.2f}")

        # If local CPU field is empty, prompt user or keep current
        loc_val = self.entry_local_t.get().strip()
        if loc_val:
            self._on_compute_clicked()
        else:
            messagebox.showinfo(
                "Production Metrics Loaded",
                f"Loaded Remote Times:\nUpload: {t_up:.2f}s\nGPU Render: {t_rend:.2f}s\nDownload: {t_dl:.2f}s\n\n"
                "Please enter your estimated or tested Local CPU Time (s) to calculate the speedup ratio."
            )

    def _build_calculator_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=24, pady=(18, 12))

        ic = ctk.CTkLabel(h_row, text="📐", font=ctk.CTkFont(size=15), fg_color="#DBEAFE", corner_radius=8, width=32, height=32)
        ic.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(h_row, text="Speedup Measurement Calculator", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=24, pady=(0, 16))
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 4 Inputs (Clean initial state, no dummy values)
        ctk.CTkLabel(grid, text="Local CPU Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.entry_local_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY, placeholder_text="e.g. 18.5")
        self.entry_local_t.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(grid, text="Upload Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.entry_up_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY, placeholder_text="e.g. 0.4")
        self.entry_up_t.grid(row=1, column=1, sticky="ew", padx=6)

        ctk.CTkLabel(grid, text="Remote GPU Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=2, sticky="w", pady=(0, 4))
        self.entry_render_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY, placeholder_text="e.g. 2.1")
        self.entry_render_t.grid(row=1, column=2, sticky="ew", padx=6)

        ctk.CTkLabel(grid, text="Download Time (s)", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY).grid(row=0, column=3, sticky="w", pady=(0, 4))
        self.entry_dl_t = ctk.CTkEntry(grid, fg_color=BG_INPUT, border_color=BORDER_COLOR, corner_radius=10, height=38, text_color=TEXT_PRIMARY, placeholder_text="e.g. 0.2")
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
        self.res_box.grid_columnconfigure(0, weight=1)
        self.res_box.grid_columnconfigure(1, weight=0)

        left_res = ctk.CTkFrame(self.res_box, fg_color="transparent")
        left_res.grid(row=0, column=0, sticky="nsew", padx=18, pady=14)

        t_row = ctk.CTkFrame(left_res, fg_color="transparent")
        t_row.pack(fill="x")

        self.lbl_speedup_icon = ctk.CTkLabel(t_row, text="⚡", font=ctk.CTkFont(size=18), fg_color="#E2E8F0", corner_radius=8, width=32, height=32)
        self.lbl_speedup_icon.pack(side="left", padx=(0, 8))

        self.lbl_speedup = ctk.CTkLabel(t_row, text="Speedup Factor: Awaiting Input / Benchmark", font=ctk.CTkFont(size=17, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_speedup.pack(side="left")

        self.lbl_details = ctk.CTkLabel(
            left_res,
            text="Enter measured times or execute the automated Live Benchmark above to compute real hardware metrics.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        self.lbl_details.pack(anchor="w", pady=(8, 0))

        # Right Chart
        right_res = ctk.CTkFrame(self.res_box, fg_color="transparent")
        right_res.grid(row=0, column=1, sticky="e", padx=(0, 18), pady=14)
        self.res_chart = BenchmarkBarCanvas(right_res, width=200, height=65)
        self.res_chart.pack()

    def _build_formula_guide(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 20))

        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=24, pady=(18, 10))

        ic = ctk.CTkLabel(h_row, text="📚", font=ctk.CTkFont(size=15), fg_color="#FEE2E2", corner_radius=8, width=32, height=32)
        ic.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(h_row, text="Evaluation Principles & Equations", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")

        f1 = "• Remote Total Time = T_upload + T_remote_render + T_download"
        f2 = "• Speedup Factor = T_local_render / Remote Total Time"
        f3 = "• Network Overhead Ratio = (T_upload + T_download) / Remote Total Time * 100%"
        f4 = "• Net Time Saved = T_local_render - Remote Total Time"

        for text in [f1, f2, f3, f4]:
            ctk.CTkLabel(card, text=text, font=ctk.CTkFont(family="Consolas", size=12), text_color=TEXT_SECONDARY).pack(anchor="w", padx=24, pady=3)

        # Note Callout Box
        note_box = ctk.CTkFrame(card, fg_color="#EFF6FF", corner_radius=12, border_width=1, border_color="#BFDBFE")
        note_box.pack(fill="x", padx=24, pady=(14, 20))

        n_row = ctk.CTkFrame(note_box, fg_color="transparent")
        n_row.pack(fill="x", padx=14, pady=12)

        ic_info = ctk.CTkLabel(n_row, text="ℹ️", font=ctk.CTkFont(size=14))
        ic_info.pack(side="left", anchor="n", padx=(0, 8))

        ctk.CTkLabel(
            n_row,
            text="Note: Very short clips (<10s) may see Speedup < 1.0x due to network transfer overhead.\nLonger and higher-resolution videos (1080p/4K) typically achieve 3x to 10x net speedup.",
            font=ctk.CTkFont(size=12),
            text_color="#1E40AF",
            justify="left",
            anchor="w"
        ).pack(side="left", fill="x")

    def _start_live_benchmark(self):
        if self._bench_running:
            return

        if not self.app.is_connected:
            messagebox.showwarning(
                "Worker Server Offline",
                "Remote Worker Server is offline. Please connect via LAN wire first before running the live benchmark."
            )
            return

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            messagebox.showerror(
                "FFmpeg Missing",
                "FFmpeg executable was not found on your local system PATH. FFmpeg is required to perform local CPU benchmark."
            )
            return

        self._bench_running = True
        self.btn_run_bench.configure(state="disabled", text="⏳ Running Benchmark...")
        self.lbl_bench_status.configure(text="● Executing live hardware benchmark...", text_color=ACCENT_ORANGE)
        self.bench_prog.set(0.0)

        self.txt_bench_log.delete("1.0", "end")
        self._log_bench("🚀 [Init] Starting Live Hardware Benchmark Suite...")

        threading.Thread(target=self._run_live_benchmark_worker, daemon=True).start()

    def _log_bench(self, line: str):
        self.after(0, lambda: self._append_bench_log(line))

    def _append_bench_log(self, line: str):
        self.txt_bench_log.insert("end", line + "\n")
        self.txt_bench_log.see("end")

    def _update_bench_prog(self, val: float, status_text: str):
        self.after(0, lambda: self._apply_prog_ui(val, status_text))

    def _apply_prog_ui(self, val: float, status_text: str):
        self.bench_prog.set(val)
        self.lbl_bench_status.configure(text=f"● {status_text}", text_color=ACCENT_ORANGE)

    def _run_live_benchmark_worker(self):
        temp_dir = Path(tempfile.gettempdir())
        src_file = temp_dir / "bench_test_source.mp4"
        local_out = temp_dir / "bench_local_cpu.mp4"
        remote_out = temp_dir / "bench_remote_download.mp4"

        ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
        net = NetworkClient(
            self.app.config_data.get("server_host", "127.0.0.1"),
            self.app.config_data.get("server_port", 8000),
            self.app.config_data.get("api_token", "")
        )

        try:
            # Step 1: Generate standardized 1080p synthetic clip (4s)
            self._log_bench("[1/5] Generating standardized 1080p test video (4s, 30fps)...")
            self._update_bench_prog(0.15, "Generating 1080p payload...")
            cmd_gen = [
                ffmpeg_bin, "-y",
                "-f", "lavfi", "-i", "testsrc=duration=4:size=1920x1080:rate=30",
                "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                str(src_file)
            ]
            subprocess.run(cmd_gen, capture_output=True, check=True)
            payload_size_kb = src_file.stat().st_size / 1024
            self._log_bench(f"✔ Standard payload generated: {payload_size_kb:.1f} KB")

            # Step 2: Measure Local Laptop CPU Transcode
            self._log_bench("[2/5] Benchmarking Local Laptop CPU transcode (libx264, medium, 720p)...")
            self._update_bench_prog(0.35, "Testing Local Laptop CPU...")
            cmd_cpu = [
                ffmpeg_bin, "-y",
                "-i", str(src_file),
                "-vf", "scale=-2:720",
                "-c:v", "libx264", "-preset", "medium", "-b:v", "2M",
                str(local_out)
            ]
            t0_cpu = time.perf_counter()
            subprocess.run(cmd_cpu, capture_output=True, check=True)
            t_local_cpu = max(0.01, round(time.perf_counter() - t0_cpu, 2))
            self._log_bench(f"✔ Local Laptop CPU Render Time: {t_local_cpu:.2f} seconds")

            # Step 3: Measure LAN Upload Time
            self._log_bench(f"[3/5] Uploading payload to Remote Server over LAN wire...")
            self._update_bench_prog(0.55, "Uploading payload to server...")
            checksum = net.compute_sha256(src_file)
            t0_up = time.perf_counter()
            up_res = net.upload_file(src_file)
            if not up_res.get("success"):
                raise RuntimeError(f"Upload failed: {up_res.get('error')}")
            t_up = max(0.01, round(time.perf_counter() - t0_up, 2))
            self._log_bench(f"✔ LAN Upload Time: {t_up:.2f} seconds")

            # Step 4: Measure Remote GPU Render Time
            self._log_bench("[4/5] Executing Remote NVIDIA NVENC GPU transcode (720p, p4 preset)...")
            self._update_bench_prog(0.75, "Remote GPU encoding...")
            job_res = net.create_job(
                file_name=src_file.name,
                checksum=checksum,
                resolution="720p",
                preset="p4",
                bitrate="2M",
                allow_cpu=True
            )
            if not job_res.get("success"):
                raise RuntimeError(f"Failed to submit remote job: {job_res.get('error')}")
            job_id = job_res["job_id"]

            t0_rend = time.perf_counter()
            while True:
                time.sleep(0.3)
                stat = net.get_job_status(job_id)
                if not stat.get("success"):
                    raise RuntimeError(f"Failed polling remote job: {stat.get('error')}")
                j_data = stat["data"]
                s = j_data.get("status")
                if s == "COMPLETED":
                    break
                elif s in ("FAILED", "CANCELLED"):
                    raise RuntimeError(f"Remote job {s}: {j_data.get('error_message')}")
            t_render = max(0.01, round(time.perf_counter() - t0_rend, 2))
            self._log_bench(f"✔ Remote GPU Render Time: {t_render:.2f} seconds")

            # Step 5: Measure LAN Download Time
            self._log_bench("[5/5] Downloading encoded stream from Remote Server...")
            self._update_bench_prog(0.9, "Downloading output stream...")
            t0_dl = time.perf_counter()
            dl_res = net.download_file(job_id, remote_out)
            if not dl_res.get("success"):
                raise RuntimeError(f"Download failed: {dl_res.get('error')}")
            t_dl = max(0.01, round(time.perf_counter() - t0_dl, 2))
            self._log_bench(f"✔ LAN Download Time: {t_dl:.2f} seconds")

            # Final Calculations
            t_remote_total = round(t_up + t_render + t_dl, 2)
            speedup = round(t_local_cpu / t_remote_total, 2)
            overhead = round(t_up + t_dl, 2)
            overhead_pct = round((overhead / t_remote_total) * 100.0, 1)
            saved = round(t_local_cpu - t_remote_total, 2)

            self._log_bench("--------------------------------------------------")
            self._log_bench("🏁 LIVE HARDWARE BENCHMARK COMPLETE:")
            self._log_bench(f"• Local CPU Time: {t_local_cpu:.2f}s  |  Remote Total: {t_remote_total:.2f}s")
            self._log_bench(f"• Speedup Factor: {speedup:.2f}x ({'Faster' if speedup >= 1.0 else 'Slower'} than Local)")
            self._log_bench(f"• Network Overhead: {overhead:.2f}s ({overhead_pct:.1f}%)")
            self._log_bench(f"• Net Time Saved: {saved:.2f}s")

            self.after(0, lambda: self._apply_benchmark_results(
                t_local_cpu, t_up, t_render, t_dl, speedup, overhead, overhead_pct, saved, t_remote_total
            ))

        except Exception as e:
            err_msg = str(e)
            self._log_bench(f"❌ Benchmark Failed: {err_msg}")
            self.after(0, lambda err=err_msg: self._on_benchmark_error(err))
        finally:
            for p in (src_file, local_out, remote_out):
                try:
                    if p.exists():
                        p.unlink()
                except Exception:
                    pass
            self._bench_running = False
            self.after(0, lambda: self.btn_run_bench.configure(state="normal", text="▶  Run Live Hardware Benchmark"))

    def _apply_benchmark_results(self, t_loc: float, t_up: float, t_rend: float, t_dl: float, speedup: float, overhead: float, overhead_pct: float, saved: float, t_rem_total: float):
        self.bench_prog.set(1.0)
        self.lbl_bench_status.configure(text=f"✔ Benchmark Complete ({speedup:.2f}x Speedup)", text_color=ACCENT_GREEN)

        self.entry_local_t.delete(0, "end")
        self.entry_local_t.insert(0, f"{t_loc:.2f}")

        self.entry_up_t.delete(0, "end")
        self.entry_up_t.insert(0, f"{t_up:.2f}")

        self.entry_render_t.delete(0, "end")
        self.entry_render_t.insert(0, f"{t_rend:.2f}")

        self.entry_dl_t.delete(0, "end")
        self.entry_dl_t.insert(0, f"{t_dl:.2f}")

        color = ACCENT_GREEN if speedup >= 1.0 else ACCENT_RED
        self.lbl_speedup_icon.configure(text="🏆" if speedup >= 1.0 else "⚠️", fg_color="#D1FAE5" if speedup >= 1.0 else "#FEE2E2")
        self.lbl_speedup.configure(
            text=f"Speedup Factor: {speedup:.2f}x ({'Faster' if speedup >= 1.0 else 'Slower'} than Local)",
            text_color=color
        )

        msg = (
            f"Remote Total Time: {t_rem_total:.2f}s (vs Local: {t_loc:.2f}s)\n"
            f"Network Overhead: {overhead:.2f}s ({overhead_pct:.1f}% of total job duration)\n"
            f"Net Time Saved: {saved:.2f} seconds"
        )
        self.lbl_details.configure(text=msg)
        self.res_chart.update_bars(t_loc, t_rem_total)
        self.hdr_chart.update_bars(t_loc, t_rem_total)

    def _on_benchmark_error(self, err_msg: str):
        self.bench_prog.set(0.0)
        self.lbl_bench_status.configure(text="❌ Benchmark Failed", text_color=ACCENT_RED)
        messagebox.showerror("Benchmark Execution Failed", f"Live benchmark could not complete:\n\n{err_msg}")

    def _on_compute_clicked(self):
        try:
            raw_loc = self.entry_local_t.get().strip()
            raw_up = self.entry_up_t.get().strip()
            raw_rend = self.entry_render_t.get().strip()
            raw_dl = self.entry_dl_t.get().strip()

            if not raw_loc or not raw_up or not raw_rend or not raw_dl:
                messagebox.showinfo("Missing Values", "Please fill in all 4 timing fields to calculate speedup and network overhead.")
                return

            t_loc = float(raw_loc)
            t_up = float(raw_up)
            t_rend = float(raw_rend)
            t_dl = float(raw_dl)

            t_rem_total = t_up + t_rend + t_dl
            if t_rem_total <= 0:
                messagebox.showwarning("Invalid Input", "Remote total duration must be greater than zero.")
                return

            speedup = t_loc / t_rem_total
            overhead = t_up + t_dl
            overhead_pct = (overhead / t_rem_total) * 100.0
            saved = t_loc - t_rem_total

            color = ACCENT_GREEN if speedup >= 1.0 else ACCENT_RED
            self.lbl_speedup_icon.configure(text="🏆" if speedup >= 1.0 else "⚠️", fg_color="#D1FAE5" if speedup >= 1.0 else "#FEE2E2")
            self.lbl_speedup.configure(
                text=f"Speedup Factor: {speedup:.2f}x ({'Faster' if speedup >= 1.0 else 'Slower'} than Local)",
                text_color=color
            )

            msg = (
                f"Remote Total Time: {t_rem_total:.2f}s (vs Local: {t_loc:.2f}s)\n"
                f"Network Overhead: {overhead:.2f}s ({overhead_pct:.1f}% of total job duration)\n"
                f"Net Time Saved: {saved:.2f} seconds"
            )
            self.lbl_details.configure(text=msg)
            self.res_chart.update_bars(t_loc, t_rem_total)
            self.hdr_chart.update_bars(t_loc, t_rem_total)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numerical seconds (e.g. 18.5).")
