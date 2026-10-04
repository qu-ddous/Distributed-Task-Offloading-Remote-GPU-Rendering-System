# Distributed Remote GPU Rendering System: Communication Protocol

## Protocol Version
Current specification version: `v1.0.0`

All endpoints and WebSocket handshakes enforce compatibility checking against this major protocol version (`v1.x.y`).

---

## 1. Authentication & Security
- **Header:** `X-API-Token: <token>`
- **WebSocket Query Param:** `?token=<token>` or initial authentication frame.
- Intended for trusted local area networks (LAN / WLAN).

---

## 2. REST Endpoints

### 2.1 Handshake / Health & Capabilities
- **Method:** `GET /api/v1/health`
- **Headers:** `X-API-Token: <token>`
- **Response `200 OK`:**
```json
{
  "status": "online",
  "protocol_version": "v1.0.0",
  "server_time": "2026-10-04T22:50:00Z",
  "ffmpeg": {
    "available": true,
    "version": "6.1.1-full_build",
    "nvenc_available": true,
    "supported_encoders": ["h264_nvenc", "hevc_nvenc", "libx264"]
  },
  "hardware": {
    "gpu_detected": true,
    "gpu_name": "NVIDIA GeForce RTX 4070 Laptop GPU",
    "cpu_cores": 16,
    "disk_free_bytes": 107374182400
  },
  "limits": {
    "max_upload_size_bytes": 2147483648,
    "max_concurrent_jobs": 1,
    "active_jobs": 0
  }
}
```

### 2.2 Latency Ping
- **Method:** `GET /api/v1/ping`
- **Response `200 OK`:**
```json
{
  "pong": true,
  "timestamp": 1728075000.123
}
```

### 2.3 Job Creation & Video Upload
- **Method:** `POST /api/v1/jobs`
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Video binary stream
  - `checksum`: Client SHA-256 hex string of the original video
  - `resolution`: `Original` | `720p` | `1080p`
  - `bitrate`: e.g. `2M` | `5M` | `8M` | `12M`
  - `preset`: `p1` ... `p7` or `fast` | `medium` | `slow`
  - `output_filename`: e.g. `my_render_1080p.mp4`
  - `allow_cpu_fallback`: `true` | `false` (explicit fallback)
- **Response `201 Created`:**
```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "queued",
  "created_at": "2026-10-04T22:50:10Z",
  "input_filename": "source.mp4",
  "output_filename": "my_render_1080p.mp4",
  "file_size": 15420340,
  "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```
- **Error `400 Bad Request`:** Checksum mismatch, invalid resolution, or unsupported settings.
- **Error `413 Payload Too Large`:** File exceeds `max_upload_size_bytes`.
- **Error `503 Service Unavailable`:** Server queue capacity exceeded.

### 2.4 Job Status Query
- **Method:** `GET /api/v1/jobs/{job_id}`
- **Response `200 OK`:**
```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "rendering", 
  "progress_percent": 45.2,
  "elapsed_seconds": 12.4,
  "eta_seconds": 15.0,
  "speed": "2.4x",
  "current_fps": 142.5,
  "output_ready": false,
  "output_size_bytes": 0,
  "output_checksum": null,
  "error_message": null
}
```
*Valid Status Values:* `queued`, `rendering`, `completed`, `failed`, `cancelled`.

### 2.5 Cancel Job
- **Method:** `POST /api/v1/jobs/{job_id}/cancel`
- **Response `200 OK`:**
```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "cancelled",
  "message": "Render process safely terminated."
}
```

### 2.6 Download Rendered Video
- **Method:** `GET /api/v1/jobs/{job_id}/download`
- **Response Headers:**
  - `Content-Disposition: attachment; filename="my_render_1080p.mp4"`
  - `X-Checksum-SHA256: <output_sha256_hex>`
  - `Content-Length: <bytes>`
- **Response Body:** Binary stream.

---

## 3. WebSocket Real-Time Progress & Logs
- **Endpoint:** `ws://<host>:<port>/api/v1/ws/{job_id}?token=<token>`

### Server -> Client Stream Frames (JSON)

#### Progress Message:
```json
{
  "type": "progress",
  "job_id": "job_a1b2c3d4e5f6",
  "status": "rendering",
  "percent": 54.8,
  "elapsed_seconds": 14.2,
  "eta_seconds": 11.5,
  "fps": 138.2,
  "speed": "2.35x"
}
```

#### Log Message:
```json
{
  "type": "log",
  "job_id": "job_a1b2c3d4e5f6",
  "level": "INFO",
  "message": "frame= 1240 fps=142 q=24.0 size= 8192kB time=00:00:41.20 bitrate=1628.4kbits/s speed=2.36x"
}
```

#### State Transition Message:
```json
{
  "type": "state",
  "job_id": "job_a1b2c3d4e5f6",
  "status": "completed",
  "output_checksum": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "output_size_bytes": 10485760,
  "total_render_seconds": 22.8
}
```

#### Error Message:
```json
{
  "type": "error",
  "job_id": "job_a1b2c3d4e5f6",
  "status": "failed",
  "error": "NVENC initialization failed: Driver version too low or device busy."
}
```
