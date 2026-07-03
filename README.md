# 🇮🇳 LabhArth AI: Agentic RAG Welfare Platform

> **LabhArth** (लाभ + अर्थ): Connecting citizens to the true meaning and utility of government welfare. An advanced agentic retrieval-augmented generation (RAG) platform that guides Indian citizens through central and state-level scheme discovery, profile eligibility matching, and document preparation workflows.

[![System Status](https://img.shields.io/badge/status-active-emerald.svg)]()
[![Platform Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-purple.svg)]()
[![AI-Model](https://img.shields.io/badge/LLM-Gemini--2.5--Flash-orange.svg)]()
[![Vector-DB](https://img.shields.io/badge/Vector--DB-Qdrant-red.svg)]()

---

## 📖 Table of Contents
1. [Platform Core Vision](#-platform-core-vision)
2. [Key Capabilities](#-key-capabilities)
3. [System Architecture](#-system-architecture)
4. [Technical Implementation Detail](#-technical-implementation-detail)
   - [Google ADK Multi-Agent Orchestration](#google-adk-multi-agent-orchestration)
   - [Model Context Protocol (MCP) Server](#model-context-protocol-mcp-server)
   - [Semantic Hybrid Storage & RAG Pipeline](#semantic-hybrid-storage--rag-pipeline)
   - [API Quota Rotation & Resilience](#api-quota-rotation--resilience)
   - [Security Shield (Prompt Injection Protection)](#security-shield-prompt-injection-protection)
5. [Directory Layout](#-directory-layout)
6. [Local Deployment Guide](#-local-deployment-guide)
   - [Prerequisites](#prerequisites)
   - [Database Infrastructure Setup](#database-infrastructure-setup)
   - [FastAPI Backend Service](#fastapi-backend-service)
   - [Vite React Frontend SPA](#vite-react-frontend-spa)
7. [Verification & Testing](#-verification--testing)
   - [End-to-End Test Suite](#end-to-end-test-suite)
   - [RAG Retrieval Metrics Evaluator](#rag-retrieval-metrics-evaluator)

---

## 🎯 Platform Core Vision

Many eligible citizens miss out on government assistance due to complex legal rules, fragmented information across sitemaps, and confusing paperwork requirements. **LabhArth AI** acts as a conversational bridge, allowing users to state their conditions in natural language (e.g. *"I am a small farmer in Maharashtra struggling with fertilizer costs"*) and instantly matching them with relevant state and central benefits.

---

## ✨ Key Capabilities

*   🔍 **Natural Language Semantic Search:** Bypasses keyword constraints using vector embeddings of sitemap text to locate contextually relevant schemes.
*   📋 **Deterministic Rule Checking:** Evaluates structured user profiles against multi-variable constraints (income caps, age thresholds, occupational fields, state boundaries) using a rule engine instead of relying on unreliable LLM inferences.
*   🗂️ **Dynamic Document Checklists:** Translates scheme requirements into a custom-tailored document preparation list, detailing mandatory items, optional exemptions, and acceptable alternates.
*   👥 **Multi-Agent Orchestration:** Spawns specialized agents for profile gathering, scheme catalog queries, and eligibility checks, coordinated by a central orchestrator.
*   🌓 **Refactored Responsive Dashboard:** Features a clean web interface supporting full Light and Dark mode options, transitions, layout spacing, page routes, and staggered entry animations.

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────┐
                                  │   React 18 Frontend SPA  │
                                  │   (Vite + React Router)  │
                                  └────────────┬─────────────┘
                                               │ HTTP / REST
                                  ┌────────────▼─────────────┐
                                  │      FastAPI Backend     │
                                  │  (Uvicorn Lifespan App)  │
                                  └────────────┬─────────────┘
                                               │ Invoke Request
    ┌──────────────────────────────────────────▼──────────────────────────────────────────┐
    │                               Google ADK Multi-Agent System                         │
    │                                                                                     │
    │                      ┌──────────────────────────────────────────────┐               │
    │                      │             Orchestrator Agent               │               │
    │                      │  (Central Router / Intent Hand-off Manager)  │               │
    │                      └──────┬───────────────┬────────────────┬──────┘               │
    │                             │               │                │                      │
    │                             ▼               ▼                ▼                      │
    │                     ┌───────────────┐ ┌──────────────┐ ┌─────────────┐              │
    │                     │ Profile Agent │ │ Search Agent │ │ Match Agent │              │
    │                     └───────┬───────┘ └──────┬───────┘ └──────┬──────┘              │
    │                             │                │                │                     │
    └─────────────────────────────┼────────────────┼────────────────┼─────────────────────┘
                                  │                │                │
                                  └──────────┐     │     ┌──────────┘
                                        MCP  │     │     │ MCP
                                             ▼     ▼     ▼
                                  ┌──────────────────────────┐
                                  │    Local MCP Stdio Server│
                                  │  (Dual Standard IO Channel)│
                                  └────────────┬─────────────┘
                                               │ Expose Internal Services
                                  ┌────────────▼─────────────┐
                                  │   Hybrid Storage Layer   │
                                  ├────────────┬─────────────┤
                                  │ PostgreSQL │ Qdrant Cloud│
                                  │   (Neon)   │ (Vector DB) │
                                  └────────────┴─────────────┘
```

---

## 🛠️ Technical Implementation Detail

### Google ADK Multi-Agent Orchestration
LabhArth AI builds upon the **Google Agent Development Kit (ADK)**. Specialized agent loops collaborate by sharing a transfer-based state channel:
1.  **Orchestrator Agent:** The root gateway. Evaluates user intent and uses hand-offs (`transfer_to_agent`) to route requests to specialized sub-agents while maintaining profile contexts in the background.
2.  **Profile Agent:** Formulates structural profile mappings using Pydantic validation tools, converting conversational sentences into valid JSON data.
3.  **Scheme Search Agent:** Interfaces with semantic databases to retrieve ranked candidate lists matching the user's situation.
4.  **Eligibility Agent:** Runs full profile comparisons against candidate scheme criteria, reporting validation parameters.

### Model Context Protocol (MCP) Server
To isolate tools from agents, we run a local **FastMCP stdio server**. Standard I/O communication pipes are protected by a global standard output redirector, routing debug output to a dedicated log file (`logs/mcp_server.log`) to prevent pipeline deadlocks on standard output channels.
*   `search_schemes`: Executes semantic and metadata keyword lookups.
*   `get_scheme_details`: Hydrates full scheme parameters from PostgreSQL.
*   `check_eligibility`: Invokes the deterministic rules matching engine.

### Semantic Hybrid Storage & RAG Pipeline
Retrieval-Augmented Generation relies on a dual-engine architecture:
*   **Vector Retrieval (Qdrant):** PDF documents are segmented using sitemap state-machine extractors, embedded using the `gemini-embedding-001` model (768 dimensions), and indexed in Qdrant with payload metadata filters.
*   **Relational Storage (PostgreSQL):** PostgreSQL handles relational lookups, transaction audits, and structured rule storage.
*   **Double-Fallback Scheme Search:** If vector indexes or databases experience network timeouts, the query pipeline falls back to database keyword parsing. If both fail, it resolves to a stored in-memory mock schema, guaranteeing the API remains resilient and operational.

### API Quota Rotation & Resilience
A rotated pool of multiple Gemini API keys operates under the `GOOGLE_API_KEY` configurations. When a `429 Resource Exhausted` rate-limit status is detected, the query handler automatically switches to the next active API key and retries the request.

### Security Shield (Prompt Injection Protection)
All inputs pass through a security middleware module (`prompt_injection.py`) that scans text case-insensitively for jailbreak attempts (e.g., *"ignore prior instructions"*, *"system override"*). Flagged inputs are blocked with an HTTP 400 Bad Request response before reaching the LLM layers.

---

## 📁 Directory Layout

```
LabhArth/
├── backend/                  # FastAPI Application Services
│   ├── agents/               # Google ADK agent personas & hand-offs
│   ├── api/                  # REST controllers, middleware, & router paths
│   ├── database/             # Async connection hooks & repositories
│   ├── mcp/                  # MCP Server registry & stdout isolation
│   ├── models/               # Pydantic schemas & SQLAlchemy ORM mapping
│   ├── rag/                  # ETL ingestion, embeddings, & Qdrant retrievers
│   ├── security/             # Prompt injection filters & rate limiters
│   ├── services/             # Rules verification engines & scheme logic
│   ├── tests/                # System E2E verification test suite
│   └── utils/                # Environment configurations & log handlers
├── frontend/                 # Client React SPA
│   ├── src/
│   │   ├── components/       # Forms, status pills, bubbles, & header toggles
│   │   ├── pages/            # Search catalog, detail panels, & home screen
│   │   ├── services/         # API HTTP connector utilities
│   │   └── index.css         # Refactored Light/Dark design variables
│   └── package.json
└── README.md
```

---

## 🚀 Local Deployment Guide

### Prerequisites
*   **Python:** Version `3.11` or higher.
*   **NodeJS:** Version `18` or higher (equipped with `npm` or `yarn`).
*   **Database Services:** Access to a PostgreSQL instance and Qdrant Cloud cluster (or local Qdrant container).

---

### Database Infrastructure Setup

1.  **Configure environment variables:** Create a `backend/.env` file from the example template.
    ```bash
    cd backend
    cp .env.example .env
    ```
    Set your database credentials, Qdrant cluster host, and API key string:
    ```ini
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/labharth
    QDRANT_HOST=https://your-qdrant-cluster.cloud.qdrant.io
    QDRANT_API_KEY=your-qdrant-secret-key
    GOOGLE_API_KEY=key_1,key_2,key_3
    ```

2.  **Initialize relational schemas:** Run the SQL schema script on your PostgreSQL instance:
    ```bash
    psql -U user -d labharth -f backend/database/migrations/create_ingestion_tables.sql
    ```

3.  **Run knowledge base ingestion:** Execute the ETL script to parse, extract, structure, and index the welfare dataset:
    ```bash
    python -m backend.rag.ingest
    ```
    *Note: The ingest pipeline supports checkpoint-resume. If a run is interrupted, re-running the command resumes extraction without duplicating API usage.*

---

### FastAPI Backend Service

1.  **Configure python virtual environment:**
    ```bash
    cd backend
    python -m venv venv
    
    # Activate virtual environment
    # On Windows:
    .\venv\Scripts\activate
    # On Unix/macOS:
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3.  **Launch the development server:**
    ```bash
    python -m backend.main
    ```
    The FastAPI service boots on `http://localhost:8000`. You can test endpoints via the interactive Swagger docs at `http://localhost:8000/docs`.

---

### Vite React Frontend SPA

1.  **Navigate to the frontend folder and install node modules:**
    ```bash
    cd ../frontend
    npm install
    ```

2.  **Launch the frontend development server:**
    ```bash
    npm run dev
    ```
    The dev server starts on `http://localhost:5173/` (or the next available port, such as `http://localhost:5174/`). Open the address in your browser to interact with the platform.

---

## 🧪 Verification & Testing

The platform includes automated testing tools to verify integration and check performance metrics.

### End-to-End Test Suite
Tests execute within a single event loop using asynchronous HTTP clients to verify API endpoints:
*   Health diagnostics (`GET /health`)
*   Multi-agent orchestrations (`POST /chat`)
*   Prompt injection blocks (`POST /chat` with jailbreaks)
*   Direct search fallbacks (`POST /search`)

To run the E2E suite:
```bash
cd backend
pytest -v backend/tests/test_e2e.py
```

### RAG Retrieval Metrics Evaluator
The golden-dataset evaluator runs multiple queries to measure retrieval relevance, Precision@K, Recall@K, and processing latencies:
```bash
python -m backend.scripts.evaluate_rag
```

**Baseline Performance Metrics:**
*   **Recall@K:** 100.0% (Retrieves all target context schemes)
*   **Precision@K:** 75.0%
*   **Average API Latency:** 2.12s
*   **Duplicate Retrievals:** 0.00%
*   **Response Integrity:** Verified (0.00% hallucinations detected)

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
