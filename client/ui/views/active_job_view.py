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
        self._build_console_logs_card()

    def _build_header_card(self):
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        header.pack(fill="x", padx=10, pady=(0, 15))
        header.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=20, pady=16, sticky="w")

        ctk.CTkLabel(title_box, text="Live Render Monitor", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        self.lbl_job_id_display = ctk.CTkLabel(title_box, text="No job currently active", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_job_id_display.pack(anchor="w")

        self.btn_cancel = ctk.CTkButton(
            header,
            text="✖ Cancel Job",
            command=self._on_cancel_clicked,
            fg_color=ACCENT_RED,
            hover_color=ACCENT_RED_HOVER,
            width=110,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            state="disabled"
        )
        self.btn_cancel.grid(row=0, column=1, padx=20, pady=16, sticky="e")

    def _build_progress_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", padx=10, pady=(0, 15))

        self.progress_bar = ctk.CTkProgressBar(card, height=14, corner_radius=7, fg_color="#262C3D", progress_color=ACCENT_BLUE)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=20, pady=(18, 10))

        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=20, pady=(0, 18))
        stats.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_stage = ctk.CTkLabel(stats, text="Stage: Idle", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_PRIMARY)
        self.lbl_stage.grid(row=0, column=0, sticky="w")

        self.lbl_pct = ctk.CTkLabel(stats, text="0.0%", font=ctk.CTkFont(size=14, weight="bold"), text_color=ACCENT_BLUE)
        self.lbl_pct.grid(row=0, column=1)

        self.lbl_elapsed = ctk.CTkLabel(stats, text="Elapsed: 00:00", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_elapsed.grid(row=0, column=2)

        self.lbl_eta = ctk.CTkLabel(stats, text="ETA: --", font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self.lbl_eta.grid(row=0, column=3, sticky="e")

    def _build_results_card(self):
        self.result_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        self.result_card.pack(fill="x", padx=10, pady=(0, 15))

        self.lbl_result_status = ctk.CTkLabel(self.result_card, text="Job Status: Awaiting Submission", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_MUTED)
        self.lbl_result_status.pack(anchor="w", padx=20, pady=(16, 4))

        self.lbl_result_details = ctk.CTkLabel(self.result_card, text="Submit a video from the 'New Render Job' page to monitor here.", font=ctk.CTkFont(size=12), text_color=TEXT_DIM, justify="left")
        self.lbl_result_details.pack(anchor="w", padx=20, pady=(0, 14))

        self.btn_open_folder = ctk.CTkButton(
            self.result_card,
            text="📂 Open Output Folder",
            command=self._on_open_folder_clicked,
            fg_color="#374151",
            hover_color="#4B5563",
            height=32,
            width=160
        )
        self.last_saved_folder: Optional[Path] = None

    def _build_console_logs_card(self):
        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(14, 6))

        ctk.CTkLabel(top, text="Remote Worker Stream Console", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_SECONDARY).pack(side="left")

        btn_clear = ctk.CTkButton(
            top,
            text="Clear Logs",
            command=self._clear_logs,
            width=70,
            height=24,
            fg_color="#2A3144",
            hover_color="#374151",
            font=ctk.CTkFont(size=11)
        )
        btn_clear.pack(side="right")

        self.txt_console = ctk.CTkTextbox(
            card,
            fg_color=BG_MAIN,
            text_color="#10B981",
            font=ctk.CTkFont(family="Courier", size=11),
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.txt_console.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def append_log(self, msg: str):
        self.txt_console.insert("end", msg + "\n")
        self.txt_console.see("end")

    def _clear_logs(self):
        self.txt_console.delete("1.0", "end")

    def run_render_flow(self, params: Dict[str, Any]):
        self._clear_logs()
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

        # Step 1: Uploading
        self.lbl_stage.configure(text="Stage: Uploading video...")
        self.lbl_pct.configure(text="0.0%")
        self.progress_bar.set(0.0)
        self.lbl_result_status.configure(text="● Job Status: Uploading Payload", text_color=ACCENT_BLUE)
        self.lbl_result_details.configure(text=f"Uploading {input_file.name} to http://{host}:{port} with SHA-256 verification...")
        self.append_log(f"[Upload] Starting upload for {input_file.name} ({input_file.stat().st_size:,} bytes)...")

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
            self.after(0, lambda: self._on_failure(f"Upload Failed: {err}"))
            return

        job_info = res_upload["job"]
        job_id = job_info["job_id"]
        self.active_job_id = job_id
        self.after(0, lambda: self.lbl_job_id_display.configure(text=f"Active Job ID: {job_id}"))
        self.append_log(f"[Upload] Completed in {t_up_duration}s. Server confirmed SHA-256 match.")

        # Step 2: Live WebSocket Rendering
        self.lbl_stage.configure(text="Stage: Remote GPU Rendering...")
        self.lbl_result_status.configure(text="● Job Status: Remote GPU Encoding (NVENC)", text_color=ACCENT_PURPLE)
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
                self.after(0, lambda: self._update_render_ui(pct, elapsed, eta, speed, fps))
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
            err = render_summary.get("error", "Rendering failed or was cancelled.")
            self.after(0, lambda: self._on_failure(f"Render Error: {err}"))
            return

        # Step 3: Downloading
        expected_hash = render_summary.get("output_checksum")
        t_render_sec = render_summary.get("render_seconds", 0)
        target_path = out_dir / out_name
        self.last_saved_folder = out_dir

        self.lbl_stage.configure(text="Stage: Downloading finished video...")
        self.lbl_result_status.configure(text="● Job Status: Downloading Stream", text_color=ACCENT_BLUE)
        self.append_log(f"[Download] Downloading finished video to {target_path}...")

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

    def _update_render_ui(self, pct: float, elapsed: float, eta: Optional[float], speed: Optional[str], fps: Optional[float]):
        self.progress_bar.set(pct / 100.0)
        self.lbl_pct.configure(text=f"{pct:.1f}%")
        m, s = divmod(int(elapsed), 60)
        self.lbl_elapsed.configure(text=f"Elapsed: {m:02d}:{s:02d}")
        if eta is not None and eta > 0:
            em, es = divmod(int(eta), 60)
            self.lbl_eta.configure(text=f"ETA: {em:02d}:{es:02d}")
        self.lbl_stage.configure(text=f"Stage: Remote GPU Rendering ({speed or '1.0x'}, {fps or 0:.0f} fps)")

    def _update_download_ui(self, pct: float, rec: int, total: int):
        self.progress_bar.set(pct / 100.0)
        self.lbl_pct.configure(text=f"{pct:.1f}%")
        self.lbl_stage.configure(text=f"Stage: Downloading ({rec/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)")

    def _on_failure(self, err_msg: str):
        self.btn_cancel.configure(state="disabled")
        self.progress_bar.set(0.0)
        self.lbl_stage.configure(text="Stage: Failed")
        self.lbl_result_status.configure(text="✖ Job Failed", text_color=ACCENT_RED)
        self.lbl_result_details.configure(text=f"Failure Reason: {err_msg}")
        self.append_log(f"[Error] {err_msg}")
        messagebox.showerror("Job Execution Failed", err_msg)

    def _on_success(self, target_file: Path, upload_sec: float, render_sec: float, download_sec: float, total_sec: float, checksum: str):
        self.btn_cancel.configure(state="disabled")
        self.progress_bar.set(1.0)
        self.lbl_pct.configure(text="100.0%")
        self.lbl_stage.configure(text="Stage: Completed Successfully")
        self.lbl_result_status.configure(text="✔ Remote GPU Render Complete", text_color=ACCENT_GREEN)

        details = (
            f"File: {target_file.name}\n"
            f"Upload: {upload_sec}s | Render: {render_sec}s | Download: {download_sec}s | Total: {total_sec}s\n"
            f"SHA-256 Checksum Verified: {checksum}"
        )
        self.lbl_result_details.configure(text=details)
        self.btn_open_folder.pack(anchor="w", padx=20, pady=(0, 16))

        self.append_log(f"[Finished] All stages completed successfully in {total_sec}s.")
        messagebox.showinfo("Render Finished", f"Rendered video successfully downloaded and verified!\nLocation: {target_file}")

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
