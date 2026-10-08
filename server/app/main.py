import sys
import io

# If running as windowed app (console=False in PyInstaller), sys.stdout/sys.stderr can be None.
# Fix 'NoneType' object has no attribute 'isatty' for uvicorn/logging.
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.app.api.health import router as health_router
from server.app.api.jobs import router as jobs_router
from server.app.api.websocket import router as ws_router
from server.app.config import settings
from shared.schemas import PROTOCOL_VERSION
from server.ui.log_bus import server_log_bus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
root_logger = logging.getLogger()
root_logger.addHandler(server_log_bus)
logger = logging.getLogger("server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Distributed GPU Rendering Daemon (Protocol {PROTOCOL_VERSION})...")
    logger.info(f"Storage directory: {settings.storage_path}")
    yield
    logger.info("Shutting down Distributed GPU Rendering Daemon...")

app = FastAPI(
    title="Distributed Remote GPU Rendering Server",
    description="FastAPI daemon for offloaded FFmpeg NVENC rendering.",
    version=PROTOCOL_VERSION,
    lifespan=lifespan
)

# Enable CORS for local network interfaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.requests import Request
from starlette.responses import Response
from server.app.services.connection_tracker import connection_tracker
from server.app.server_state import server_state

@app.middleware("http")
async def track_client_connections(request: Request, call_next):
    if not server_state.is_active:
        return Response(content="Server daemon is currently stopped / paused by administrator.", status_code=503)

    client_ip = request.client.host if request.client else "127.0.0.1"
    client_port = request.client.port if request.client else 0
    content_len = request.headers.get("content-length")
    bytes_in = int(content_len) if content_len and content_len.isdigit() else 0

    response = await call_next(request)

    resp_len = response.headers.get("content-length")
    bytes_out = int(resp_len) if resp_len and resp_len.isdigit() else 0

    connection_tracker.record_request(client_ip, client_port, bytes_in + bytes_out)
    return response

# Mount endpoints
app.include_router(health_router, prefix="/api/v1", tags=["Health & Capabilities"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(ws_router, prefix="/api/v1", tags=["WebSocket"])

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    import uvicorn
    import threading
    from server.ui.server_app import ServerApp

    # Configure Uvicorn server instance with log_config=None to prevent isatty crash
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

    logger.info(f"Worker Server daemon running on port {settings.PORT}")

    # Start Modern CustomTkinter Worker GUI
    try:
        gui_app = ServerApp(uvicorn_server_instance=server_instance)
        gui_app.mainloop()
    except Exception as e:
        logger.error(f"Error in Server GUI: {e}")
        server_instance.should_exit = True
        sys.exit(1)
