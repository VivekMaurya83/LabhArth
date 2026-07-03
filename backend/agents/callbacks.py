import time
import os
import asyncio
from backend.utils.logger import logger
from google.adk.tools import ToolContext

_key_index = 0

async def before_agent_callback(*args, **kwargs):
    global _key_index
    context = None
    if len(args) > 0:
        context = args[0]
    elif "callback_context" in kwargs:
        context = kwargs["callback_context"]
    elif "context" in kwargs:
        context = kwargs["context"]
        
    if not context:
        logger.warning(f"before_agent_callback could not resolve context. args={args}, kwargs={kwargs}")
        return

    # 1. Rotate API keys to distribute load across quota pools
    raw_keys = os.getenv("GEMINI_API_KEYS") or os.getenv("GOOGLE_API_KEY") or ""
    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if keys:
        # Increment index first so sub-agent uses a different key than parent/root run
        _key_index += 1
        key = keys[_key_index % len(keys)]
        os.environ["GEMINI_API_KEY"] = key
        os.environ["GOOGLE_API_KEY"] = key
        logger.info(f"Rotated environment for '{context.agent_name if context else 'Agent'}' to API Key: {key[:10]}...")

    # 2. Apply a strict 0.2-second rate limit buffer between agent runs
    logger.info("Applying rate-limiting delay (0.2s) to safeguard free-tier quota...")
    await asyncio.sleep(0.2)

    if "start_times" not in context.state:
        context.state["start_times"] = {}
    context.state["start_times"][context.agent_name] = time.perf_counter()
    
    if "delegation_chain" not in context.state:
        context.state["delegation_chain"] = []
    context.state["delegation_chain"].append(context.agent_name)
    
    logger.info(f"\n============================================================\n[AGENT START] Agent '{context.agent_name}' Invoked\nDelegation Chain: {' -> '.join(context.state['delegation_chain'])}")

def after_agent_callback(*args, **kwargs):
    context = None
    if len(args) > 0:
        context = args[0]
    elif "callback_context" in kwargs:
        context = kwargs["callback_context"]
    elif "context" in kwargs:
        context = kwargs["context"]
        
    if not context:
        logger.warning(f"after_agent_callback could not resolve context. args={args}, kwargs={kwargs}")
        return

    start_times = context.state.get("start_times", {})
    start_time = start_times.get(context.agent_name)
    elapsed_str = ""
    if start_time:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        elapsed_str = f" in {duration_ms:.2f}ms"
    
    logger.info(f"[AGENT END] Agent '{context.agent_name}' Finished{elapsed_str}\n============================================================")

def before_tool_callback(*args, **kwargs):
    tool = kwargs.get("tool") or (args[0] if len(args) > 0 else None)
    arguments = kwargs.get("args") or kwargs.get("arguments") or kwargs.get("callback_arguments") or (args[1] if len(args) > 1 else {})
    context = kwargs.get("tool_context") or kwargs.get("context") or kwargs.get("callback_context") or (args[2] if len(args) > 2 else None)

    agent_name = context.agent_name if context else "Unknown"
    tool_name = tool.name if tool else "Unknown"
    
    # Store start time if context state is available
    if context and hasattr(context, "state") and isinstance(context.state, dict):
        if "tool_start_times" not in context.state:
            context.state["tool_start_times"] = {}
        context.state["tool_start_times"][tool_name] = time.perf_counter()
    
    logger.info(f"  --> [TOOL CALL] Agent '{agent_name}' invoking tool '{tool_name}'")
    logger.info(f"      Arguments: {arguments}")

def after_tool_callback(*args, **kwargs):
    tool = kwargs.get("tool") or (args[0] if len(args) > 0 else None)
    arguments = kwargs.get("args") or kwargs.get("arguments") or kwargs.get("callback_arguments") or (args[1] if len(args) > 1 else {})
    context = kwargs.get("tool_context") or kwargs.get("context") or kwargs.get("callback_context") or (args[2] if len(args) > 2 else None)
    result = kwargs.get("tool_response") or kwargs.get("result") or kwargs.get("callback_result") or (args[3] if len(args) > 3 else None)

    tool_name = tool.name if tool else "Unknown"
    
    # Measure tool execution duration
    elapsed_str = ""
    if context and hasattr(context, "state") and isinstance(context.state, dict):
        tool_start_times = context.state.get("tool_start_times", {})
        start_time = tool_start_times.get(tool_name)
        if start_time:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            elapsed_str = f" in {duration_ms:.2f}ms"
    
    logger.info(f"  <-- [TOOL RESPONSE] Tool '{tool_name}' returned successfully{elapsed_str}")
    res_str = str(result)
    if len(res_str) > 300:
        res_str = res_str[:300] + "... [truncated]"
    logger.info(f"      Result: {res_str}")

def route_to_agent(agent_name: str, tool_context: ToolContext) -> str:
    """
    Handoff and route execution control to a specialized sub-agent.
    
    Args:
        agent_name: The name of the target sub-agent. Must be exactly one of:
                    - 'profile_agent' (use if user provides personal details like age, income, state, etc.)
                    - 'scheme_search_agent' (use if user wants to search/find schemes)
                    - 'eligibility_agent' (use if user asks about eligibility/qualification for a scheme)
        tool_context: The execution context injected by ADK.
    """
    tool_context.actions.transfer_to_agent = agent_name
    return f"Handoff initiated to sub-agent '{agent_name}'."

def return_to_orchestrator(tool_context: ToolContext) -> str:
    """
    Return execution control back to the root Orchestrator Agent. 
    Call this when you have finished your specialized task.
    
    Args:
        tool_context: The execution context injected by ADK.
    """
    tool_context.actions.transfer_to_agent = "orchestrator_agent"
    return "Handoff initiated back to root orchestrator_agent."
