"""
LabhArth AI — Chat Routes
=============================
API endpoints for the conversational AI interface.
"""

from uuid import uuid4

from fastapi import APIRouter, Depends

from backend.models.schemas import ChatRequest, ChatResponse
from backend.security.rate_limiter import rate_limit_dependency
from backend.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send Chat Message",
    description="Send a message to the LabhArth AI assistant.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message through the AI agent pipeline.

    The Orchestrator Agent receives the message, classifies intent,
    and routes to the appropriate sub-agent.
    """
    session_id = request.session_id or str(uuid4())
    logger.info(f"API chat: session={session_id}, message='{request.message[:50]}'")

    # TODO: Wire to OrchestratorAgent
    return ChatResponse(
        response="Welcome to LabhArth AI! 🇮🇳 I'm here to help you discover government welfare schemes. This service is currently being set up. Please check back soon!",
        session_id=session_id,
        agent_name="orchestrator",
        sources=None,
    )
