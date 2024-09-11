import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import project_router, tables_router, planning_router, analytics_router
from app.config import get_settings

log = logging.getLogger("uvicorn")


def create_application() -> FastAPI:
    application = FastAPI(title="BuildLogic API", debug=True)
    application.include_router(project_router, prefix="/project", tags=["project"])
    application.include_router(tables_router, prefix="/tables", tags=["tables"])
    application.include_router(planning_router, prefix="/planning", tags=["planning"])
    application.include_router(
        analytics_router, prefix="/analytics", tags=["analytics"]
    )

    application.mount(
        "/static", StaticFiles(directory=get_settings().static_dir), name="static"
    )

    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    log.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("Shutting down...")
