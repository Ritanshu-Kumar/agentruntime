from fastapi import FastAPI

from app.api.routes import router as runs_router
from app.config import get_settings
from app.logging_config import configure_logging

from app.api.health import router as health_router
from app.api.metrics import router as metrics_router
from app.api.dashboard import router as dashboard_router

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
)

app.include_router(runs_router)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(dashboard_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}