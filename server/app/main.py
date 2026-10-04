import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.app.api.health import router as health_router
from server.app.api.jobs import router as jobs_router
from server.app.api.websocket import router as ws_router
from server.app.config import settings
from shared.schemas import PROTOCOL_VERSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Distributed GPU Rendering Daemon (Protocol {PROTOCOL_VERSION})...")
    logger.info(f"Storage directory: {settings.storage_path}")
    yield
    logger.info("Shutting down Distributed GPU Rendering Daemon...")

app = FastAPI(
    title="Distributed Remote GPU Rendering Server",
    description="Headless FastAPI daemon for offloaded FFmpeg NVENC rendering.",
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

# Mount endpoints
app.include_router(health_router, prefix="/api/v1", tags=["Health & Capabilities"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(ws_router, prefix="/api/v1", tags=["WebSocket"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
