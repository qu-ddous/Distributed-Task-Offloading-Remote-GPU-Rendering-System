import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from server.app.services.job_manager import job_manager
from server.app.config import settings

logger = logging.getLogger("websocket")
router = APIRouter()

@router.websocket("/ws/{job_id}")
async def websocket_job_stream(websocket: WebSocket, job_id: str, token: str = Query(None)):
    if settings.API_TOKEN and token != settings.API_TOKEN:
        await websocket.close(code=4001, reason="Unauthorized: Invalid token")
        return

    job = job_manager.get_job(job_id)
    if not job:
        await websocket.close(code=4004, reason="Job not found")
        return

    await websocket.accept()
    await job_manager.subscribe(job_id, websocket)

    # Send initial snapshot
    await websocket.send_json({
        "type": "state",
        "job_id": job.job_id,
        "status": job.status,
        "percent": job.progress_percent,
        "elapsed_seconds": job.elapsed_seconds,
        "output_checksum": job.output_checksum,
        "error": job.error_message
    })

    try:
        while True:
            # Keep alive and listen for client messages (e.g. ping)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await job_manager.unsubscribe(job_id, websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        await job_manager.unsubscribe(job_id, websocket)
