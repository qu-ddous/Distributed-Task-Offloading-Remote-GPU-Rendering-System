# Evidence & Capture Checklist: Screenshots and Demos

To submit or document your setup, take real screenshots and screen recordings of both machines in action. Do not fabricate captures. Place your real media files in this directory (`docs/screenshots/` and `docs/demos/`).

---

## 1. Screenshot Checklist

- [ ] **`01_dashboard_idle.png`**  
  *What to capture:* The desktop client immediately after launch with dark studio theme, showing server IP/port fields, file selection picker, and disconnected status.

- [ ] **`02_handshake_connected_nvenc.png`**  
  *What to capture:* Client status bar displaying **"● Worker: Online (v1.0.0)"**, **"● NVENC Ready (NVIDIA GeForce...)"**, and round-trip latency (e.g., `< 5ms`).

- [ ] **`03_file_selected_sha256.png`**  
  *What to capture:* The file picker populated with a real `.mp4` file, exhibiting file size (MB/bytes) and green verified SHA-256 hash.

- [ ] **`04_active_job_uploading.png`**  
  *What to capture:* Active job monitor during the upload phase showing real-time upload progress (e.g. `Uploading (45.2/120.0 MB)`).

- [ ] **`05_active_job_rendering_nvenc.png`**  
  *What to capture:* The progress bar in motion, showing live FFmpeg FPS (e.g., `160 fps`), speed (e.g., `3.2x`), elapsed time, and ETA. The live FFmpeg log window should display active console frames.

- [ ] **`06_worker_terminal_log.png`**  
  *What to capture:* The server command terminal showing FastAPI request logging, multipart file reception, checksum validation, and FFmpeg execution logs.

- [ ] **`07_job_completed_success.png`**  
  *What to capture:* The completion summary card showing total time breakdown (Upload time, Render time, Download time), output path, and the **"Open Output Folder"** action button.

- [ ] **`08_error_recovery_nvenc_missing.png`** (Optional Failure Test)  
  *What to capture:* Behavior when connecting to a machine without NVENC or with invalid token, showing clear, actionable user recovery guidance.

---

## 2. Demonstration Video / GIF Checklist

Place your recorded video or GIF in `docs/demos/`:

- [ ] **`demo_end_to_end_offloading.mp4`** (or `.gif`)  
  *Duration:* 30–60 seconds.  
  *Flow:*
  1. Click **Test Connection** (green indicators light up).
  2. Select an input video file (automatic checksum computation).
  3. Choose 1080p / 5M bitrate and click **Submit & Render Remotely**.
  4. Show the live progress bar and streaming logs updating via WebSocket.
  5. Show the completion message and opening the folder with the verified downloaded video.
