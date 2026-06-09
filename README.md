# Sen'Analytics Mission Control

### Agentic Governance Operating System

**Sen'Analytics Mission Control** is a production-grade visual operating system for governance, compliance, security, risk management, and data engineering operations — built for Senegal and Francophone West Africa.

It combines multi-agent orchestration, visual workflow building (n8n-style), real-time execution monitoring (Datadog-style), and comprehensive auditability (Purview-style) into a single platform.

---

## Table of Contents

- [Quick Start](#quick-start)
- [What It Does](#what-it-does)
- [Architecture](#architecture)
- [Screen-by-Screen](#screen-by-screen)
- [Agent Mesh](#agent-mesh)
- [MCP Tool Layer](#mcp-tool-layer)
- [Knowledge Graph](#knowledge-graph)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Project Stats](#project-stats)
- [Documentation](#documentation)

---

## What It Does

| Capability | Description |
|-----------|-------------|
| **Agent Orchestration** | 7 specialized AI agents (Supervisor → Discovery → Classification → Security → Compliance → Risk → Reporting) working through a supervisor-worker pipeline with human-in-the-loop approval checkpoints |
| **Visual Workflows** | Drag-and-drop React Flow canvas with 6 custom node types (Agent, Tool, Approval, Policy, Condition, Trigger). Build governance pipelines visually |
| **Real-Time Monitoring** | WebSocket-driven live execution streaming — nodes pulse green during execution, edges animate, metrics update in real-time |
| **MCP Integrations** | Pluggable tool adapters for Snowflake, PostgreSQL, AWS, Azure, Databricks, Jira, ServiceNow, Power BI, Microsoft Purview, and SQL Server — 53 discoverable tools across 10 systems |
| **Knowledge Graph** | Neo4j-powered governance graph — 29 nodes, 31 relationships, full lineage tracing, impact analysis, compliance mapping |
| **Compliance Reporting** | Auto-generated executive summaries, audit reports, and remediation plans. Downloadable as TXT/JSON |
| **Multi-Tenant RBAC** | Organization isolation with 4 roles (Admin, Editor, Viewer, Auditor), granular permissions |
| **Full Auditability** | Immutable append-only audit logs, replayable workflows, traceable agent decisions |

---

## Quick Start

### Prerequisites

- **Docker** + Docker Compose v2+
- **Python 3.12+** + venv
- **Node.js 22+** + pnpm
- **Git**

### 60-Second Start

```bash
# 1. Clone
git clone https://github.com/ibfaye/senanalytics-mission-control.git
cd senanalytics-mission-control

# 2. Infrastructure (once)
cd docker && docker compose up -d

# 3. Backend
cd ../backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Frontend (new terminal)
cd ../frontend && pnpm install && pnpm dev --turbopack -p 3000

# 5. Open
open http://localhost:3000/mission-control
```

### URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Mission Control | http://localhost:3000 | — |
| API Docs (Swagger) | http://localhost:8001/docs | — |
| pgAdmin | http://localhost:5050 | admin@senanalytics.com / admin |
| Neo4j Browser | http://localhost:7474 | neo4j / senanalytics_dev |

---

## Architecture

### System Layers

```
┌─────────────────────────────────────────────┐
│ L6 · Next.js 16 + React Flow Canvas          │ Frontend (15 pages)
├─────────────────────────────────────────────┤
│ L5 · FastAPI + WebSocket Server              │ API Gateway (47 endpoints)
├─────────────────────────────────────────────┤
│ L4 · Agent Mesh (7 agents, direct calls)     │ Orchestration
├─────────────────────────────────────────────┤
│ L3 · MCP Tool Layer (10 adapters)            │ External Systems
├─────────────────────────────────────────────┤
│ L2 · Neo4j · PostgreSQL · Redis              │ Data Layer
├─────────────────────────────────────────────┤
│ L1 · Docker · Kubernetes                     │ Infrastructure
└─────────────────────────────────────────────┘
```

### Data Flow

```
User → Canvas → REST API → Engine → Agent Mesh → MCP Tools → External Systems
                    ↑                        ↓
                    └── WebSocket ←── Live Status (node.started/completed/failed)
```

---

## Screen-by-Screen

### 1. Mission Control (`/mission-control`)
The main dashboard. Shows active workflows, running agents, live stats (executions, agents, costs, risks). Stats grid, recent workflow list with status badges, execute button per workflow.

### 2. Workflows (`/workflows`)
List all governance workflows with create, edit, and delete. Click any workflow to open the canvas.

### 3. Workflow Canvas (`/workflows/[id]`)
The central experience — a React Flow canvas with:
- **Toolbar**: Drag-and-drop node palette (Agent, Tool, Approval, Policy, Condition, Trigger) + Save/Execute buttons
- **Canvas**: Infinite pan/zoom, minimap, background grid
- **Live Execution**: Nodes animate during execution — pulsing green border → solid green with metrics
- **Approval Dialog**: Modal overlay when execution hits a human checkpoint
- **Progress Bar**: Shows "Executing 2/4 agents" during runs

### 4. Agents (`/agents`)
Registry of all 7 agents with type badges, descriptions, and status indicators.

### 5. MCP Servers (`/mcp`)
Connect external systems. Shows all 10 supported adapters with connection status, tool discovery (53 tools), connect/disconnect buttons, and a system grid with status indicators.

### 6. Knowledge Graph (`/knowledge`)
Graph explorer showing:
- Node type distribution (Domains, Tables, Columns, Policies, Controls, Risks)
- Risk heatmap with likelihood×impact score bars
- **Lineage trace**: Customer Data → Customer 360 → customers → email → CDP-ART-34 → Control-Enc-01
- Compliance gaps: PII columns with no mapped control

### 7. Governance Dashboard (`/governance`)
Data domains, products, classification stats, PII encryption status, lineage depth, data stewardship.

### 8. Security Dashboard (`/security`)
Security findings (encryption, IAM, network), risk heatmap with severity badges, compliance gap counts, control implementation status.

### 9. Compliance Dashboard (`/compliance`)
5-framework score cards (GDPR, CDP-Senegal, PIPEDA, SOC2, ISO27001) with status, gap counts, policy/control mappings, and a detail table.

### 10. Reports (`/reports`)
Generate 3 report types: Executive Summary, Audit Report, Remediation Plan. Download as TXT or JSON. Reports include findings, risk assessments, and prioritized action items.

### 11. Audit Trail (`/audit`)
Immutable log of all actions — workflow executions, agent decisions, approval events.

### 12. Organization (`/organization`)
Multi-tenant management — view org, members with role badges (Admin/Editor/Viewer/Auditor), RBAC permission reference grid.

### 13. Profile (`/profile`)
User profile with role, organization context, and API header display for multi-tenant scoping.

---

## Agent Mesh

### Supervisor-Worker Pipeline

```
┌──────────────┐
│  Supervisor  │  Plans → Routes → Delegates → Aggregates
└──────┬───────┘
       │
  ┌────┴────────────────────────────┐
  │                                  │
  ▼                                  ▼
┌──────────┐                   ┌──────────────┐
│ Discovery │                   │Classification│
│ 3 sources │                   │ 12 PII fields │
└────┬─────┘                   └──────┬───────┘
     │                                │
     └────────┬───────────────────────┘
              ▼
        ┌──────────┐
        │ 🛑 Human  │  ← Approval checkpoint
        │ Approval  │
        └────┬─────┘
             │
        ┌────┴────┐
        ▼         ▼
   ┌─────────┐ ┌──────────┐
   │Compliance│ │Reporting │
   │5 frameworks│ │3 reports │
   └─────────┘ └──────────┘
```

### Verified Run
```
✅ Discovery:       450ms, 320 tok, $0.01
✅ Classification:  680ms, 540 tok, $0.02
🛑 Human Approval: Paused → Resolved via API
✅ Compliance:      750ms, 610 tok, $0.02
✅ Reporting:       380ms, 290 tok, $0.01
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 1,760 tokens · $0.06 · 2,260ms
```

---

## MCP Tool Layer

### 10 System Adapters — 53 Discoverable Tools

| Adapter | Tools | Key Capabilities |
|---------|-------|-----------------|
| **Snowflake** | 6 | List databases, schemas, tables, describe tables, run queries |
| **PostgreSQL** | 6 | List DBs, schemas, tables, encryption check, query |
| **AWS** | 7 | S3 buckets, RDS, Glue, Athena, IAM roles, encryption |
| **Azure** | 7 | Storage, SQL DB, Purview assets, Synapse, Key Vault |
| **Jira** | 6 | Projects, issues, compliance tasks, audit trail |
| **Databricks** | 5 | Clusters, jobs, Unity Catalog, SQL, lineage |
| **SQL Server** | 4 | Databases, tables, describe, query |
| **ServiceNow** | 4 | Incidents, CMDB, change requests |
| **Power BI** | 4 | Workspaces, reports, datasets, sources |
| **Purview** | 4 | Search, classifications, lineage, scan status |

### Architecture
```
Agent → MCP Registry → Adapter → External System
         │
    ┌────┴────┐
    │ Registry │
    │ 10 types │
    │ CRUD API │
    │ Tool Exec│
    └─────────┘
```

---

## Knowledge Graph

### Graph Model — 29 Nodes, 31 Relationships

```
Customer Data ──→ Customer 360 ──→ customers ──→ email
                                                  │
                       ┌──────────────────────────┼──────────────────────┐
                       ▼                          ▼                      ▼
                 CDP-ART-34                  GDPR Art.32           CDP-ART-49
                       │                          │                      │
                       ▼                          ▼                      ▼
                 Control-Enc-01                                   Control-CB-03
                       │
                       ▼
                 Unencrypted PII at rest
                 (CRITICAL, score 0.72)
```

### Key Queries
- **Lineage**: Trace a column's full governance context (table → product → domain → policy → control → risk)
- **Impact Analysis**: Find all assets affected if a policy changes
- **Compliance Gaps**: PII columns with no mapped security control
- **Risk Heatmap**: Top risks by likelihood×impact score

---

## API Reference

Full Swagger docs at `http://localhost:8001/docs`

### Core Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check (PG + Neo4j status) |
| GET | `/api/workflows` | List workflows |
| GET | `/api/workflows/:id` | Get workflow with nodes/edges |
| POST | `/api/workflows/:id/execute` | Execute a workflow |
| GET | `/api/executions` | List executions |
| GET | `/api/agents` | List registered agents |
| GET | `/api/approvals` | List pending approvals |
| POST | `/api/approvals/:id/approve` | Approve a checkpoint |
| WS | `/ws/workflows/:id` | Live execution streaming |

### Dashboard Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboards/mission-control` | Main dashboard stats |
| GET | `/api/dashboards/governance` | Governance metrics |
| GET | `/api/dashboards/security` | Security findings + risks |
| GET | `/api/dashboards/compliance` | Framework scores + gaps |

### Knowledge Graph Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/knowledge/summary` | Graph statistics |
| GET | `/api/knowledge/lineage?column=email` | Full lineage trace |
| GET | `/api/knowledge/risks` | Risk heatmap |
| GET | `/api/knowledge/compliance/gaps` | Unprotected PII columns |

### MCP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/mcp/adapters` | List available adapters |
| GET | `/api/mcp/servers` | List connected servers |
| POST | `/api/mcp/servers` | Connect a new server |
| POST | `/api/mcp/tools/execute` | Execute a tool |

### Organization Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/organizations/` | List organizations |
| GET | `/api/organizations/current` | Current user context |
| GET | `/api/organizations/:id/members` | List members with roles |

### Reports Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/reports` | List generated reports |
| POST | `/api/reports/generate/executive-summary` | Generate executive summary |
| GET | `/api/reports/:id/download` | Download as TXT/JSON |

---

## Configuration

All configuration via environment variables in `backend/.env`:

```bash
# Server
BACKEND_URL=http://localhost:8001
FRONTEND_URL=http://localhost:3000
HOST=0.0.0.0
PORT=8001

# Databases
DATABASE_URL=postgresql://senanalytics:***@localhost:5432/senanalytics
NEO4J_URI=bolt://localhost:7687
REDIS_URL=redis://localhost:6379

# LLM (optional — without it, agents use simulated data)
LLM_API_KEY=sk-***
LLM_MODEL=gpt-4o-mini
```

---

## Deployment

### Local Development
```bash
cd docker && docker compose up -d         # Infrastructure
cd backend && uvicorn app.main:app --port 8001  # Backend
cd frontend && pnpm dev --turbopack -p 3000     # Frontend
```

### Docker Compose
```bash
docker compose up -d                      # All services
```

### Kubernetes
```bash
kubectl apply -f k8s/                     # Full cluster deploy
kubectl -n senanalytics get pods,svc,ingress
```

---

## Project Stats

| Metric | Value |
|--------|-------|
| **Total files** | 107 |
| **Total lines** | 14,492 |
| **Python** | 48 files · 5,522 lines |
| **TSX/TS** | 39 files · 4,118 lines |
| **YAML** | 13 files · 2,969 lines |
| **Backend routes** | 47 endpoints |
| **Frontend pages** | 14 routes |
| **Docker images** | 2 (backend 389MB, frontend 283MB) |
| **K8s manifests** | 9 files |

---

## Documentation

| Document | Path |
|----------|------|
| **User Guide** | [docs/USER_GUIDE.md](docs/USER_GUIDE.md) |
| **Architecture Diagram** | [docs/architecture-diagram.html](docs/architecture-diagram.html) |
| **Database Schema** | [docs/database-schema.sql](docs/database-schema.sql) |
| **Knowledge Graph Schema** | [docs/knowledge-graph-schema.md](docs/knowledge-graph-schema.md) |
| **Event Model & API** | [docs/event-model-api.md](docs/event-model-api.md) |

---

## License

Proprietary — Sen'Analytics. Built for data governance in Senegal and Francophone West Africa.
