from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from structlog import get_logger

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import HabeshaBetError
from app.core.logging import setup_logging
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from app.core.security_middleware import CSRFMiddleware, ConnectionThrottleMiddleware, ReplayAttackPreventionMiddleware, SecurityHeadersMiddleware
from app.services.background_workers import (
    AuditArchivingWorker,
    CleanupWorker,
    GameSchedulerWorker,
    HealthMonitorWorker,
    LeaderboardRefreshWorker,
    NotificationWorker,
    ReminderWorker,
    RetryQueueWorker,
    StatisticsAggregationWorker,
)
from app.websocket.channels import ws_manager

logger = get_logger(__name__)


def get_db_session():
    from app.core.database import async_session_maker
    return async_session_maker


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan events."""
    logger.info("application_starting", app_name=settings.APP_NAME, version=settings.APP_VERSION)
    setup_logging()
    db_factory = get_db_session()
    workers = [
        ws_manager,
        NotificationWorker(db_factory),
        ReminderWorker(db_factory),
        GameSchedulerWorker(db_factory),
        CleanupWorker(db_factory),
        LeaderboardRefreshWorker(db_factory),
        StatisticsAggregationWorker(db_factory),
        AuditArchivingWorker(db_factory),
        RetryQueueWorker(db_factory),
        HealthMonitorWorker(db_factory, ws_manager),
    ]
    for worker in workers:
        if hasattr(worker, "start"):
            await worker.start()
    yield
    for worker in reversed(workers):
        if hasattr(worker, "stop"):
            await worker.stop()
    logger.info("application_stopping")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(ReplayAttackPreventionMiddleware)
app.add_middleware(ConnectionThrottleMiddleware, max_connections_per_ip=100, window=60)
app.add_middleware(RateLimitMiddleware, rate_limit=120 if settings.DEBUG else 60)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(HabeshaBetError)
async def habeshabet_exception_handler(request: Request, exc: HabeshaBetError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(
        "handled_exception",
        request_id=request_id,
        path=request.url.path,
        error=exc.message,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.exception("unhandled_exception", request_id=request_id, path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "InternalServerError",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            }
        },
    )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness() -> JSONResponse:
    from app.core.database import engine
    from sqlalchemy import text

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return JSONResponse(content={"status": "ready"})
    except Exception as exc:
        logger.error("readiness_check_failed", error=str(exc))
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "not_ready"})


@app.get("/health/live", tags=["health"])
async def liveness() -> JSONResponse:
    return JSONResponse(content={"status": "alive"})


@app.websocket("/ws")
async def ws_root(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"event": "welcome", "data": {"message": "Connect to /ws?token=..."}})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
