import json
from backend.utils.logger import logger

# Global MCP client session reference to route agent tools through the stdio server
_mcp_client_session = None

def register_mcp_client_session(session):
    """
    Register an active MCP client session for routing agent tools.
    """
    global _mcp_client_session
    _mcp_client_session = session
    logger.info("Active MCP Client Session registered with agents helper module.")

def get_mcp_client_session():
    global _mcp_client_session
    return _mcp_client_session

async def call_mcp_tool(name: str, arguments: dict) -> dict:
    """
    Invokes an MCP tool. First attempts to call it through the registered MCP client session,
    falling back directly to the local backend service layer if no active session is found.
    """
    global _mcp_client_session
    if _mcp_client_session:
        try:
            logger.info(f"Routing tool '{name}' call through active MCP Client Session...")
            res = await _mcp_client_session.call_tool(name, arguments)
            # FastMCP responses wrap tool results in a Content structure
            if res.content and len(res.content) > 0:
                text_content = res.content[0].text
                return json.loads(text_content)
            return {}
        except Exception as e:
            logger.error(f"MCP Client Tool call '{name}' failed: {e}. Falling back to direct service layer.")
    
    # Fallback to direct service layer invocations
    if name == "search_schemes":
        from backend.services.scheme_service import SchemeService
        service = SchemeService()
        return await service.search_schemes(
            query=arguments.get("query"),
            category=arguments.get("category"),
            state=arguments.get("state"),
            limit=arguments.get("limit", 10)
        )
    elif name == "get_scheme_details":
        from backend.services.scheme_service import SchemeService
        from uuid import UUID
        service = SchemeService()
        return await service.get_scheme_details(UUID(arguments.get("scheme_id")))
    elif name == "check_eligibility":
        from backend.services.eligibility_service import EligibilityService
        from uuid import UUID
        service = EligibilityService()
        return await service.check_eligibility(
            scheme_id=UUID(arguments.get("scheme_id")),
            user_profile=arguments.get("user_profile")
        )
    else:
        raise ValueError(f"Unknown tool: {name}")
