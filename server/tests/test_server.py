import pytest
import io
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport

from server.app.main import app
from server.app.config import settings
from server.app.services.security import sanitize_filename, validate_path_safety
from server.app.services.ffmpeg_service import FFmpegService
from server.app.services.checksum_service import compute_file_sha256
from shared.schemas import PROTOCOL_VERSION

@pytest.mark.asyncio
async def test_ping_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["pong"] is True
        assert "timestamp" in data

@pytest.mark.asyncio
async def test_health_endpoint_auth_and_protocol():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Unauthorized without token
        unauth = await client.get("/api/v1/health")
        assert unauth.status_code == 401

        # Authorized with token
        headers = {"X-API-Token": settings.API_TOKEN}
        resp = await client.get("/api/v1/health", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["protocol_version"] == PROTOCOL_VERSION
        assert "ffmpeg" in data
        assert "hardware" in data
        assert "limits" in data

def test_security_filename_sanitization():
    # Traversal attempts
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\cmd.exe") == "cmd.exe"
    # Weird characters
    assert sanitize_filename("my video #1 (render).mp4") == "my_video__1__render_.mp4"
    # Hidden dot files
    assert sanitize_filename("...secret.mp4") == "secret.mp4"

def test_path_safety_validation(tmp_path):
    root = tmp_path / "storage"
    root.mkdir()
    safe_file = root / "video.mp4"
    unsafe_file = tmp_path / "outside.mp4"

    assert validate_path_safety(root, safe_file) is True
    assert validate_path_safety(root, unsafe_file) is False

def test_ffmpeg_command_construction():
    in_p = Path("input.mp4")
    out_p = Path("output.mp4")

    # 1. NVENC 1080p
    cmd_nvenc = FFmpegService.build_ffmpeg_command(
        input_path=in_p,
        output_path=out_p,
        resolution="1080p",
        bitrate="5M",
        preset="p4",
        use_nvenc=True
    )
    assert "-c:v" in cmd_nvenc
    assert "h264_nvenc" in cmd_nvenc
    assert "-vf" in cmd_nvenc
    assert "scale=-2:1080" in cmd_nvenc
    assert "-b:v" in cmd_nvenc
    assert "5M" in cmd_nvenc
    assert "-progress" in cmd_nvenc

    # 2. CPU fallback 720p
    cmd_cpu = FFmpegService.build_ffmpeg_command(
        input_path=in_p,
        output_path=out_p,
        resolution="720p",
        bitrate="2M",
        preset="p2",
        use_nvenc=False
    )
    assert "libx264" in cmd_cpu
    assert "scale=-2:720" in cmd_cpu
    assert "2M" in cmd_cpu

def test_ffmpeg_progress_parsing():
    line_time = "out_time_us=12500000"
    parsed_time = FFmpegService.parse_progress_line(line_time)
    assert parsed_time == {"out_time_us": "12500000"}
    secs = FFmpegService.parse_time_to_seconds(parsed_time["out_time_us"])
    assert secs == 12.5

    line_speed = "speed=2.5x"
    parsed_speed = FFmpegService.parse_progress_line(line_speed)
    assert parsed_speed == {"speed": "2.5x"}

    # HH:MM:SS.xx format
    clock_secs = FFmpegService.parse_time_to_seconds("00:01:30.50")
    assert clock_secs == 90.5

@pytest.mark.asyncio
async def test_job_upload_checksum_verification(tmp_path):
    transport = ASGITransport(app=app)
    headers = {"X-API-Token": settings.API_TOKEN}

    sample_content = b"Mock Video Data Stream 1234567890"
    correct_hash = hashlib.sha256(sample_content).hexdigest()
    wrong_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Attempt with incorrect hash -> Expect 400 Bad Request
        files = {"file": ("test.mp4", io.BytesIO(sample_content), "video/mp4")}
        data = {
            "checksum": wrong_hash,
            "resolution": "Original",
            "bitrate": "5M",
            "preset": "p4",
            "output_filename": "output.mp4",
            "allow_cpu_fallback": "true"
        }
        resp_bad = await client.post("/api/v1/jobs", headers=headers, files=files, data=data)
        assert resp_bad.status_code == 400
        assert "Integrity check failed" in resp_bad.json()["detail"]

        # 2. Attempt with correct hash -> Expect 201 Created
        files_good = {"file": ("test.mp4", io.BytesIO(sample_content), "video/mp4")}
        data_good = {
            "checksum": correct_hash,
            "resolution": "Original",
            "bitrate": "5M",
            "preset": "p4",
            "output_filename": "output.mp4",
            "allow_cpu_fallback": "true"
        }
        with patch("server.app.services.job_manager.job_manager.start_render_job"):
            resp_good = await client.post("/api/v1/jobs", headers=headers, files=files_good, data=data_good)
            assert resp_good.status_code == 201
            body = resp_good.json()
            assert "job_id" in body
            assert body["checksum"] == correct_hash
            assert body["file_size"] == len(sample_content)

def test_universal_hardware_telemetry():
    from server.app.services.system_service import SystemService
    telem = SystemService.get_hardware_telemetry()
    assert "hostname" in telem
    assert "cpu_cores" in telem
    assert telem["cpu_cores"] >= 1
    assert "gpu_detected" in telem
    assert "ram_total_gb" in telem
    assert telem["ram_total_gb"] > 0

def test_universal_lan_adapters_and_primary_ip():
    from server.app.services.system_service import SystemService
    ip = SystemService.get_primary_ip()
    assert isinstance(ip, str)
    assert len(ip.split(".")) == 4

    adapters = SystemService.get_all_lan_adapters()
    assert isinstance(adapters, list)
    for ad in adapters:
        assert "interface" in ad
        assert "ip" in ad
        assert "is_up" in ad
        assert "type" in ad

def test_multivendor_ffmpeg_command_construction():
    in_p = Path("input.mp4")
    out_p = Path("output.mp4")

    # 1. Intel QuickSync (QSV)
    cmd_qsv = FFmpegService.build_ffmpeg_command(
        input_path=in_p,
        output_path=out_p,
        encoder="h264_qsv"
    )
    assert "h264_qsv" in cmd_qsv

    # 2. AMD AMF
    cmd_amf = FFmpegService.build_ffmpeg_command(
        input_path=in_p,
        output_path=out_p,
        encoder="h264_amf"
    )
    assert "h264_amf" in cmd_amf

    # 3. Windows MediaFoundation
    cmd_mf = FFmpegService.build_ffmpeg_command(
        input_path=in_p,
        output_path=out_p,
        encoder="h264_mf"
    )
    assert "h264_mf" in cmd_mf

def test_ffmpeg_capabilities_validation():
    from server.app.services.system_service import SystemService
    avail, ver, is_hw, encoders = SystemService.check_ffmpeg_capabilities(force_refresh=True)
    if avail:
        assert isinstance(encoders, list)
        assert len(encoders) > 0
        # Verified encoders must include libx264
        assert "libx264" in encoders
        # If NVENC is not supported on host, it MUST NOT be in supported_encoders
        if not is_hw or "h264_nvenc" not in encoders:
            assert "h264_nvenc" not in encoders
