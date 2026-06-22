# LabhArth AI — Project Blueprint

## 1. Vision Statement

LabhArth AI is an **Agentic RAG platform** that bridges the information gap between Indian citizens and government welfare schemes. Using multi-agent AI architecture, it provides personalized scheme discovery, eligibility determination, document guidance, and application assistance.

## 2. Problem Statement

India has **500+ central and state government welfare schemes**, but:
- Citizens are unaware of schemes they qualify for
- Eligibility criteria are scattered across multiple portals
- Document requirements are unclear and frequently change
- Application processes vary by scheme and are often opaque

**LabhArth AI solves this** by providing a single conversational interface powered by agentic AI that understands a citizen's profile and proactively matches them with relevant schemes.

## 3. Target Users

| User Segment | Description |
|---|---|
| Citizens | Individuals seeking government benefits |
| NGO Workers | Field workers helping beneficiaries apply |
| Government Officials | Administrators monitoring scheme reach |

## 4. Core Features (MVP)

### 4.1 Conversational Scheme Discovery
- Natural language queries: *"What schemes can a farmer in UP get?"*
- Multi-turn conversations with context retention
- Proactive suggestions based on user profile

### 4.2 Eligibility Determination
- Profile-based eligibility matching
- Clear YES/NO with reasoning
- Gap analysis: what criteria are missing

### 4.3 Document Guidance
- Scheme-specific document checklists
- Alternative document suggestions
- Document preparation tips

### 4.4 Application Guidance
- Step-by-step application walkthroughs
- Portal links and offline office locations
- Status tracking guidance

### 4.5 Data Ingestion
- Government scheme data loaded from the `shrijayan/gov_myscheme` HuggingFace dataset
- 723 PDF documents extracted from MyScheme.gov.in, each containing structured scheme information
- PDFs parsed, cleaned, and normalized into a canonical format
- Section-based chunking (overview, eligibility, benefits, documents, application)
- Gemini embeddings generated and indexed into Qdrant Cloud
- Structured metadata stored in PostgreSQL for filtering and traceability

## 5. Technical Highlights

| Component | Technology | Purpose |
|---|---|---|
| Data Source | [shrijayan/gov_myscheme](https://huggingface.co/datasets/shrijayan/gov_myscheme) (HuggingFace) | 723 structured government scheme PDFs from MyScheme.gov.in |
| Agent Framework | Google ADK | Multi-agent orchestration |
| LLM | Gemini 2.5 Flash | Reasoning & generation |
| Embedding Model | Gemini text-embedding-004 | 768-dim vectors for semantic search |
| Tool Protocol | MCP | Standardized tool access |
| Vector Store | Qdrant Cloud | Semantic search over scheme embeddings |
| Database | PostgreSQL (Neon) | Structured data, chunk tracking, audit trail |
| Backend | FastAPI | REST API server |
| Frontend | React + Vite | User interface |
| Deployment | Railway + Docker | Production hosting |

## 6. Success Metrics

- **Scheme Match Accuracy:** ≥ 85% precision in scheme recommendations
- **Eligibility Accuracy:** ≥ 90% correct eligibility determinations
- **Response Latency:** < 3 seconds for scheme search, < 5 seconds for eligibility checks
- **User Satisfaction:** Qualitative feedback from demo sessions

## 7. Kaggle Capstone Demonstration Checklist

- [x] Google ADK — Multi-agent architecture with Orchestrator, Profile, Search, Eligibility agents
- [x] Multi-Agent Architecture — Four specialized agents with clear responsibilities
- [x] MCP (Model Context Protocol) — Five MCP tools: search_schemes, get_scheme_details, check_eligibility, get_profile, save_profile
- [x] Agent Skills — Each agent has defined skills and tool bindings
- [x] Gemini Models — Gemini 2.5 Flash for reasoning, text-embedding-004 for embeddings
- [x] Security — API key auth, rate limiting, input sanitization
- [x] Deployability — Docker + Railway deployment pipeline
- [x] Agentic RAG — PDF ingestion → section chunking → vector search → LLM reasoning pipeline

## 8. Non-Goals (v1)

- Multi-language support (Hindi, etc.) — future version
- Mobile app — web-only for MVP
- Real-time scheme status tracking
- Government portal integration (OAuth)
- Payment/transaction processing
- Hybrid search (BM25 + vector) — future optimization

## 9. Implementation Phases

### Phase 0: Data Preparation
- Source and analyze the `shrijayan/gov_myscheme` HuggingFace dataset
- Build PDF text extraction pipeline
- Define canonical data format for ingestion

### Phase 1: Foundation
- Project scaffold ✅
- Database schema (including `scheme_chunks` and `ingestion_runs` tables)
- Qdrant collection creation with payload indexes
- Data ingestion pipeline (parse → clean → chunk → embed → index)

### Phase 2: RAG Pipeline
- Embedding generation with Gemini text-embedding-004
- Qdrant retrieval with metadata filtering
- Context formatting and LLM augmentation

### Phase 3: Core Agents
- Implement Orchestrator Agent (ADK)
- Implement Profile Agent with `get_profile` / `save_profile` tools
- Implement Scheme Search Agent with `search_schemes` / `get_scheme_details` tools
- Implement Eligibility Agent with `check_eligibility` tool

### Phase 4: MCP Integration
- MCP server setup
- Wire tools to services and RAG pipeline
- Agent-tool bindings

### Phase 5: Frontend
- Chat interface
- Scheme browsing UI
- Eligibility form

### Phase 6: Polish & Deploy
- Security hardening
- Performance optimization
- Railway deployment
- Demo preparation
