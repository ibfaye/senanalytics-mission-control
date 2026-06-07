# Sen'Analytics Mission Control

## Agentic Governance Operating System

**Sen'Analytics Mission Control** is a production-grade visual operating system for governance, compliance, security, risk management, and data engineering operations.

It combines:
- **Multi-agent orchestration** with supervisor-worker pattern
- **React Flow** visual workflow building (n8n-style)
- **LangGraph** execution engine with human-in-the-loop
- **MCP** pluggable tool adapters (Snowflake, Databricks, AWS, Azure, etc.)
- **Neo4j** knowledge graph for lineage and impact analysis
- **Full auditability** with immutable append-only logs
- **Real-time execution monitoring** via WebSockets

---

## Quick Start

### Prerequisites

- Node.js 22+ with pnpm
- Python 3.12+
- Docker & Docker Compose

### Infrastructure

```bash
cd docker
docker compose up -d
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
# Opens on http://localhost:3000
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## Architecture

See `docs/architecture-diagram.html` for a full system architecture diagram.

See `docs/architecture-plan.md` for the complete implementation plan.

---

## Phase Roadmap

| Phase | Deliverable | Status |
|-------|------------|--------|
| 1 | Auth + React Flow canvas + workflow persistence | 🚧 In Progress |
| 2 | LangGraph + supervisor agent + execution engine | ⏳ Planned |
| 3 | Realtime WebSocket streaming + live node animation | ⏳ Planned |
| 4 | MCP integrations (Snowflake, AWS, etc.) | ⏳ Planned |
| 5 | Neo4j knowledge graph + lineage | ⏳ Planned |
| 6 | Compliance reporting + dashboards | ⏳ Planned |
| 7 | Multi-tenant SaaS support | ⏳ Planned |

---

## Technology Stack

**Frontend:** Next.js 16 · TypeScript · React Flow (@xyflow/react) · Tailwind v4 · shadcn/ui · Zustand · TanStack Query

**Backend:** FastAPI · LangGraph · Python 3.12 · Pydantic v2

**Data:** PostgreSQL/Neon · Neo4j · Redis Streams

**Observability:** Langfuse · OpenTelemetry

**Auth:** NextAuth v5

**Deployment:** Docker · Kubernetes-ready

---

## Project Structure

```
senanalytics-mission-control/
├── frontend/          # Next.js 16 + React Flow
├── backend/           # FastAPI + LangGraph
├── docker/            # Docker Compose (PostgreSQL, Neo4j, Redis)
├── docs/              # Architecture docs, diagrams, schemas
└── .hermes/plans/     # Implementation plans
```
