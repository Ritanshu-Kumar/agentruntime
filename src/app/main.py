from fastapi import FastAPI

from app.api.routes import router as runs_router
from app.config import get_settings
from app.logging_config import configure_logging


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
)

app.include_router(runs_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}