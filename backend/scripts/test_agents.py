"""
LabhArth AI — Multi-Agent System Integration Test Client
============================================================
Launches the MCP server subprocess, registers it with the ADK agent tools,
and executes the three user queries through the multi-agent orchestration
flow using the Google Agent Development Kit (ADK).
"""

import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.genai import types
from google.adk import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.features import FeatureName, override_feature_enabled
override_feature_enabled(FeatureName.JSON_SCHEMA_FOR_FUNC_DECL, False)

from backend.agents import orchestrator_agent
from backend.agents.mcp_client_helper import register_mcp_client_session
from backend.utils.logger import logger

# Load environment variables
load_dotenv()

async def run_query(runner: Runner, query: str, session_id: str):
    print("\n" + "=" * 80)
    print(f" USER QUERY: '{query}'")
    print(f" Session ID: {session_id}")
    print("=" * 80)
    
    t_start = time.perf_counter()
    
    try:
        response_chunks = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session_id,
            new_message=types.Content(
                parts=[types.Part(text=query)]
            )
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                        response_chunks.append(part.text)
        
        t_end = time.perf_counter()
        elapsed_sec = t_end - t_start
        print(f"\n\n[SUCCESS] Final Response generated in {elapsed_sec:.2f} seconds.")
        
    except Exception as e:
        logger.error(f"Error during agent run: {e}")
        print(f"\n[ERROR] Agent execution failed: {e}")

def select_all_valid_api_keys() -> list[str]:
    raw_keys = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEYS") or ""
    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    return keys

async def main():
    # Force UTF-8 stream encoding on standard output for Windows console compatibility
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 80)
    print(" LABHARTH AI — GOOGLE ADK MULTI-AGENT TEST RUNNER")
    print("=" * 80)

    # 1. Fetch and filter valid Gemini API keys
    api_keys = select_all_valid_api_keys()
    if not api_keys:
        print("[ERROR] No valid Gemini API Keys found (all are exhausted or invalid).")
        sys.exit(1)
        
    print(f"\nLoaded {len(api_keys)} active Gemini API Keys for load balancing.")
    
    # Update environment with only valid keys for agents rotation
    valid_keys_str = ",".join(api_keys)
    os.environ["GOOGLE_API_KEY"] = valid_keys_str
    os.environ["GEMINI_API_KEYS"] = valid_keys_str

    # 2. Spawn local MCP Server subprocess
    python_exe = sys.executable or "python"
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONUNBUFFERED"] = "1"
    
    server_params = StdioServerParameters(
        command=python_exe,
        args=["-u", "-m", "backend.mcp.server"],
        env=subprocess_env
    )

    print(f"Spawning local MCP server via stdio transport: {python_exe} -m backend.mcp.server")
    
    # Start Stdio MCP Client session
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("Initializing MCP Client Session...")
            await session.initialize()
            print("MCP Session initialized successfully!")
            
            # Register mcp client session in helper so agent tools route calls through it
            register_mcp_client_session(session)
            
            from backend.agents.profile_agent import profile_agent
            print("PROFILE_AGENT TOOLS:", [t.name if hasattr(t, "name") else t.__name__ for t in profile_agent.tools])
            
            # 3. Setup ADK Agent Runner
            session_service = InMemorySessionService()
            runner = Runner(
                agent=orchestrator_agent,
                app_name="LabhArth_AI",
                session_service=session_service,
                auto_create_session=True
            )
            
            # 4. Run the three required test queries using different keys
            queries = [
                "I am a student from Maharashtra. Which schemes can I apply for?",
                "I am a widow living in Karnataka.",
                "I am a farmer from Gujarat."
            ]
            
            for idx, query in enumerate(queries, start=0):
                session_id = f"test-session-{idx + 1}"
                await run_query(runner, query, session_id)
                print("\nWaiting 10 seconds before next query to prevent rate limits...")
                await asyncio.sleep(10.0)
                
    print("\n" + "=" * 80)
    print(" MULTI-AGENT SYSTEM VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
