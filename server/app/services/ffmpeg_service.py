import re
import json
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from server.app.services.system_service import SystemService
from shared.schemas import ResolutionPreset, NvencPreset

class FFmpegService:
    @staticmethod
    def get_video_duration(file_path: Path) -> Optional[float]:
        """
        Uses ffprobe to extract total video duration in seconds.
        """
        ffprobe_bin = SystemService.get_ffprobe_path()
        if not ffprobe_bin:
            return None

        cmd = [
            ffprobe_bin,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip())
        except Exception:
            pass
        return None

    @staticmethod
    def build_ffmpeg_command(
        input_path: Path,
        output_path: Path,
        resolution: str = "Original",
        bitrate: str = "5M",
        preset: str = "p4",
        use_nvenc: bool = True
    ) -> List[str]:
        """
        Constructs safe FFmpeg command argument list.
        Never uses shell=True.
        """
        ffmpeg_bin = SystemService.get_ffmpeg_path() or "ffmpeg"
        cmd = [
            ffmpeg_bin,
            "-y",                     # Overwrite output without asking
            "-i", str(input_path)     # Input file
        ]

        # Resolution scaling filter
        scale_filter = None
        try:
            res_enum = ResolutionPreset(resolution)
            scale_filter = res_enum.scale_filter
        except Exception:
            if resolution == "720p":
                scale_filter = "scale=-2:720"
            elif resolution == "1080p":
                scale_filter = "scale=-2:1080"
            elif resolution == "1440p":
                scale_filter = "scale=-2:1440"
            elif resolution == "4K":
                scale_filter = "scale=-2:2160"

        if scale_filter:
            cmd.extend(["-vf", scale_filter])

        # Encoder selection
        if use_nvenc:
            cmd.extend(["-c:v", "h264_nvenc"])
            # Validate NVENC preset
            cmd.extend(["-preset", str(preset)])
        else:
            cmd.extend(["-c:v", "libx264"])
            # Map nvenc preset to cpu preset if needed
            cpu_preset = "medium"
            if preset in ["p1", "p2", "fast"]:
                cpu_preset = "fast"
            elif preset in ["p6", "p7", "slow"]:
                cpu_preset = "slow"
            cmd.extend(["-preset", cpu_preset])

        # Bitrate configuration
        cmd.extend([
            "-b:v", bitrate,
            "-maxrate", bitrate,
            "-bufsize", f"{int(bitrate.rstrip('MkK')) * 2}M" if bitrate.endswith('M') else bitrate
        ])

        # Audio copy or aac
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        # Progress reporting over pipe
        cmd.extend(["-progress", "pipe:1", "-nostats"])

        # Final output
        cmd.append(str(output_path))
        return cmd

    @staticmethod
    def parse_progress_line(line: str) -> Dict[str, str]:
        """
        Parses a key=value line from FFmpeg -progress pipe:1
        """
        parts = line.strip().split("=", 1)
        if len(parts) == 2:
            return {parts[0].strip(): parts[1].strip()}
        return {}

    @staticmethod
    def parse_time_to_seconds(time_str: str) -> float:
        """
        Parses HH:MM:SS.micro to total seconds, or microseconds integer from out_time_ms.
        """
        if not time_str or time_str == "N/A":
            return 0.0
        # If integer microseconds
        if time_str.isdigit():
            return int(time_str) / 1_000_000.0
        # If HH:MM:SS.xx
        match = re.match(r"(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)", time_str)
        if match:
            h = float(match.group(1) or 0)
            m = float(match.group(2))
            s = float(match.group(3))
            return h * 3600 + m * 60 + s
        return 0.0
