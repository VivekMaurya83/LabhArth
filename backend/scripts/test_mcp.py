"""
LabhArth AI — MCP Integration Test Client
============================================
Launches the FastMCP server in a subprocess and invokes the search_schemes,
get_scheme_details, and check_eligibility tools via the Model Context Protocol
stdio client transport, outputting structured JSON results.
"""

import asyncio
import json
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_mcp_client():
    # Force UTF-8 encoding on standard streams to prevent Windows cp1252 charmap errors
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 60)
    print(" LABHARTH AI — MCP INTEGRATION TEST")
    print("=" * 60)

    # Determine Python executable
    python_exe = sys.executable or "python"
    
    # Configure parameters to spawn the MCP server subprocess
    # Run python with -u (unbuffered) and set PYTHONUNBUFFERED to prevent logs or outputs from buffering
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONUNBUFFERED"] = "1"
    
    server_params = StdioServerParameters(
        command=python_exe,
        args=["-u", "-m", "backend.mcp.server"],
        env=subprocess_env
    )

    print(f"Spawning MCP server subprocess via: {python_exe} -m backend.mcp.server")
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("Initializing MCP Client Session...")
            await session.initialize()
            print("Session initialized successfully!\n")

            # 1. List Available Tools
            print("-" * 50)
            print("1. LIST AVAILABLE TOOLS")
            print("-" * 50)
            tools_response = await session.list_tools()
            print(f"Found {len(tools_response.tools)} registered tools:")
            for t in tools_response.tools:
                print(f"  - Tool: {t.name}")
                print(f"    Description: {t.description}")
            print("\n")

            # 2. Invoke search_schemes tool
            print("-" * 50)
            print("2. INVOKE: search_schemes")
            print("-" * 50)
            search_query = "scholarships and educational benefits for students in maharashtra"
            print(f"Querying search_schemes for: '{search_query}'...")
            
            search_res = await session.call_tool(
                "search_schemes", 
                {"query": search_query, "category": "Education", "state": "Maharashtra", "limit": 2}
            )
            
            # Print response
            print("Raw Response Content:")
            content_text = search_res.content[0].text
            print(content_text)
            
            search_data = json.loads(content_text)
            results = search_data.get("results", [])
            
            if not results:
                print("[ERROR] No search results found. Exiting test.")
                return

            # Grab matched scheme_id for next steps
            target_scheme = results[0]
            scheme_id = target_scheme["id"]
            scheme_name = target_scheme["name"]
            print(f"\nMatched Scheme ID: {scheme_id} ({scheme_name})\n")

            # 3. Invoke get_scheme_details tool
            print("-" * 50)
            print("3. INVOKE: get_scheme_details")
            print("-" * 50)
            print(f"Querying get_scheme_details for ID: {scheme_id}...")
            
            details_res = await session.call_tool(
                "get_scheme_details",
                {"scheme_id": scheme_id}
            )
            
            details_text = details_res.content[0].text
            print("Details Response:")
            details_data = json.loads(details_text)
            print(json.dumps(details_data, indent=2))
            print("\n")

            # 4. Invoke check_eligibility tool (Scenario A: Eligible)
            print("-" * 50)
            print("4. INVOKE: check_eligibility (Scenario A: Eligible)")
            print("-" * 50)
            eligible_profile = {
                "age": 20,
                "gender": "Male",
                "state": "Maharashtra",
                "category": "General",
                "income_annual": 100000,
                "is_student": True,
                "is_farmer": False,
                "is_bpl": False
            }
            print(f"Checking eligibility with profile: {eligible_profile}...")
            
            elig_res_a = await session.call_tool(
                "check_eligibility",
                {"scheme_id": scheme_id, "user_profile": eligible_profile}
            )
            
            elig_text_a = elig_res_a.content[0].text
            print("Eligibility Result A:")
            print(json.dumps(json.loads(elig_text_a), indent=2))
            print("\n")

            # 5. Invoke check_eligibility tool (Scenario B: Not Eligible - Income Exceeds Limit)
            print("-" * 50)
            print("5. INVOKE: check_eligibility (Scenario B: Not Eligible due to Income)")
            print("-" * 50)
            ineligible_profile = {
                "age": 20,
                "gender": "Male",
                "state": "Maharashtra",
                "category": "General",
                "income_annual": 900000, # Exceeds Maharashtra Scholarship limit (800000)
                "is_student": True,
                "is_farmer": False,
                "is_bpl": False
            }
            print(f"Checking eligibility with profile: {ineligible_profile}...")
            
            elig_res_b = await session.call_tool(
                "check_eligibility",
                {"scheme_id": scheme_id, "user_profile": ineligible_profile}
            )
            
            elig_text_b = elig_res_b.content[0].text
            print("Eligibility Result B:")
            print(json.dumps(json.loads(elig_text_b), indent=2))
            print("\n")

            # 6. Invoke check_eligibility tool (Scenario C: Partially Eligible - Missing Age field)
            print("-" * 50)
            print("6. INVOKE: check_eligibility (Scenario C: Partially Eligible due to missing Age)")
            print("-" * 50)
            partial_profile = {
                "gender": "Male",
                "state": "Maharashtra",
                "category": "General",
                "income_annual": 100000,
                "is_student": True,
                "is_farmer": False,
                "is_bpl": False
                # "age" field is missing
            }
            print(f"Checking eligibility with profile (missing age): {partial_profile}...")
            
            elig_res_c = await session.call_tool(
                "check_eligibility",
                {"scheme_id": scheme_id, "user_profile": partial_profile}
            )
            
            elig_text_c = elig_res_c.content[0].text
            print("Eligibility Result C:")
            print(json.dumps(json.loads(elig_text_c), indent=2))
            print("\n")

            print("=" * 60)
            print(" MCP INTEGRATION TEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_mcp_client())
