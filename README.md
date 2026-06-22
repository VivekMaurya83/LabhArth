# 🇮🇳 LabhArth AI

> **Agentic RAG platform** that helps Indian citizens discover government welfare schemes, determine eligibility, understand required documents, and receive step-by-step application guidance.

Built for the **Kaggle AI Agents: Intensive Vibe Coding Capstone Project**.

---

## ✨ Key Capabilities

| Capability | Description |
|---|---|
| **Scheme Discovery** | Search and explore 720+ central & state government schemes |
| **Eligibility Check** | AI-powered eligibility determination based on user profile |
| **Document Guidance** | Know exactly which documents you need |
| **Application Help** | Step-by-step guidance through the application process |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│               React Frontend                │
│          (Vite + React Router)              │
└─────────────┬───────────────────────────────┘
              │ REST API
┌─────────────▼───────────────────────────────┐
│            FastAPI Backend                  │
│  ┌─────────────────────────────────────┐    │
│  │       Orchestrator Agent (ADK)      │    │
│  │  ┌──────────┬──────────┬─────────┐  │    │
│  │  │ Profile  │ Scheme   │Eligibil.│  │    │
│  │  │ Agent    │ Search   │ Agent   │  │    │
│  │  └──────────┴──────────┴─────────┘  │    │
│  └──────────────┬──────────────────────┘    │
│                 │ MCP Tools                  │
│  ┌──────────────▼──────────────────────┐    │
│  │  search_schemes   │ get_details     │    │
│  │  check_eligibility                  │    │
│  │  get_profile      │ save_profile    │    │
│  └──────────────┬──────────────────────┘    │
│                 │                            │
│  ┌──────────────▼──────────────────────┐    │
│  │          RAG Pipeline               │    │
│  │   Embeddings → Retriever → Ranker   │    │
│  └──────────────┬──────────────────────┘    │
└─────────────────┼───────────────────────────┘
          ┌───────┴───────┐
    ┌─────▼─────┐   ┌────▼────┐
    │ PostgreSQL │   │ Qdrant  │
    │  (Neon)    │   │ Cloud   │
    └───────────┘   └─────────┘
```

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, Google ADK, MCP
- **Frontend:** React 18, Vite, React Router
- **AI:** Gemini 2.5 Flash, Agentic RAG
- **Databases:** PostgreSQL (Neon), Qdrant Cloud
- **Deployment:** Railway, Docker

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google API Key

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # Fill in your keys
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
LabhArth/
├── backend/          # FastAPI + ADK + MCP
│   ├── agents/       # Google ADK agent definitions
│   ├── api/          # REST API routes
│   ├── mcp/          # MCP server & tools
│   ├── rag/          # RAG pipeline components
│   ├── services/     # Business logic layer
│   ├── database/     # DB connections & repositories
│   ├── models/       # Pydantic schemas & ORM models
│   ├── security/     # Auth & rate limiting
│   └── utils/        # Config, logging, helpers
├── frontend/         # React + Vite SPA
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── hooks/
├── docs/             # Architecture & design docs
└── docker-compose.yml
```

## 📜 License

This project is licensed under the MIT License.
