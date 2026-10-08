# ⚡ Distributed Task Offloading & Remote GPU Rendering System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)](https://www.python.org/)
[![UI: CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Acceleration: NVIDIA NVENC](https://img.shields.io/badge/Acceleration-NVIDIA%20NVENC-76B900.svg)](https://developer.nvidia.com/video-encode-decode-gpu-support-matrix)
[![Network: Direct Gigabit LAN](https://img.shields.io/badge/Network-Direct%20LAN%20(~0.5ms)-orange.svg)](#-direct-lan-hardware-setup)

A production-grade, distributed task offloading and hardware-accelerated remote computing suite. Designed to offload processor-heavy and GPU-intensive workloads (**4K Video Transcoding**, **Python / AI Model Training**, and **Batch Scripts**) from a low-power client laptop (0% heavy resource usage) to a dedicated worker server PC over a local area network (LAN/Ethernet) with wire-speed throughput and sub-millisecond latency.

---

## 📸 Visual Showcase & Real Application Screenshots

### 1. Dual Control Terminals: Client Studio & Worker Server
| Client Studio (`GPURenderStudio.exe`) | Worker Server (`GPUWorkerServer.exe`) |
| :---: | :---: |
| ![Client Host & Settings](docs/screenshots/01_client_host_settings.png) | ![Server Network Monitor](docs/screenshots/02_server_network_monitor.png) |
| *Client Studio: Host & Connection Settings with Server Hardware Detection* | *Worker Server: Real-time Network View & Connected Client Monitor* |

---

### 2. Client Studio Screens (`GPURenderStudio.exe`)
| Submit Universal Job | Live Active Job Monitor |
| :---: | :---: |
| ![Submit Job](docs/screenshots/03_client_submit_job.png) | ![Active Monitor](docs/screenshots/04_client_active_monitor.png) |
| *Task Profile Selection (Video, AI Python, Batch Script) & Preset Controls* | *Live Telemetry Cards, Dual Progress Bars & Streaming WebSockets* |

| Render Queue & History | Real-Time Diagnostics |
| :---: | :---: |
| ![Render Queue](docs/screenshots/05_client_render_queue.png) | ![Diagnostics](docs/screenshots/07_client_diagnostics.png) |
| *Task Queue with SHA-256 Checksum Badges & Output Folder Access* | *Round-Trip Latency Graph (< 1ms LAN), Health Checks & Auto-Repair* |

---

### 3. Server Node Screens (`GPUWorkerServer.exe`)
| Hardware Overview & Vitals | GPU Engine Detection & Acceleration |
| :---: | :---: |
| ![Server Overview](docs/screenshots/08_server_overview_dashboard.png) | ![Server GPU Hardware](docs/screenshots/09_server_gpu_hardware.png) |
| *Real-time CPU Load, Memory Allocation & Worker State* | *Hardware NVENC Engine Verification & Codec Matrix* |

---

### 4. System Architecture Blueprint
![UI Architecture Blueprint](docs/screenshots/10_ui_system_design_blueprint.jpg)
*High-level multi-screen UI/UX design blueprint and distributed pipeline.*

---

## 📑 Complete System Manual
For the in-depth screen-by-screen user guide, direct cable setup instructions, and step-by-step offloading walkthroughs, refer to:
👉 **[COMPREHENSIVE_SYSTEM_MANUAL.md](COMPREHENSIVE_SYSTEM_MANUAL.md)**

---

## 💡 Core Architecture & Philosophy

```
+-----------------------------------+                     +-----------------------------------+
|      CLIENT LAPTOP (Thin UI)      |  Cat6 LAN Cable     |     SERVER PC (Compute Node)      |
|  • CustomTkinter Desktop Studio   |<===================>|  • FastAPI High-Speed Daemon      |
|  • Chunked SHA-256 Hashing        |   1 Gbps (~0.5 ms)  |  • Dedicated NVIDIA NVENC / CPU   |
|  • Non-Blocking Async GUI         |   Zero Internet     |  • Isolated Task Sandbox Storage  |
|  • 0% Heavy Load on Battery       |     Required        |  • 100% Workload Execution        |
+-----------------------------------+                     +-----------------------------------+
```

1. **0% Client Laptop Load**: Your laptop acts purely as a thin controller. Whether transcoding a 20 GB video file or training a deep neural network, 100% of the RAM, CPU, and GPU execution occurs on the server PC.
2. **Wire-Speed Deterministic LAN**: Optimized for a direct RJ-45 Ethernet cable link between laptop and PC with sub-millisecond round-trip latency (~0.3 ms – 0.8 ms). No internet connection or cloud subscription required.
3. **End-to-End Cryptographic Integrity**: Every job transfer is protected by pre-flight and post-flight SHA-256 cryptographic checksums.
4. **Universal Compute Support**:
   - 🎬 **Video GPU Transcoding**: Accelerated via FFmpeg `h264_nvenc`, `hevc_nvenc`, and CPU fallback.
   - 🧠 **Python AI / ML Training**: Execute Python scripts (`.py`) on remote server hardware with live stdout/stderr WebSockets.
   - ⚡ **Batch & Shell Execution**: Execute `.bat`, `.cmd`, and `.ps1` automation scripts on the worker node.

---

## 🏗 Sequence & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client as Client Studio (GPURenderStudio.exe)
    participant Worker as Worker Server (GPUWorkerServer.exe)
    participant Engine as Hardware Engine (NVENC / Python)

    User->>Client: 1. Enter Worker IP & Click "Test & Connect"
    Client->>Worker: GET /api/v1/ping & GET /api/v1/health (Token Auth)
    Worker-->>Client: 200 OK (Hardware Specs, NVENC detected, Latency < 1ms)
    User->>Client: 2. Pick File & Configure Task Profile (Video / AI / Script)
    Client->>Client: Compute Pre-flight SHA-256 Checksum
    Client->>Worker: POST /api/v1/jobs (Multipart stream + Checksum + Parameters)
    Worker->>Worker: Verify SHA-256 & Create Sandboxed Execution Directory
    Worker-->>Client: 201 Created (Job ID assigned)
    Client->>Worker: WebSocket Connect ws:///api/v1/ws/{job_id}
    Worker->>Engine: Spawn Process (FFmpeg NVENC or Python Worker)
    loop Real-Time Telemetry & Log Streaming
        Engine-->>Worker: Progress pipe & stdout/stderr stream
        Worker-->>Client: WebSocket JSON frame (fps, speed, ETA, memory, live logs)
        Client-->>User: Update Telemetry Cards, Dual Progress Bars & Console
    end
    Engine-->>Worker: Exit Code 0 (Completed)
    Worker->>Worker: Calculate Output Artifact SHA-256 Checksum
    Worker-->>Client: WebSocket State Event: Completed
    Client->>Worker: GET /api/v1/jobs/{job_id}/download
    Worker-->>Client: Binary Stream + X-Checksum-SHA256 Header
    Client->>Client: Verify Downloaded SHA-256 Hash
    Client-->>User: Success Banner & Enable "Open Output Folder"
```

---

## 📂 Repository Structure

```
.
├── COMPREHENSIVE_SYSTEM_MANUAL.md     # In-depth architectural & screen user manual
├── README.md                          # Primary project documentation
├── server_entrypoint.py               # Server UI + FastAPI daemon unified launcher
├── client/
│   ├── app.py                         # Client desktop application entrypoint
│   ├── requirements.txt               # Client Python dependencies
│   ├── tests_client.py                # Client automated test suite
│   ├── services/
│   │   ├── config_manager.py          # Client local configuration persistence
│   │   ├── network_client.py          # HTTP & WebSocket client with SHA-256 hashing
│   │   └── watch_folder.py            # Automated folder monitor daemon
│   └── ui/
│       ├── main_window.py             # Client main navigation shell
│       ├── components/                # Modular UI widgets (sidebar, topbar, sparklines)
│       └── views/
│           ├── settings_view.py       # Host IP & Server Connection view
│           ├── render_job_view.py     # Multi-mode Task Submission view
│           ├── active_job_view.py     # Live Telemetry & Log Streaming view
│           ├── dashboard_view.py      # Render Queue & History view
│           ├── diagnostics_view.py    # Latency & Network Health view
│           └── benchmarks_view.py     # Hardware Benchmarking view
├── server/
│   ├── requirements.txt               # Server dependencies (FastAPI, uvicorn, psutil, etc.)
│   ├── app/
│   │   ├── main.py                    # FastAPI server entrypoint
│   │   ├── config.py                  # Pydantic server settings loader
│   │   ├── server_state.py            # Shared runtime state between GUI and API
│   │   ├── api/
│   │   │   ├── health.py              # Health check & capability endpoints
│   │   │   ├── jobs.py                # Job lifecycle (upload, run, cancel, download)
│   │   │   └── websocket.py           # Real-time WebSocket streaming
│   │   └── services/
│   │       ├── checksum_service.py    # High-performance chunked SHA-256 hasher
│   │       ├── connection_tracker.py  # Active connected client session monitor
│   │       ├── ffmpeg_service.py      # NVENC command generator & progress parser
│   │       ├── job_manager.py         # Universal runner (FFmpeg, Python, Batch scripts)
│   │       ├── security.py            # Path traversal guards & input sanitizer
│   │       └── system_service.py      # NVENC, GPU, CPU, and RAM telemetry provider
│   └── ui/
│       ├── server_window.py           # Server desktop GUI shell
│       └── views/
│           ├── overview_view.py       # System telemetry & hardware vitals
│           ├── queue_view.py          # Server active job queue
│           ├── logs_view.py           # Real-time console activity logs
│           ├── hardware_view.py       # GPU & hardware encoder detection
│           ├── network_view.py        # Detected IP & connected client tracker
│           └── settings_view.py       # Server configuration & worker limits
├── shared/
│   ├── protocol.md                    # REST & WebSocket protocol specification
│   └── schemas.py                     # Shared Pydantic data models
├── docs/
│   ├── architecture.md                # System architecture documentation
│   ├── benchmark_report.md            # Hardware benchmarks & speedup formulas
│   └── screenshots/                   # Application screenshots
└── scripts/
    ├── start_server.bat               # 1-click Windows server runner
    ├── start_client.bat               # 1-click Windows client runner
    ├── render_cli.py                  # Command-line rendering utility
    └── setup_installer.ps1            # Automated environment installer
```

---

## 🔌 Direct LAN Hardware Setup

To connect two machines directly using an Ethernet cable:
1. Connect a standard **RJ-45 Cat5e/Cat6 LAN cable** between the Client Laptop and Worker Server PC.
2. Launch `GPUWorkerServer.exe` on the Server PC.
3. Switch to the **Network** tab to view your detected IPv4 address (e.g. `192.168.100.12`).
4. On the Client Laptop, launch `GPURenderStudio.exe`, enter the Server IP in **Host & Settings**, and click **Test & Connect**.

---

## 📦 Installation & Setup

### Option 1: Standalone Pre-compiled Binaries (.exe)
Both applications are pre-compiled and available in `dist/`:
- **Worker Server:** Run `dist/GPUWorkerServer.exe` on your server PC.
- **Client Studio:** Run `dist/GPURenderStudio.exe` on your client laptop.

### Option 2: Running from Source (Python 3.11+)

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/qu-ddous/Distributed-Task-Offloading-Remote-GPU-Rendering-System.git
   cd Distributed-Task-Offloading-Remote-GPU-Rendering-System
   ```

2. **Server Installation (GPU Machine):**
   ```powershell
   python -m pip install -r server/requirements.txt
   python server_entrypoint.py
   ```

3. **Client Installation (Laptop):**
   ```powershell
   python -m pip install -r client/requirements.txt
   python client/app.py
   ```

---

## 🧪 Automated Testing

Run the test suite to verify checksumming, command generation, and endpoint contracts:
```powershell
python -m pytest -v
```

---

## 📄 License
This project is licensed under the terms of the [MIT License](LICENSE).

<img width="1920" height="1033" alt="rander 4" src="https://github.com/user-attachments/assets/028e1eca-f3c4-4c9e-8aa5-21ff96dc9539" />
<img width="1920" height="1030" alt="rander 5" src="https://github.com/user-attachments/assets/b1ba5806-bb20-47a0-860d-53236e06f91e" />
<img width="1920" height="1026" alt="rander 3" src="https://github.com/user-attachments/assets/f2dbfff9-5ddd-45ed-ad27-d4d3b715ecfa" />
<img width="1920" height="1030" alt="rander 2" src="https://github.com/user-attachments/assets/37f8d53c-66cc-44f2-9574-a1d68740d022" />
<img width="1920" height="1030" alt="rander 1" src="https://github.com/user-attachments/assets/b1ed1b4f-c303-4645-876d-4b9340391d4f" />
