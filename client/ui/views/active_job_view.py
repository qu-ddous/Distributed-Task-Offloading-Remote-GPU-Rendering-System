import os
import sys
import time
import threading
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from tkinter import messagebox
import customtkinter as ctk

from client.ui.theme import *
from client.services.network_client import NetworkClient

class ActiveJobView(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master, fg_color="transparent")
        self.app = app_controller

        self.active_job_id: Optional[str] = None
        self.ws_stop_event = asyncio.Event()

        self._build_header_card()
        self._build_progress_card()
        self._build_results_card()
        self._build_live_telemetry_card()
        self._build_console_logs_card()

    def _build_header_card(self):
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        header.pack(fill="x", padx=10, pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=22, pady=16, sticky="w")

        ctk.CTkLabel(title_box, text="Live Telemetry & Execution Monitor", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        self.lbl_job_id_display = ctk.CTkLabel(title_box, text="No active render job currently queued", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_job_id_display.pack(anchor="w")

        self.btn_cancel = ctk.CTkButton(
            header,
            text="✖  Cancel Job",
            command=self._on_cancel_clicked,
            fg_color="#FEE2E2",
            hover_color="#FECACA",
            text_color=ACCENT_RED,
            corner_radius=10,
            width=120,
            height=34,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled"
        )
        self.btn_cancel.grid(row=0, column=1, padx=22, pady=16, sticky="e")

    def _build_progress_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 16))

        self.progress_bar = ctk.CTkProgressBar(card, height=14, corner_radius=7, fg_color="#E2E8F0", progress_color=ACCENT_BLUE)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=22, pady=(18, 12))

        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=22, pady=(0, 16))
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_stage = ctk.CTkLabel(stats, text="Stage: Idle", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_stage.grid(row=0, column=0, sticky="w")

        self.lbl_pct = ctk.CTkLabel(stats, text="0.0%", font=ctk.CTkFont(size=15, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_pct.grid(row=0, column=1)

        self.lbl_elapsed = ctk.CTkLabel(stats, text="Elapsed: 00:00", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_elapsed.grid(row=0, column=2)

        self.lbl_eta = ctk.CTkLabel(stats, text="ETA: --", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_eta.grid(row=0, column=3, sticky="e")

    def _build_results_card(self):
        self.result_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        self.result_card.pack(fill="x", padx=10, pady=(0, 16))

        r_box = ctk.CTkFrame(self.result_card, fg_color="transparent")
        r_box.pack(fill="x", padx=22, pady=16)
        r_box.grid_columnconfigure(1, weight=1)

        self.lbl_result_icon = ctk.CTkLabel(
            r_box,
            text="⚡",
            font=ctk.CTkFont(size=18),
            fg_color="#F1F5F9",
            corner_radius=12,
            width=42,
            height=42
        )
        self.lbl_result_icon.grid(row=0, column=0, rowspan=2, padx=(0, 14), sticky="n")

        self.lbl_result_status = ctk.CTkLabel(
            r_box,
            text="Job Status: Awaiting Submission",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        self.lbl_result_status.grid(row=0, column=1, sticky="w")

        self.lbl_result_details = ctk.CTkLabel(
            r_box,
            text="Submit a video from 'New Render Job' to stream real-time NVENC logs, frames, and performance.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            justify="left",
            anchor="w"
        )
        self.lbl_result_details.grid(row=1, column=1, sticky="w", pady=(4, 0))

        # Bottom row with Open Folder Button
        self.btn_open_folder = ctk.CTkButton(
            self.result_card,
            text="📂  Open Output Folder",
            command=self._on_open_folder_clicked,
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            corner_radius=10,
            height=34,
            width=180,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.last_saved_folder: Optional[Path] = None

    def _build_live_telemetry_card(self):
        self.telem_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        self.telem_card.pack(fill="x", padx=10, pady=(0, 16))

        top = ctk.CTkFrame(self.telem_card, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(14, 10))

        ctk.CTkLabel(top, text="🖥️  Remote Server Live Hardware Utilization", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_telem_status = ctk.CTkLabel(top, text="● Streaming Telemetry", font=ctk.CTkFont(size=11, weight="bold"), text_color=ACCENT_GREEN, fg_color="#D1FAE5", corner_radius=6, padx=8, pady=2)
        self.lbl_telem_status.pack(side="right")

        # 3 Metrics Row
        row = ctk.CTkFrame(self.telem_card, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(0, 16))
        row.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Server CPU
        c1 = ctk.CTkFrame(row, fg_color=BG_CARD_ALT, corner_radius=10)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(c1, text="REMOTE CPU LOAD", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(8, 2))
        self.lbl_live_cpu = ctk.CTkLabel(c1, text="--%", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_live_cpu.pack(anchor="w", padx=12, pady=(0, 4))
        self.bar_live_cpu = ctk.CTkProgressBar(c1, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=ACCENT_BLUE)
        self.bar_live_cpu.set(0.0)
        self.bar_live_cpu.pack(fill="x", padx=12, pady=(0, 10))

        # 2. Server RAM
        c2 = ctk.CTkFrame(row, fg_color=BG_CARD_ALT, corner_radius=10)
        c2.grid(row=0, column=1, sticky="nsew", padx=4)
        ctk.CTkLabel(c2, text="REMOTE RAM USED", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(8, 2))
        self.lbl_live_ram = ctk.CTkLabel(c2, text="-- / -- GB", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_live_ram.pack(anchor="w", padx=12, pady=(0, 4))
        self.bar_live_ram = ctk.CTkProgressBar(c2, height=6, corner_radius=3, fg_color="#E2E8F0", progress_color=ACCENT_PURPLE)
        self.bar_live_ram.set(0.0)
        self.bar_live_ram.pack(fill="x", padx=12, pady=(0, 10))

        # 3. Encoder Speed & FPS
        c3 = ctk.CTkFrame(row, fg_color=BG_CARD_ALT, corner_radius=10)
        c3.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(c3, text="RENDER PERFORMANCE", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(8, 2))
        self.lbl_live_perf = ctk.CTkLabel(c3, text="FPS: -- | Speed: --", font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT_GREEN)
        self.lbl_live_perf.pack(anchor="w", padx=12, pady=(0, 4))
        self.lbl_live_engine = ctk.CTkLabel(c3, text="Active compute processing", font=ctk.CTkFont(size=11), text_color=TEXT_SECONDARY)
        self.lbl_live_engine.pack(anchor="w", padx=12, pady=(0, 10))

    def _build_console_logs_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="both", expand=True, padx=10, pady=(0, 16))

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(14, 6))

        ctk.CTkLabel(top, text="FFmpeg NVENC Real-Time Console Stream", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY).pack(side="left")

        btn_clear = ctk.CTkButton(
            top,
            text="Clear Logs",
            command=self._clear_logs,
            width=75,
            height=26,
            corner_radius=6,
            fg_color="#F1F5F9",
            hover_color="#E2E8F0",
            text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        btn_clear.pack(side="right")

        self.txt_console = ctk.CTkTextbox(
            card,
            fg_color="#0A0F1D",
            text_color="#34D399",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=12,
            border_width=1,
            border_color="#1E293B"
        )
        self.txt_console.pack(fill="both", expand=True, padx=22, pady=(0, 18))

    def append_log(self, msg: str):
        self.txt_console.insert("end", msg + "\n")
        self.txt_console.see("end")

    def _clear_logs(self):
        self.txt_console.delete("1.0", "end")

    def run_render_flow(self, params: Dict[str, Any]):
        self._clear_logs()
        self.current_job_params = params
        self.btn_cancel.configure(state="normal")
        self.btn_open_folder.pack_forget()

        input_file = params["input_file"]
        checksum = params["checksum"]
        res = params["resolution"]
        bitrate = params["bitrate"]
        preset = params["preset"]
        out_name = params["output_name"]
        out_dir = params["output_dir"]
        allow_cpu = params["allow_cpu"]

        host = self.app.config_data.get("server_host", "127.0.0.1")
        port = self.app.config_data.get("server_port", 8000)
        token = self.app.config_data.get("api_token", "")

        net = NetworkClient(host, port, token)
        start_overall = time.time()

        # Phase 1: Uploading
        self.lbl_stage.configure(text="Stage: Uploading video...")
        self.lbl_pct.configure(text="0.0%")
        self.progress_bar.set(0.0)
        self.lbl_result_icon.configure(text="⬆️", fg_color="#DBEAFE")
        self.lbl_result_status.configure(text="Job Status: Uploading File Stream", text_color=ACCENT_BLUE)
        self.lbl_result_details.configure(text=f"Streaming {input_file.name} to {host}:{port} with cryptographic SHA-256 validation...")
        self.append_log(f"[Upload] Initiating upload for {input_file.name} ({input_file.stat().st_size:,} bytes)...")

        def on_upload_prog(sent, total):
            pct = (sent / total) * 100.0 if total > 0 else 0
            self.after(0, lambda: self._update_upload_ui(pct, sent, total))

        t_up_start = time.time()
        res_upload = net.submit_job(
            input_file=input_file,
            checksum=checksum,
            resolution=res,
            bitrate=bitrate,
            preset=preset,
            output_filename=out_name,
            allow_cpu_fallback=allow_cpu,
            progress_callback=on_upload_prog
        )
        t_up_duration = round(time.time() - t_up_start, 2)

        if not res_upload.get("success"):
            err = res_upload.get("error", "Upload error")
            self.append_log(f"[Error] Failed uploading to http://{host}:{port}. Details: {err}")
            self.after(0, lambda: self._on_failure(f"Upload Failed: {err}\n\nTarget Server: http://{host}:{port}\nMake sure GPUWorkerServer.exe is actively running on that PC and not blocked by firewall."))
            return

        job_info = res_upload["job"]
        job_id = job_info["job_id"]
        self.active_job_id = job_id
        self.after(0, lambda: self.lbl_job_id_display.configure(text=f"Active Job ID: {job_id}"))
        self.append_log(f"[Upload] Completed in {t_up_duration}s. Server confirmed SHA-256 match.")

        # Phase 2: Live Remote Compute / Rendering
        is_script = input_file.suffix.lower() in [".py", ".pyw", ".bat", ".cmd", ".ps1"]
        stage_desc = "Stage: Remote Compute Execution (100% Server Hardware)..." if is_script else "Stage: Remote GPU Rendering..."
        status_desc = "Job Status: Remote Compute (100% Server)" if is_script else "Job Status: Remote GPU Encoding (NVENC)"
        self.lbl_stage.configure(text=stage_desc)
        self.lbl_result_icon.configure(text="🧠" if input_file.suffix.lower() in [".py", ".pyw"] else "⚡", fg_color="#EDE9FE")
        self.lbl_result_status.configure(text=status_desc, text_color=ACCENT_PURPLE)
        self.ws_stop_event.clear()

        render_done_event = threading.Event()
        render_summary: Dict[str, Any] = {"status": "unknown"}

        def on_ws_msg(msg: Dict[str, Any]):
            mtype = msg.get("type")
            if mtype == "progress":
                pct = msg.get("percent", 0.0)
                elapsed = msg.get("elapsed_seconds", 0.0)
                eta = msg.get("eta_seconds")
                speed = msg.get("speed")
                fps = msg.get("fps")
                telem = msg.get("server_telemetry")
                self.after(0, lambda: self._update_render_ui(pct, elapsed, eta, speed, fps, telem))
            elif mtype == "log":
                txt = msg.get("message", "")
                self.after(0, lambda: self.append_log(f"[Worker] {txt}"))
            elif mtype == "state":
                st = msg.get("status")
                if st == "completed":
                    render_summary["status"] = "completed"
                    render_summary["output_checksum"] = msg.get("output_checksum")
                    render_summary["render_seconds"] = msg.get("total_render_seconds", 0)
                    render_done_event.set()
                elif st in ["failed", "cancelled"]:
                    render_summary["status"] = st
                    render_summary["error"] = msg.get("message") or msg.get("error")
                    render_done_event.set()
            elif mtype == "error":
                render_summary["status"] = "failed"
                render_summary["error"] = msg.get("error")
                render_done_event.set()

        def ws_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(net.listen_websocket(job_id, on_ws_msg, self.ws_stop_event))
            loop.close()

        threading.Thread(target=ws_worker, daemon=True).start()

        render_done_event.wait()
        self.ws_stop_event.set()

        if render_summary.get("status") != "completed":
            err = render_summary.get("error", "Execution failed or was cancelled.")
            self.after(0, lambda: self._on_failure(f"Execution Error: {err}"))
            return

        # Phase 3: Downloading
        expected_hash = render_summary.get("output_checksum")
        t_render_sec = render_summary.get("render_seconds", 0)
        target_path = out_dir / out_name
        self.last_saved_folder = out_dir

        dl_title = "Stage: Downloading execution artifacts..." if is_script else "Stage: Downloading finished video..."
        self.lbl_stage.configure(text=dl_title)
        self.lbl_result_icon.configure(text="⬇️", fg_color="#CFFAFE")
        self.lbl_result_status.configure(text="Job Status: Downloading Finished Output", text_color=ACCENT_CYAN)
        self.append_log(f"[Download] Downloading output artifact to {target_path}...")

        def on_dl_prog(received, total):
            pct = (received / total) * 100.0 if total > 0 else 0
            self.after(0, lambda: self._update_download_ui(pct, received, total))

        t_dl_start = time.time()
        dl_res = net.download_output_file(
            job_id=job_id,
            target_path=target_path,
            expected_checksum=expected_hash,
            progress_callback=on_dl_prog
        )
        t_dl_sec = round(time.time() - t_dl_start, 2)

        if not dl_res.get("success"):
            err = dl_res.get("error", "Download error.")
            self.after(0, lambda: self._on_failure(f"Download Error: {err}"))
            return

        total_sec = round(time.time() - start_overall, 2)
        self.after(0, lambda: self._on_success(
            target_file=target_path,
            upload_sec=t_up_duration,
            render_sec=t_render_sec,
            download_sec=t_dl_sec,
            total_sec=total_sec,
            checksum=dl_res.get("checksum", "")
        ))

    def _update_upload_ui(self, pct: float, sent: int, total: int):
        self.progress_bar.set(pct / 100.0)
        self.lbl_pct.configure(text=f"{pct:.1f}%")
        self.lbl_stage.configure(text=f"Stage: Uploading ({sent/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)")

    def _update_render_ui(self, pct: float, elapsed: float, eta: Optional[float], speed: Optional[str], fps: Optional[float], server_telemetry: Optional[dict] = None):
        self.progress_bar.set(pct / 100.0)
        self.lbl_pct.configure(text=f"{pct:.1f}%")
        m, s = divmod(int(elapsed), 60)
        self.lbl_elapsed.configure(text=f"Elapsed: {m:02d}:{s:02d}")
        if eta is not None and eta > 0:
            em, es = divmod(int(eta), 60)
            self.lbl_eta.configure(text=f"ETA: {em:02d}:{es:02d}")
        if speed and "Compute" in speed:
            self.lbl_stage.configure(text=f"Stage: Remote Server Compute Execution ({speed})")
        else:
            self.lbl_stage.configure(text=f"Stage: Remote Node Rendering ({speed or '1.0x'}, {fps or 0:.0f} fps)")

        speed_txt = speed or "1.0x"
        fps_txt = f"{fps:.0f} FPS" if fps else ("Multi-Core/GPU" if (speed and "Compute" in speed) else "-- FPS")
        self.lbl_live_perf.configure(text=f"{fps_txt}  •  {speed_txt}")

        if server_telemetry:
            cpu_p = server_telemetry.get("cpu_percent", 0.0)
            self.lbl_live_cpu.configure(text=f"{cpu_p:.1f}%")
            self.bar_live_cpu.set(min(1.0, max(0.02, cpu_p / 100.0)))

            ram_u = server_telemetry.get("ram_used_gb", 0.0)
            ram_t = server_telemetry.get("ram_total_gb", 0.0)
            ram_p = server_telemetry.get("ram_percent", 0.0)
            self.lbl_live_ram.configure(text=f"{ram_u:.1f} / {ram_t:.1f} GB ({ram_p:.0f}%)")
            self.bar_live_ram.set(min(1.0, max(0.02, ram_p / 100.0)))

    def _update_download_ui(self, pct: float, rec: int, total: int):
        self.progress_bar.set(pct / 100.0)
        self.lbl_pct.configure(text=f"{pct:.1f}%")
        self.lbl_stage.configure(text=f"Stage: Downloading ({rec/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)")

    def _on_failure(self, err_msg: str):
        self.btn_cancel.configure(state="disabled")
        self.progress_bar.set(0.0)
        self.lbl_stage.configure(text="Stage: Failed")
        self.lbl_result_icon.configure(text="✖", fg_color="#FEE2E2")
        self.lbl_result_status.configure(text="✖ Job Failed", text_color=ACCENT_RED)
        self.lbl_result_details.configure(text=f"Failure Reason: {err_msg}")
        self.append_log(f"[Error] {err_msg}")
        messagebox.showerror("Job Execution Failed", err_msg)

    def _on_success(self, target_file: Path, upload_sec: float, render_sec: float, download_sec: float, total_sec: float, checksum: str):
        self.btn_cancel.configure(state="disabled")
        self.progress_bar.set(1.0)
        self.lbl_pct.configure(text="100.0%")
        self.lbl_stage.configure(text="Stage: Completed Successfully")
        self.lbl_result_icon.configure(text="✔", fg_color="#D1FAE5")
        self.lbl_result_status.configure(text="Remote GPU Render Complete", text_color=ACCENT_GREEN)

        details = (
            f"Saved: {target_file.name}\n"
            f"Upload: {upload_sec}s | Render: {render_sec}s | Download: {download_sec}s | Total: {total_sec}s\n"
            f"SHA-256 Checksum: {checksum}"
        )
        self.lbl_result_details.configure(text=details)
        self.btn_open_folder.pack(anchor="w", padx=22, pady=(0, 16))

        in_file = self.current_job_params.get("input_file") if hasattr(self, "current_job_params") and self.current_job_params else None
        in_name = in_file.name if in_file else target_file.name
        in_size_mb = round(in_file.stat().st_size / (1024 * 1024), 2) if in_file and hasattr(in_file, "stat") and in_file.exists() else 0.0

        self.app.last_render_benchmark = {
            "target_file": target_file.name,
            "input_name": in_name,
            "input_size_mb": in_size_mb,
            "upload_sec": upload_sec,
            "render_sec": render_sec,
            "download_sec": download_sec,
            "total_sec": total_sec,
            "checksum": checksum,
            "timestamp": time.time()
        }

        self.append_log(f"[Finished] All stages completed successfully in {total_sec}s.")
        messagebox.showinfo("Render Finished", f"Remote GPU rendering complete!\nSaved to:\n{target_file}")

    def _on_cancel_clicked(self):
        if not self.active_job_id:
            return
        if not messagebox.askyesno("Confirm Cancel", "Cancel the currently active remote render job?"):
            return

        host = self.app.config_data.get("server_host", "127.0.0.1")
        port = self.app.config_data.get("server_port", 8000)
        token = self.app.config_data.get("api_token", "")
        net = NetworkClient(host, port, token)

        def do_cancel():
            net.cancel_job(self.active_job_id)
            self.ws_stop_event.set()
        threading.Thread(target=do_cancel, daemon=True).start()

    def _on_open_folder_clicked(self):
        if self.last_saved_folder and self.last_saved_folder.exists():
            if sys.platform == "win32":
                os.startfile(self.last_saved_folder)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", str(self.last_saved_folder)])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", str(self.last_saved_folder)])
