"""
LabhArth AI — FastAPI Application Entry Point
=================================================
Main application factory with middleware, CORS, and route registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    chat_router,
    eligibility_router,
    health_router,
    schemes_router,
)
from backend.utils.config import get_settings
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    logger.info(f"🚀 Starting {settings.app_name} v0.1.0 [{settings.app_env}]")

    # Startup: initialize connections
    # TODO: Uncomment when database is configured
    # from backend.database.connection import init_db
    # await init_db()
    # logger.info("Database initialized")

    yield

    # Shutdown: close connections
    # TODO: Uncomment when database is configured
    # from backend.database.connection import close_db
    # await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Agentic RAG platform helping Indian citizens discover "
            "government welfare schemes, determine eligibility, and "
            "receive application guidance."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- CORS Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Register Routes ---
    api_prefix = "/api/v1"
    app.include_router(health_router, prefix=api_prefix, tags=["Health"])
    app.include_router(schemes_router, prefix=api_prefix)
    app.include_router(eligibility_router, prefix=api_prefix)
    app.include_router(chat_router, prefix=api_prefix)

    logger.info(f"Routes registered under {api_prefix}")
    return app


# Application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=not settings.is_production,
    )
