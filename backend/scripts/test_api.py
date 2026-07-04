"""
LabhArth AI — API Integration Test Client
=================================================
Automated verification of the FastAPI REST API layers.
Fires requests against the API endpoints under active lifespan
management, verifying health, chat, search, and eligibility routes.
"""

import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import select
import httpx
from backend.database.connection import async_session_factory
from backend.models.db_models import Scheme
from backend.main import app


async def run_tests():
    # Force UTF-8 streams for Windows console compatibility
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 80)
    print(" LABHARTH AI — FastAPI REST API INTEGRATION TEST CLIENT")
    print("=" * 80)

    # 1. Fetch a real scheme from PostgreSQL to use for lookup test
    valid_scheme_id = None
    valid_scheme_name = None
    try:
        async with async_session_factory() as session:
            res = await session.execute(select(Scheme).limit(1))
            scheme = res.scalar_one_or_none()
            if scheme:
                valid_scheme_id = str(scheme.id)
                valid_scheme_name = scheme.name
                print(f"[DB] Found sample scheme: '{valid_scheme_name}' ({valid_scheme_id})")
            else:
                print("[DB] Warning: No schemes found in database.")
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch test scheme: {e}")

    # 2. Run requests through httpx.AsyncClient using FastAPI's lifespan
    print("\nStarting FastAPI lifespan (initiating DB, spawning MCP server)...")
    async with app.router.lifespan_context(app):
        print("FastAPI lifespan context entered successfully!")
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://localhost:8000",
            timeout=30.0
        ) as client:
            print("FastAPI application started!")

            # ----------------------------------------------------
            # TEST Scenario 0: Health Check
            # ----------------------------------------------------
            print("\n" + "-" * 50)
            print("SCENARIO 0: API HEALTH CHECK (GET /api/v1/health)")
            print("-" * 50)
            try:
                res = await client.get("/api/v1/health")
                print(f"Status Code: {res.status_code}")
                print(f"Headers: {dict(res.headers)}")
                print("Response Body:")
                import json
                print(json.dumps(res.json(), indent=2))
            except Exception as e:
                print(f"Health check failed: {e}")

            # ----------------------------------------------------
            # TEST Scenario 1: Chat API (Student Scholarship Query)
            # ----------------------------------------------------
            print("\n" + "-" * 50)
            print("SCENARIO 1: STUDENT SCHOLARSHIP (POST /api/v1/chat)")
            print("-" * 50)
            chat_req = {
                "message": "I am a student from Maharashtra. Which schemes can I apply for?",
                "session_id": "test-session-student"
            }
            try:
                res = await client.post("/api/v1/chat", json=chat_req)
                print(f"Status Code: {res.status_code}")
                print("Response Body:")
                print(json.dumps(res.json(), indent=2))
            except Exception as e:
                print(f"Chat request failed: {e}")

            # ----------------------------------------------------
            # TEST Scenario 2: Search API (Farmer Subsidy Query)
            # ----------------------------------------------------
            print("\n" + "-" * 50)
            print("SCENARIO 2: FARMER SUBSIDY SEARCH (POST /api/v1/search)")
            print("-" * 50)
            search_req = {
                "query": "subsidies for seeds, fertilizer, and agricultural machinery",
                "category": "Agriculture, Rural & Environment",
                "state": "Gujarat",
                "limit": 3
            }
            try:
                res = await client.post("/api/v1/search", json=search_req)
                print(f"Status Code: {res.status_code}")
                print("Response Body:")
                print(json.dumps(res.json(), indent=2))
            except Exception as e:
                print(f"Search request failed: {e}")

            # ----------------------------------------------------
            # TEST Scenario 3: Eligibility API (Women's Welfare Schemes)
            # ----------------------------------------------------
            print("\n" + "-" * 50)
            print("SCENARIO 3: BULK ELIGIBILITY (POST /api/v1/eligibility)")
            print("-" * 50)
            profile = {
                "age": 35,
                "gender": "female",
                "state": "Karnataka",
                "category": "General",
                "income_annual": 150000.0,
                "occupation": "unemployed",
                "is_bpl": True,
                "is_farmer": False,
                "is_student": False
            }
            try:
                res = await client.post("/api/v1/eligibility", json=profile)
                print(f"Status Code: {res.status_code}")
                print("Response Body:")
                print(json.dumps(res.json(), indent=2))
            except Exception as e:
                print(f"Eligibility evaluation failed: {e}")

            # ----------------------------------------------------
            # TEST Scenario 4: Scheme Details Lookup
            # ----------------------------------------------------
            print("\n" + "-" * 50)
            print("SCENARIO 4: SCHEME DETAILS (GET /api/v1/schemes/{scheme_id})")
            print("-" * 50)
            if valid_scheme_id:
                try:
                    res = await client.get(f"/api/v1/schemes/{valid_scheme_id}")
                    print(f"Status Code: {res.status_code}")
                    print("Response Body (Keys):", list(res.json().keys()))
                    print("Details Name:", res.json().get("name"))
                    print("Category:", res.json().get("category"))
                    print("Level:", res.json().get("level"))
                except Exception as e:
                    print(f"Scheme detail fetch failed: {e}")
            else:
                print("Skipping details lookup check: no valid scheme loaded in postgres DB.")

    print("\n" + "=" * 80)
    print(" REST API VERIFICATION RUN COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_tests())
