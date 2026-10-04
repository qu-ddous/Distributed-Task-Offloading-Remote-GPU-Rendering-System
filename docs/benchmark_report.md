# Performance Benchmarking: Remote GPU Offloading vs. Local Rendering

This document provides the standard evaluation methodology, formulas, and reporting templates for measuring the efficiency gains of offloading video rendering workloads from a thin client laptop to a dedicated GPU worker over a local network.

---

## 1. Mathematical Formulas & Metrics

To objectively evaluate whether remote offloading provides a net performance gain, use the following standardized formulas:

$$\text{Remote Total Time} = T_{\text{upload}} + T_{\text{remote\_render}} + T_{\text{download}}$$

$$\text{Network Overhead} = T_{\text{upload}} + T_{\text{download}}$$

$$\text{Speedup Factor} = \frac{T_{\text{local\_render}}}{\text{Remote Total Time}}$$

- **Speedup > 1.0x**: Offloading was beneficial (saved user time).
- **Speedup < 1.0x**: Local rendering was faster (network transfer penalty exceeded render time savings).
- **Network Overhead Ratio**: $\frac{\text{Network Overhead}}{\text{Remote Total Time}} \times 100\%$

> [!NOTE]
> For very small or short video clips (< 10 seconds / < 20MB), network transfer latency and handshake overhead may exceed the rendering duration, resulting in a speedup factor under 1.0x. For high-resolution, long-form, or complex video workloads (1080p / 4K / high bitrates), GPU NVENC typically achieves speedups between **3x and 10x**.

---

## 2. Experimental Setup & Hardware Specifications

*(Fill in your actual machine specifications before reporting real benchmark data. Do not fabricate specs.)*

| Property | Client Device (Laptop) | Worker Device (GPU Station) |
| :--- | :--- | :--- |
| **Model / Make** | *e.g., ThinkPad T14 / Dell XPS 13* | *e.g., Custom Desktop / Workstation* |
| **CPU** | *e.g., Intel Core i5-1135G7 (4C/8T)* | *e.g., AMD Ryzen 9 5900X (12C/24T)* |
| **RAM** | *e.g., 16 GB DDR4* | *e.g., 32 GB DDR4 / DDR5* |
| **GPU** | *Integrated (Intel Iris Xe)* | *Dedicated NVIDIA GeForce RTX 3080 10GB* |
| **Operating System** | *Windows 11 Home* | *Windows 11 Pro / Ubuntu 22.04 LTS* |
| **NVIDIA Driver** | *N/A* | *e.g., 551.86* |
| **FFmpeg Version** | *e.g., FFmpeg 6.1* | *e.g., FFmpeg 6.1 with nv-codec-headers* |
| **Network Type** | *Wi-Fi 6 (802.11ax) or 1 Gbps Ethernet*| *1 Gbps Cat6 Direct Ethernet* |

---

## 3. Benchmark Execution Procedure

Follow these steps for consistent, reproducible results:

1. **Prepare Standard Test Clips**:
   - **Test Case A (Small / 720p)**: 1-minute clip, ~50 MB, 1080p source -> 720p 2 Mbps output.
   - **Test Case B (Medium / 1080p)**: 5-minute clip, ~350 MB, 1080p source -> 1080p 5 Mbps output.
   - **Test Case C (Large / 4K/High Bitrate)**: 10-minute clip, ~1.5 GB, 4K source -> 1080p 8 Mbps output.
2. **Local Client Benchmark**:
   - Run local FFmpeg CPU render on client laptop:
     ```bash
     ffmpeg -i input.mp4 -vf scale=-2:1080 -c:v libx264 -preset medium -b:v 5M -c:a aac -b:a 192k local_output.mp4
     ```
   - Measure execution time ($T_{\text{local\_render}}$) using a stopwatch or `Measure-Command`.
3. **Remote Worker Offload Benchmark**:
   - Launch worker daemon and connect client desktop app.
   - Submit the exact same input file and settings.
   - Record upload duration ($T_{\text{upload}}$), remote GPU render duration ($T_{\text{remote\_render}}$), and download duration ($T_{\text{download}}$) reported in the client completion banner.
4. **Compute Metrics**:
   - Calculate Remote Total Time and Speedup Factor using the formulas above.

---

## 4. Benchmark Results Table (Template for Real Measurements)

*(Blank template to record real experiment results across test runs)*

| Test Case | Input Size | Target Config | Local CPU Time ($T_{\text{local}}$) | Upload Time ($T_{\text{up}}$) | Remote GPU Time ($T_{\text{render}}$) | Download Time ($T_{\text{dl}}$) | Remote Total Time | Speedup Factor | Net Gain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Case A (Small)** | ~50 MB | 720p @ 2M | ___ s | ___ s | ___ s | ___ s | ___ s | ___ x | ___ % |
| **Case B (Medium)**| ~350 MB | 1080p @ 5M | ___ s | ___ s | ___ s | ___ s | ___ s | ___ x | ___ % |
| **Case C (Large)** | ~1.5 GB | 1080p @ 8M | ___ s | ___ s | ___ s | ___ s | ___ s | ___ x | ___ % |

---

## 5. Hypothetical Reference Calculation (For Guidance Only)

*(The numbers below are illustrative examples demonstrating how formulas apply; replace with your measured physical data)*

- **Scenario**: 500 MB 4K gaming footage transcoded to 1080p 5M on a Gigabit LAN.
- $T_{\text{local\_render}}$ (Laptop Core i5 CPU): **240.0 seconds** (4 minutes).
- $T_{\text{upload}}$ (Gigabit LAN @ ~90 MB/s): **5.5 seconds**.
- $T_{\text{remote\_render}}$ (Desktop RTX 4070 NVENC): **22.0 seconds**.
- $T_{\text{download}}$ (Rendered 50 MB output @ ~90 MB/s): **0.6 seconds**.
- $\text{Remote Total Time} = 5.5 + 22.0 + 0.6 = \mathbf{28.1\text{ seconds}}$.
- $\text{Speedup Factor} = \frac{240.0}{28.1} = \mathbf{8.54\times}$.
- **Net Time Saved**: $240.0 - 28.1 = \mathbf{211.9\text{ seconds}}$ (~3.5 minutes saved on a single clip).
