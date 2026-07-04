"""
LabhArth AI — FastAPI Application Entry Point
=================================================
Main application factory with middleware, CORS, and route registration.
"""

import sys
import asyncio

if sys.platform == "win32":
    # Force ProactorEventLoop on Windows to support subprocess stdio communication (MCP server)
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    chat_router,
    eligibility_router,
    health_router,
    schemes_router,
    search_router,
)
from backend.utils.config import get_settings
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    logger.info(f"🚀 Starting {settings.app_name} v0.1.0 [{settings.app_env}]")

    # Startup: initialize connections
    from backend.database.connection import init_db
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Spawning local MCP Server stdio client and session
    import sys
    import os
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from backend.agents.mcp_client_helper import register_mcp_client_session

    python_exe = sys.executable or "python"
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONUNBUFFERED"] = "1"
    
    server_params = StdioServerParameters(
        command=python_exe,
        args=["-u", "-m", "backend.mcp.server"],
        env=subprocess_env
    )

    logger.info(f"Spawning local MCP server via stdio transport: {python_exe} -m backend.mcp.server")

    # Keep stdio_client context active for app lifecycle
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                logger.info("Initializing MCP Client Session...")
                await session.initialize()
                logger.info("MCP Session initialized successfully!")
                
                # Register the mcp client session
                register_mcp_client_session(session)
                app.state.mcp_session = session

                yield
    except Exception as e:
        logger.warning(f"⚠️ Failed to spawn local MCP server subprocess: {e}")
        logger.warning("LabhArth AI will run with direct service-layer fallback mode enabled.")
        
        # Yield anyway to allow the FastAPI application to start up and run normally
        yield
    finally:
        # Shutdown: close database connections
        from backend.database.connection import close_db
        await close_db()
        logger.info("Database connections closed.")
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
    allow_origins = settings.allowed_origins_list
    allow_credentials = True
    if "*" in allow_origins or not allow_origins:
        allow_origins = ["*"]
        allow_credentials = False

    logger.info(f"CORS Allowed Origins: {allow_origins} (Credentials: {allow_credentials})")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Response Compression Middleware ---
    from fastapi.middleware.gzip import GZipMiddleware
    app.add_middleware(GZipMiddleware, minimum_size=500)

    # --- Request Lifecycle Middleware ---
    from backend.api.middleware import RequestLifecycleMiddleware
    app.add_middleware(RequestLifecycleMiddleware)

    # --- Register Routes ---
    api_prefix = "/api/v1"
    app.include_router(health_router, prefix=api_prefix, tags=["Health"])
    app.include_router(schemes_router, prefix=api_prefix)
    app.include_router(search_router, prefix=api_prefix)
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
        loop="none",
    )
