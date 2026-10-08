@echo off
REM ========================================================================
REM Distributed Remote GPU Render Launcher for 3rd-Party Applications
REM Works with Adobe Premiere Pro, DaVinci Resolve, Blender, HandBrake, etc.
REM Usage: render_remote.bat "C:\path\to\video.mp4" [Options]
REM ========================================================================

python "%~dp0render_cli.py" %*

