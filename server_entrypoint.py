"""
GPU Worker Server Application Entrypoint
Hosts the FastAPI daemon on port 8000 alongside the modern CustomTkinter Studio GUI.
"""
import sys
import io
import os
import multiprocessing
import threading
import logging
from pathlib import Path

# Ensure root repository directory is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Fix 'NoneType' object has no attribute 'isatty' when packaged without console
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

def main():
    multiprocessing.freeze_support()
    import uvicorn
    from server.app.main import app
    from server.app.config import settings
    from server.ui.server_app import ServerApp

    # Configure Uvicorn server instance
    config = uvicorn.Config(
        app=app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        log_config=None,
        reload=False
    )
    server_instance = uvicorn.Server(config)

    # Start FastAPI daemon in dedicated background thread
    server_thread = threading.Thread(target=server_instance.run, daemon=True)
    server_thread.start()

    # Start Modern CustomTkinter Worker GUI
    gui_app = ServerApp(uvicorn_server_instance=server_instance)
    gui_app.mainloop()

if __name__ == "__main__":
    main()
