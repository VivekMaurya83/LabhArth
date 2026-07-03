"""
LabhArth AI — Chat Routes
=============================
API endpoints for the conversational AI interface.
"""

from uuid import uuid4
from fastapi import APIRouter, Depends
from google.adk import Runner

from backend.models.schemas import ChatRequest, ChatResponse
from backend.security.rate_limiter import rate_limit_dependency
from backend.api.dependencies import get_orchestrator_runner
from backend.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send Chat Message",
    description="Send a message to the LabhArth AI assistant.",
    dependencies=[Depends(rate_limit_dependency)],
)
async def chat(
    request: ChatRequest,
    runner: Runner = Depends(get_orchestrator_runner)
) -> ChatResponse:
    """
    Process a chat message through the AI agent pipeline.

    The Orchestrator Agent receives the message, classifies intent,
    and routes to the appropriate sub-agent.
    """
    session_id = request.session_id or str(uuid4())
    logger.info(f"API chat: session={session_id}, message='{request.message[:50]}'")

    # 1. Prompt Injection scanner
    from backend.security import scan_prompt_injection
    scan_prompt_injection(request.message)

    try:
        from google.genai import types
        response_chunks = []
        
        async for event in runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=types.Content(
                parts=[types.Part(text=request.message)]
            )
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_chunks.append(part.text)
                        
        final_text = "".join(response_chunks)
        if not final_text:
            final_text = "I am sorry, I couldn't generate a response. Please try again."
            
        logger.info(f"Orchestrator Agent response complete for session {session_id}.")
        return ChatResponse(
            response=final_text,
            session_id=session_id,
            agent_name="orchestrator_agent",
            sources=None,
        )
    except Exception as e:
        logger.error(f"Error in chat agent runner: {e}", exc_info=True)
        # Graceful agent failure response recovery
        friendly_fallback = (
            "I am sorry, the AI reasoning agent is currently experiencing connection latency. "
            "Please try your request again shortly, or use the main Search Catalog tab to browse "
            "and check your eligibility for schemes directly!"
        )
        return ChatResponse(
            response=friendly_fallback,
            session_id=session_id,
            agent_name="orchestrator_agent",
            sources=None,
        )

