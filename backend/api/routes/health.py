"""
LabhArth AI — Health Check Route
===================================
"""

import time
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.schemas import HealthResponse, ComponentStatus
from backend.utils.config import get_settings
from backend.database.connection import get_db_session

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the API and all underlying services (DB, Qdrant, Gemini, MCP, ADK) are running and healthy.",
)
async def health_check(
    db: AsyncSession = Depends(get_db_session)
) -> HealthResponse:
    """Return the current health status of the API and its dependent components."""
    settings = get_settings()
    components = {}
    overall_healthy = True

    # 1. Verify PostgreSQL Connection
    t_start = time.perf_counter()
    try:
        await db.execute(text("SELECT 1"))
        latency = (time.perf_counter() - t_start) * 1000.0
        components["postgres"] = ComponentStatus(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        latency = (time.perf_counter() - t_start) * 1000.0
        overall_healthy = False
        components["postgres"] = ComponentStatus(
            status="unhealthy", message=str(e), latency_ms=round(latency, 2)
        )

    # 2. Verify Qdrant Cloud Connection
    t_start = time.perf_counter()
    try:
        from backend.rag.retriever import QdrantRetriever
        retriever = QdrantRetriever()
        client = await retriever._get_client()
        await client.collection_exists(retriever.collection_name)
        latency = (time.perf_counter() - t_start) * 1000.0
        components["qdrant"] = ComponentStatus(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        latency = (time.perf_counter() - t_start) * 1000.0
        overall_healthy = False
        components["qdrant"] = ComponentStatus(
            status="unhealthy", message=str(e), latency_ms=round(latency, 2)
        )

    # 3. Verify Gemini API
    t_start = time.perf_counter()
    try:
        from backend.rag.embeddings import EmbeddingService
        embedding_service = EmbeddingService()
        # Call with a minimal payload to check API key validity
        await embedding_service.embed_query("healthcheck")
        latency = (time.perf_counter() - t_start) * 1000.0
        components["gemini_api"] = ComponentStatus(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        latency = (time.perf_counter() - t_start) * 1000.0
        overall_healthy = False
        components["gemini_api"] = ComponentStatus(
            status="unhealthy", message=str(e), latency_ms=round(latency, 2)
        )

    # 4. Verify MCP Server
    t_start = time.perf_counter()
    try:
        from backend.agents.mcp_client_helper import get_mcp_client_session
        session = get_mcp_client_session()
        if session is not None:
            await session.list_tools()
            latency = (time.perf_counter() - t_start) * 1000.0
            components["mcp_server"] = ComponentStatus(status="healthy", latency_ms=round(latency, 2))
        else:
            latency = (time.perf_counter() - t_start) * 1000.0
            components["mcp_server"] = ComponentStatus(
                status="healthy", message="healthy (running in direct service-layer mode)", latency_ms=round(latency, 2)
            )
    except Exception as e:
        latency = (time.perf_counter() - t_start) * 1000.0
        overall_healthy = False
        components["mcp_server"] = ComponentStatus(
            status="unhealthy", message=str(e), latency_ms=round(latency, 2)
        )

    # 5. Verify ADK Agent Initialization
    t_start = time.perf_counter()
    try:
        from google.adk import Runner
        from google.adk.sessions import InMemorySessionService
        from backend.agents import orchestrator_agent

        session_service = InMemorySessionService()
        Runner(
            agent=orchestrator_agent,
            app_name="LabhArth_AI_Healthcheck",
            session_service=session_service,
            auto_create_session=True,
        )
        latency = (time.perf_counter() - t_start) * 1000.0
        components["adk_agent"] = ComponentStatus(status="healthy", latency_ms=round(latency, 2))
    except Exception as e:
        latency = (time.perf_counter() - t_start) * 1000.0
        overall_healthy = False
        components["adk_agent"] = ComponentStatus(
            status="unhealthy", message=str(e), latency_ms=round(latency, 2)
        )

    return HealthResponse(
        status="healthy" if overall_healthy else "unhealthy",
        version="0.1.0",
        environment=settings.app_env,
        components=components,
    )
