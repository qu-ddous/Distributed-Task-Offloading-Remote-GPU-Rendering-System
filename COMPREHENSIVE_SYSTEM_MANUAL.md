# Distributed Task Offloading & Remote GPU Rendering System
## Comprehensive System Architecture & Professional User Manual

---

## 1. Executive Summary & Core Philosophy

The **Distributed Task Offloading & Remote GPU Rendering System** is an enterprise-grade, high-performance distributed computing suite engineered to offload computationally intensive workloads (such as 4K video transcoding, 3D rendering, and AI/Machine Learning model execution) from a lightweight client machine (e.g., an everyday laptop) to a dedicated worker server PC over a local area network (LAN).

### Core Architectural Pillars
1. **0% Client Laptop Load**: All processor-heavy, memory-heavy, and GPU-intensive jobs run entirely on the Server PC. The client laptop functions strictly as a thin-client control terminal, consuming minimal battery and generating zero fan noise or thermal throttling.
2. **Deterministic Wire-Speed LAN Connection**: Optimized for direct Ethernet (LAN cable) links (1 Gbps – 2.5 Gbps) with sub-millisecond round-trip latency (~0.3 ms – 0.8 ms). No internet connectivity is required.
3. **Cryptographic Integrity**: Every job transfer is protected by pre-flight and post-flight SHA-256 cryptographic hashing to guarantee zero data corruption during transfer.
4. **Universal Compute Pipeline**: Beyond video transcoding, the system natively supports executing Python scripts (`.py`), AI model training routines, and system shell scripts (`.bat`, `.cmd`, `.ps1`) on the server's compute hardware with real-time stdout/stderr streaming over WebSockets.

---

## 2. Hardware Setup & Direct LAN Cable Configuration

### Physical Connection
1. Take a standard **RJ-45 Ethernet Cable** (Cat5e, Cat6, or Cat6a).
2. Plug one end into your **Client Laptop's** Ethernet port.
3. Plug the other end into your **Server PC's** Ethernet port.
*(If either computer lacks a built-in Ethernet jack, a USB-to-Ethernet adapter works at full Gigabit speed).*

```
+---------------------------+                     +---------------------------+
|       CLIENT LAPTOP       |  Cat6 LAN Cable     |      SERVER WORKER PC     |
|   (GPURenderStudio.exe)   |<===================>|   (GPUWorkerServer.exe)   |
|   Thin Control Terminal   |   1 Gbps (~0.5 ms)  |   Dedicated GPU / Compute |
|      [0% Heavy Load]      |                     |      [100% Workload]      |
+---------------------------+                     +---------------------------+
```

### IP Auto-Detection & Verification
1. Both Windows machines will automatically detect the local network connection.
2. On the **Server PC**, launch `GPUWorkerServer.exe`.
3. Open the **Network** tab in the Server UI.
4. In the **Detected Worker IP** card, the server will display its local IPv4 address (for example: `192.168.100.12` or `192.168.1.15`).
5. Click the **📋 Copy IP** button.
6. On the **Client Laptop**, launch `GPURenderStudio.exe`, navigate to **Host & Settings**, paste this IP address into the **Worker IPv4 Address** field, and click **🔄 Test & Connect**.

---

## 3. Server Application Manual (`GPUWorkerServer.exe`)

The Server application acts as an autonomous background daemon (powered by FastAPI and Uvicorn) integrated with a modern GUI built on CustomTkinter.

```
+---------------------------------------------------------------------------------------+
|  [WORKER SERVER] GPU Render Stream Studio • Worker Server (v1.0.0)           [Stop]   |
+-------------------+-------------------------------------------------------------------+
|  📊 Overview      |  🖥️ Hostname: WORKER-NODE-01     ⚡ Cores: 8 (16 Threads)         |
|  📑 Render Queue  |  🧠 RAM: 15.8 GB Total             🌐 Worker IP: 192.168.100.12    |
|  📋 Activity Logs |-------------------------------------------------------------------|
|  🎮 GPU & Engine  |  [Live Telemetry]  CPU Load: 4.2%  |  RAM Usage: 3.8 / 15.8 GB    |
|  🌐 Network       |-------------------------------------------------------------------|
|  ⚙️ Settings      |  [Transcode Activity]  Status: Idle (Ready for Client Tasks)      |
+-------------------+-------------------------------------------------------------------+
```

### Screen 1: Overview (Dashboard)
* **Hardware Pre-Seeding (Frame 0)**: Upon launching the server executable, all physical hardware specifications (`CPU Model`, `Physical/Logical Cores`, `Total Installed RAM`, `Operating System`, and `LAN IP`) are instantly queried and rendered without delay.
* **Live System Telemetry**: Displays real-time CPU utilization, RAM usage, and transcode engine readiness. Refreshes every 1500 ms while idle, accelerating to 500 ms when jobs are actively running.
* **Active Transcode Status Card**: Monitors active worker tasks, encoding presets, and live stream speeds.
* **Mini Activity Console**: Displays recent daemon initialization events and incoming client connection messages.

### Screen 2: Render Queue
* **Header Metric Cards**:
  * **Total Jobs**: Cumulative number of submitted jobs in the session.
  * **Processing**: Current active jobs in progress.
  * **Completed**: Successfully rendered or executed jobs.
  * **Failed**: Jobs halted by user cancellation or syntax/codec error.
* **Interactive Filter & Search**: Search bar filters jobs in real-time by input filename, client IP address, or unique UUID. Dropdown filters jobs by status (`All Status`, `Processing`, `Completed`, `Queued`, `Failed`).
* **Interactive Job Rows**: Shows item number, filename, client IP, status pill, real-time progress bar (updated every 500 ms), elapsed execution duration, and a thread-safe **✕ Cancel** button.

### Screen 3: Activity Logs
* **Real-time Event Logging**: Connected to the central `server_log_bus` with zero mock data.
* **Level Counter Pills**: Filter by category (`All`, `Info`, `Success`, `Warning`, `Error`) with live event counters on each pill.
* **Live Search**: Filters log records instantly by timestamp, level, or message text.
* **Trash / Clear**: Empties memory log cache with one click.

### Screen 4: GPU & Engine
* **Dynamic Hardware Detection**:
  * **NVIDIA GPU Mode**: If a supported NVIDIA card is detected, displays the exact GPU model (e.g., RTX 4070 / RTX 3060), total VRAM, driver version, CUDA core status, and hardware NVENC capabilities.
  * **CPU Transcode Mode**: If running on integrated graphics or non-NVIDIA hardware, dynamically adapts to show CPU Transcode Node status, processor model, available shared system RAM, and software encoding (`libx264`) status. Zero hardcoded placeholder numbers.
* **Engine Profiles**: Lists available video encoders (`h264_nvenc`, `hevc_nvenc`, `libx264`, `libx265`, `aac`) and verified FFmpeg build paths.

### Screen 5: Network
* **Daemon Status Card**: Shows listening status on port `8000` (TCP).
* **Detected Worker IP**: Shows auto-detected primary LAN IPv4 address with a **📋 Copy IP** button for quick clipboard copying.
* **Active Client Sessions Counter**: Strictly counts authorized active client connections. When clients disconnect, drops immediately to `0 Clients • Awaiting client connection`.
* **Throughput Wave Sparklines**: Displays live requests rate and LAN data transfer throughput (KB/s / MB/s) calculated from session byte deltas.
* **Live Client Connections Table**: Lists client IP, port, live status (`Active` vs `Idle`), last activity timestamp, and total data transferred.
* **Clear History Button**: Resets previous connection history instantly.

### Screen 6: Settings
* **Startup Behavior**: Switches to configure Windows startup behavior, tray minimization, and network auto-reconnect.
* **Concurrency Limits**: Option menu to configure maximum concurrent rendering jobs (1 to 4).
* **Storage & Cache Folders**: Set custom directories for `Output folder` and `Temp cache folder`, with an automatic cache cleanup switch.
* **Default Encoding Presets**: Configure default fallback resolution, video target bitrate, and encoder presets.

---

## 4. Client Application Manual (`GPURenderStudio.exe`)

The Client Studio application is the user's primary workstation interface.

```
+---------------------------------------------------------------------------------------+
|  [CLAY STUDIO] GPU Stream • Task Offloading Studio        ● Worker Online | Lat: 0.4ms|
+-------------------+-------------------------------------------------------------------+
|  📊 Dashboard     |  Task Profile:  [🎬 Video Transcode] [🧠 Python / AI] [⚡ Batch]   |
|  🚀 Create Job    |-------------------------------------------------------------------|
|  📡 Live Monitor  |  1. Select File to Offload:   [ 📁 Browse Video / Python Script ] |
|  ⚡ Benchmarks    |  2. Execution Profile:        [ Auto-Detect CUDA / Multi-Thread ] |
|  ⚙️ Host & Settings|  3. Output Destination:       [ C:\Users\...\Downloads\Output   ] |
|                   |-------------------------------------------------------------------|
|  [ Engine Ready ] |  [ 🚀 Submit & Run / Train on Server Hardware (0% Laptop Load) ]  |
+-------------------+-------------------------------------------------------------------+
```

### Screen 1: Host Connection & Settings
* **Worker IPv4 Address**: Enter the server machine's IP address (e.g., `192.168.100.12`).
* **Port**: Default is `8000`.
* **Shared API Secret Token**: Pre-configured security token ensuring only authorized clients can submit jobs to the worker daemon.
* **Control Buttons**:
  * **🔄 Test & Connect**: Initiates handshake with the server. On success, updates badge to green `✔ Connected` and starts lightweight heartbeat tracking.
  * **🔌 Disconnect**: Immediately severs connection, stops all background pings, and informs server to release the session.
  * **🗑️ Reset Connection**: Restores default network parameters.

### Screen 2: Dashboard Overview
* **Connection Status Card**: Displays live connection status, worker IP/port, and ping latency in milliseconds.
* **Remote Hardware Readiness**: Shows remote GPU model, available VRAM, total RAM, and transcode capabilities.
* **Quick Task Launcher**: Direct shortcuts to launch Video Transcoding, AI execution, or Performance Benchmarks.

### Screen 3: Create New Task (`New Render Job`)
Features a 3-way **Task Profile Selector**:

#### Profile A: 🎬 Video Transcode (GPU NVENC)
1. Click **📁 Browse Video File...** to select any video (`.mp4`, `.mkv`, `.mov`, `.avi`, `.wmv`, `.flv`, `.ts`).
2. Client background thread calculates the cryptographic **SHA-256 Checksum** of the file.
3. Configure Transcode Settings:
   * **Resolution Preset**: `Original`, `720p`, `1080p`, `1440p`, `4K`.
   * **Target Bitrate**: `2M`, `5M`, `8M`, `12M`, `20M`.
   * **NVENC Preset**: `p1 (Fastest)` to `p7 (Slowest)`.
   * **CPU Fallback**: Checkbox to allow `libx264` CPU encoding if GPU is busy or unavailable.
4. Set destination directory and click **🚀 Submit & Render on Remote GPU**.

#### Profile B: 🧠 Python Script / AI Model (100% Server Compute)
1. Click **🐍 Browse Python (.py)...** to select any script (`.py`, `.pyw`, `.ipynb`).
2. UI automatically switches to compute mode:
   * **Execution Acceleration Profile**: `Auto-Detect (CUDA GPU / PyTorch)`, `Dedicated NVIDIA GPU Preferred`, or `Server Multi-Core CPU High-Performance`.
   * **Output Artifact Delivery**: `Capture Live Execution Log & Output Files` or `Standard Script Output Stream`.
3. Output filename automatically formats to `{script_name}_execution.log`.
4. Click **🧠 Submit & Run / Train on Server Hardware**.

#### Profile C: ⚡ Batch / Shell Script
1. Click **📜 Browse Script (.bat/.ps1)...** to select `.bat`, `.cmd`, or `.ps1` files.
2. Shell host automatically targets server environment (`cmd.exe` or `powershell.exe`).
3. Click **⚡ Submit & Execute Script on Server**.

### Screen 4: Live Telemetry & Monitor (`Active Job`)
When a job is submitted, the application transitions automatically to the Live Monitor screen:
* **Stage 1 (Upload)**: Streams the file to the server over LAN with a live progress bar and MB transfer count.
* **Stage 2 (Remote Execution)**:
  * Server processes the job using 100% server hardware.
  * **Live Output Stream**: For video, displays frame progress, FPS, speed multiplier, and ETA. For Python/AI, displays real-time `print()` statements, epoch numbers, loss metrics, and stdout/stderr lines via WebSocket.
  * **Remote Server Telemetry**: Displays real-time Server CPU utilization percentage bar and Server RAM usage (e.g., `4.2 / 16.0 GB`).
* **Stage 3 (Download & Verification)**: The completed output video, model artifact, or execution log is downloaded to the client laptop's download folder. The client verifies the SHA-256 hash against the server's output checksum.

### Screen 5: Performance & Benchmark Suite
* **▶ Run Live Hardware Benchmark**: Triggers an automated 5-step hardware stress test measuring:
  1. Integer & Floating Point Processing (GFLOPS)
  2. Memory Bandwidth Throughput (GB/s)
  3. Video Codec Transcode Efficiency (FPS)
  4. Network Transmission Bandwidth (MB/s)
  5. Cryptographic SHA-256 Hashing Speed (MB/s)
* **Real Production History**: Directly imports verified metrics from completed rendering and compute jobs (duration, resolution, throughput, and compute ratio) with zero dummy data.

---

## 5. Step-by-Step Practical Workflows

### Scenario 1: Offloading a 4K Video Transcode
1. **On Server PC**: Start `GPUWorkerServer.exe`. Note the IP (e.g., `192.168.100.12`).
2. **On Laptop**: Start `GPURenderStudio.exe`. Go to **Host & Settings**, enter `192.168.100.12`, click **Test & Connect**.
3. Go to **Create Job**, keep profile on **🎬 Video Transcode**.
4. Browse and select your 4K video file.
5. Choose resolution (e.g., `1080p`) and bitrate (e.g., `8M`).
6. Click **🚀 Submit & Render on Remote GPU**.
7. Watch the Live Monitor as the server encodes at high speed. When complete, the finished 1080p video downloads directly to your laptop.

### Scenario 2: Training a Python AI/ML Model on the Server PC
1. Write your training code in a file called `train_model.py` on your laptop (e.g., using PyTorch, TensorFlow, or Scikit-Learn).
2. In `GPURenderStudio.exe`, go to **Create Job** and click the **🧠 Python / AI Model** tab.
3. Browse and select `train_model.py`.
4. Choose **Auto-Detect (CUDA GPU / PyTorch)**.
5. Click **🧠 Submit & Run / Train on Server Hardware**.
6. The file is uploaded to the server PC. The server executes `python -u train_model.py` using its own GPU/CPU and RAM.
7. You will see every training epoch, loss value, and accuracy metric appear live in the **Console Logs** box on your laptop.
8. When training completes, the model weights and execution log are automatically downloaded back to your laptop.

---

## 6. Security, Integrity & Best Practices

1. **Firewall Settings**: Ensure Windows Firewall permits incoming TCP connections on Port `8000` on the Server PC.
2. **API Token Consistency**: The secret token in `GPURenderStudio` (`Settings`) must match the `API_TOKEN` configured on the worker server (default: `supersecret-render-token-change-me`).
3. **LAN Static IP Assignment**: For a permanent direct Ethernet setup between two PCs without a home router, assign static IPs:
   * **Server PC**: IP `192.168.1.10`, Subnet Mask `255.255.255.0`
   * **Client Laptop**: IP `192.168.1.11`, Subnet Mask `255.255.255.0`
4. **Zero Ghost Connections**: The client only communicates with the server when you explicitly click **Test & Connect** or submit a job. Disconnecting in the client immediately clears the active session on the server.

