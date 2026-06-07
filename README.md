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

### System Layers

```
┌─────────────────────────────────────────────┐
│  L6 · Next.js 16 + React Flow Canvas        │  Frontend
├─────────────────────────────────────────────┤
│  L5 · FastAPI + WebSocket Server            │  API Gateway
├─────────────────────────────────────────────┤
│  L4 · LangGraph Runtime (8-node graph)      │  Orchestration
│       Supervisor → 6 Worker Agents          │
├─────────────────────────────────────────────┤
│  L3 · MCP Tool Layer (10 adapters)          │  Tool Adapters
├─────────────────────────────────────────────┤
│  L2 · Snowflake · Databricks · AWS · Azure  │  External Systems
├─────────────────────────────────────────────┤
│  L1 · PostgreSQL · Neo4j · Redis            │  Data Stores
└─────────────────────────────────────────────┘
```

### Agent Mesh

| Agent | Role | Status |
|-------|------|--------|
| **Supervisor** | Plans, routes, delegates, aggregates results | ✅ Active |
| **Discovery** | Catalogs data sources, analyzes schemas | ✅ Active |
| **Classification** | Detects PII, PHI, SPI, sensitive data | ✅ Active |
| **Security** | Reviews IAM, encryption, vulnerabilities | ✅ Active |
| **Compliance** | Maps to GDPR, CDP, PIPEDA, SOC2, ISO 27001 | ✅ Active |
| **Risk** | Scores risks (likelihood × impact), prioritizes | ✅ Active |
| **Reporting** | Executive summaries, audit reports, plans | ✅ Active |

### Verified Execution Run

```
✅ Discovery:      450ms, 320 tok, $0.01  → 3 data sources found
✅ Classification: 680ms, 540 tok, $0.02  → 12 PII fields detected
🛑 Human Approval: Paused → Resolved via API
✅ Compliance:     750ms, 610 tok, $0.02  → 5 frameworks mapped
✅ Reporting:      380ms, 290 tok, $0.01  → 3 reports generated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Total: 1,760 tokens · $0.06 · 2,260ms
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/workflows` | List workflows |
| GET | `/api/workflows/:id` | Get workflow with nodes/edges |
| POST | `/api/workflows/:id/execute` | Execute a workflow |
| GET | `/api/executions` | List recent executions |
| GET | `/api/executions/:id` | Get execution with steps |
| GET | `/api/agents` | List registered agents |
| GET | `/api/approvals` | List pending approvals |
| POST | `/api/approvals/:id/approve` | Approve a checkpoint |
| POST | `/api/approvals/:id/reject` | Reject a checkpoint |
| WS | `/ws/workflows/:id` | Live WebSocket streaming |

---

## Phase Roadmap

| Phase | Deliverable | Status |
|-------|------------|--------|
| 1 | Auth + React Flow canvas + workflow persistence | ✅ Complete |
| 2 | LangGraph + supervisor agent + execution engine | ✅ Complete |
| 3 | Realtime WebSocket streaming + live node animation | 🚧 In Progress |
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
├── frontend/
│   ├── app/(dashboard)/         # Mission Control, Governance, Security, etc.
│   │   └── workflows/[id]/      # React Flow canvas page
│   ├── components/flow/         # Custom nodes (Agent, Tool, Approval, etc.)
│   ├── components/layout/       # Sidebar, Header, Shell
│   ├── lib/stores/              # Zustand (workflow, agent, execution, UI)
│   ├── lib/hooks/               # TanStack Query + WebSocket
│   ├── lib/types/               # TypeScript type system
│   └── lib/api/                 # API client + endpoints
├── backend/
│   ├── app/agents/              # 7 LangGraph agents (supervisor + 6 workers)
│   ├── app/graphs/              # StateGraph with supervisor-worker routing
│   ├── app/core/                # Execution engine, WebSocket, event bus
│   ├── app/api/                 # REST endpoints (executions, approvals, agents)
│   └── app/schemas/             # Pydantic models
├── docker/                      # Docker Compose (PostgreSQL, Neo4j, Redis)
└── docs/                        # Architecture diagram, DB schema, API contracts
```
