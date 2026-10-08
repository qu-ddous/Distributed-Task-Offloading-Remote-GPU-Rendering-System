#!/usr/bin/env python3
"""
Command-Line Interface (CLI) Remote GPU Rendering Tool
Allows any 3rd-party application (Adobe Premiere Pro, DaVinci Resolve,
Blender, HandBrake, FFmpeg scripts) to trigger remote GPU rendering jobs
directly via command line or post-render script.
"""

import os
import sys
import time
import argparse
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from client.services.network_client import NetworkClient

def main():
    parser = argparse.ArgumentParser(description="Distributed GPU Rendering CLI Client for 3rd-Party Editors")
    parser.add_argument("input_file", help="Path to input video file to render on remote GPU")
    parser.add_argument("--host", default="127.0.0.1", help="Worker server IP address")
    parser.add_argument("--port", type=int, default=8000, help="Worker server port (default: 8000)")
    parser.add_argument("--token", default="supersecret-render-token-change-me", help="API authentication token")
    parser.add_argument("--res", default="Original", choices=["Original", "720p", "1080p", "1440p", "4K"], help="Target resolution")
    parser.add_argument("--bitrate", default="5M", help="Target bitrate (e.g. 5M, 8M, 12M)")
    parser.add_argument("--preset", default="p4", help="NVENC preset (p1-p7, fast, medium, slow)")
    parser.add_argument("--output", default=None, help="Output destination file path")
    parser.add_argument("--cpu-fallback", action="store_true", default=True, help="Allow CPU encoding fallback if GPU absent")

    args = parser.parse_args()
    input_path = Path(args.input_file).resolve()
    if not input_path.exists():
        print(f"[Error] File not found: {input_path}")
        sys.exit(1)

    out_name = args.output or f"{input_path.stem}_remote_{args.res}{input_path.suffix or '.mp4'}"
    out_path = Path(out_name).resolve()

    print("=" * 65)
    print("   DISTRIBUTED GPU REMOTE RENDERING CLI (3RD-PARTY INTEGRATION)")
    print("=" * 65)
    print(f" Input File:   {input_path.name} ({input_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f" Target Node:  http://{args.host}:{args.port}")
    print(f" Resolution:   {args.res} | Bitrate: {args.bitrate}")
    print("=" * 65)

    net = NetworkClient(args.host, args.port, args.token)

    # 1. Health check
    print("[1/4] Connecting to worker node...")
    health = net.ping_and_health()
    if not health.get("success"):
        print(f"[Error] Could not connect to worker at {args.host}:{args.port}: {health.get('error')}")
        sys.exit(1)

    hw = health.get("data", {}).get("hardware", {})
    ff = health.get("data", {}).get("ffmpeg", {})
    print(f"  -> Connected to node: {hw.get('hostname')} ({hw.get('os_platform')})")
    print(f"  -> Hardware: {hw.get('cpu_model')} ({hw.get('cpu_cores')} cores)")
    print(f"  -> GPU Mode: {'NVENC Ready (' + str(hw.get('gpu_name')) + ')' if ff.get('nvenc_available') else 'CPU Fallback (libx264)'}")

    # 2. Hashing
    print("[2/4] Computing SHA-256 cryptographic checksum...")
    checksum = net.compute_sha256(input_path)
    print(f"  -> SHA-256: {checksum[:16]}...{checksum[-8:]}")

    # 3. Upload & Submit
    print("[3/4] Offloading video to remote GPU worker...")
    def on_prog(sent, total):
        pct = (sent / total) * 100.0 if total > 0 else 0
        sys.stdout.write(f"\r  -> Uploading: {pct:.1f}% ({sent/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)")
        sys.stdout.flush()

    res = net.submit_job(
        input_file=input_path,
        checksum=checksum,
        resolution=args.res,
        bitrate=args.bitrate,
        preset=args.preset,
        output_filename=out_path.name,
        allow_cpu_fallback=args.cpu_fallback,
        progress_callback=on_prog
    )
    print()

    if not res.get("success"):
        print(f"[Error] Job submission failed: {res.get('error')}")
        sys.exit(1)

    job_id = res["job"]["job_id"]
    print(f"  -> Job accepted! Active Job ID: {job_id}")

    # 4. Stream live render progress
    print("[4/4] Encoding on remote worker node...")
    ws_stop = asyncio.Event()
    render_summary = {"status": "unknown"}

    def on_ws(msg):
        mtype = msg.get("type")
        if mtype == "progress":
            pct = msg.get("percent", 0.0)
            elapsed = msg.get("elapsed_seconds", 0.0)
            fps = msg.get("fps", 0)
            telem = msg.get("server_telemetry") or {}
            c_pct = telem.get("cpu_percent", 0)
            r_gb = telem.get("ram_used_gb", 0)
            sys.stdout.write(f"\r  -> Rendering: {pct:.1f}% | Elapsed: {elapsed:.0f}s | FPS: {fps or 0:.0f} | Remote CPU: {c_pct:.0f}% | Remote RAM: {r_gb:.1f}GB")
            sys.stdout.flush()
        elif mtype == "state":
            st = msg.get("status")
            if st == "completed":
                render_summary["status"] = "completed"
                render_summary["output_checksum"] = msg.get("output_checksum")
                ws_stop.set()
            elif st in ["failed", "cancelled"]:
                render_summary["status"] = st
                render_summary["error"] = msg.get("message")
                ws_stop.set()

    def ws_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(net.listen_websocket(job_id, on_ws, ws_stop))
        loop.close()

    import threading
    t = threading.Thread(target=ws_loop, daemon=True)
    t.start()

    while not ws_stop.is_set():
        time.sleep(0.5)
    print()

    if render_summary.get("status") != "completed":
        print(f"[Error] Remote rendering failed: {render_summary.get('error')}")
        sys.exit(1)

    # 5. Download rendered file
    print(" Downloading finished render...")
    dl = net.download_rendered_file(job_id, out_path.parent, out_path.name, render_summary.get("output_checksum"))
    if dl.get("success"):
        print(f"✔ Success! Render saved to: {out_path}")
        sys.exit(0)
    else:
        print(f"[Error] Download failed: {dl.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()

