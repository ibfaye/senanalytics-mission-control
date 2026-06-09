# Sen'Analytics Mission Control — User Guide

### Agentic Governance Operating System

This guide walks you through every feature of Sen'Analytics Mission Control — from your first login to generating compliance reports.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [The Dashboard](#2-the-dashboard-mission-control)
3. [Building Workflows](#3-building-workflows)
4. [Executing Workflows](#4-executing-workflows)
5. [Managing MCP Connections](#5-managing-mcp-connections)
6. [Exploring the Knowledge Graph](#6-exploring-the-knowledge-graph)
7. [Governance & Security Dashboards](#7-governance--security-dashboards)
8. [Compliance Dashboard](#8-compliance-dashboard)
9. [Generating Reports](#9-generating-reports)
10. [Organization Management](#10-organization-management)
11. [Audit Trail](#11-audit-trail)
12. [API Access](#12-api-access)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Getting Started

### Accessing the Platform

Once deployed, open your browser to the frontend URL:

```
http://localhost:3000/mission-control   (local dev)
https://mission-control.senanalytics.com (production)
```

### Navigation

The left sidebar provides access to all sections:

| Menu Item | What It Does |
|-----------|-------------|
| **Mission Control** | Main dashboard with live stats |
| **Governance** | Data domains, classifications, lineage |
| **Security** | Security findings, risk heatmap |
| **Compliance** | Framework scores (GDPR, CDP, PIPEDA, etc.) |
| **Workflows** | Create and manage governance workflows |
| **Agents** | View the 7-agent mesh |
| **MCP Servers** | Connect external systems |
| **Knowledge Graph** | Explore governance relationships |
| **Reports** | Generate compliance reports |
| **Audit Trail** | Immutable action log |
| **Organization** | Manage team and roles |
| **Profile** | Your account and API context |

---

## 2. The Dashboard (Mission Control)

The Mission Control dashboard gives you a bird's-eye view of your governance operations.

### What You See

- **Active Workflows**: Count of workflows currently running
- **Agents Online**: All 7 agents in the mesh
- **Open Risks**: Critical + High risks from the knowledge graph
- **Compliance Gaps**: PII columns without mapped controls
- **Recent Workflows**: List with status badges (active/draft/archived) and execute buttons

### Live Updates

The dashboard refreshes every 30 seconds. Stats are pulled from the live API — no hardcoded numbers.

---

## 3. Building Workflows

Workflows are the core of Mission Control. They define governance pipelines as visual graphs.

### Creating a Workflow

1. Go to **Workflows** in the sidebar
2. Click **+ New Workflow**
3. Give it a name (e.g., "GDPR Compliance Audit")
4. Click the workflow card to open the canvas

### The Canvas

The workflow canvas is a React Flow editor with:

- **Infinite pan/zoom**: Scroll to move, Ctrl+scroll to zoom
- **Minimap**: Bottom-right corner for navigation
- **Background grid**: Snap-to-grid for alignment

### Adding Nodes

Drag from the toolbar on the left:

| Node | Color | Purpose |
|------|-------|---------|
| 🟢 **Agent** | Green | Runs an AI agent (Discovery, Classification, etc.) |
| 🟡 **Tool** | Yellow | Calls an MCP tool (Snowflake, AWS, etc.) |
| 🟣 **Approval** | Purple (dashed) | Pauses execution for human review |
| 🔵 **Policy** | Blue | References a compliance policy |
| 🟠 **Condition** | Orange | Branching logic |
| 🔷 **Trigger** | Teal | Workflow entry point |

### Connecting Nodes

1. Drag from a node's **output handle** (right side)
2. Drop on another node's **input handle** (left side)
3. Edges auto-animate during execution

### Configuring Nodes

Click any node to open its configuration panel. You can set:
- **Agent type** (for Agent nodes): Which agent to run
- **Description**: What this step does
- **Parameters**: Agent-specific settings

### Saving

Click **Save** in the toolbar to persist your workflow graph to the database.

---

## 4. Executing Workflows

### Starting an Execution

1. Open a workflow canvas
2. Click the green **Execute** button in the toolbar

### What Happens During Execution

The execution runs through the agent pipeline:

```
1. 🔍 Discovery Agent     → Catalogs data sources
2. 🏷️ Classification Agent → Detects PII/sensitive data
3. 🛑 Human Approval       → Waits for your review
4. 📋 Compliance Agent     → Maps to regulations
5. 📊 Reporting Agent      → Generates reports
```

### Live Visualization

As each agent runs, you'll see:
- **Node border pulses green** during execution
- **Node turns solid green** when complete, with metrics
- **Edges animate** with flowing dashes
- **Progress bar** shows "Executing 2/4 agents"

### Approving a Checkpoint

When the pipeline hits an Approval node:
1. A **modal dialog** appears with context from previous agents
2. Review the findings
3. Click **Approve** to continue or **Reject** to stop

You can also approve via API:
```bash
curl -X POST http://localhost:8001/api/approvals/{id}/approve \
  -d '{"decision":"approved"}'
```

### After Completion

A toast notification appears with a summary. Go to **Audit Trail** to see the full execution record.

---

## 5. Managing MCP Connections

MCP (Mission Control Protocol) connects Mission Control to your external systems.

### Connecting a System

1. Go to **MCP Servers** in the sidebar
2. Click any system card (e.g., "Snowflake", "PostgreSQL")
3. The adapter connects and discovers available tools

### Available Systems

| System | Tools | Example Use |
|--------|-------|------------|
| **Snowflake** | 6 | List databases, describe tables, run queries |
| **PostgreSQL** | 6 | Schema discovery, encryption check |
| **AWS** | 7 | S3 encryption, IAM roles, Glue catalogs |
| **Azure** | 7 | Purview scan, Key Vault, Synapse |
| **Jira** | 6 | Compliance tasks, audit trail |
| **Databricks** | 5 | Unity Catalog, lineage, SQL |
| **SQL Server** | 4 | Table discovery, query |
| **ServiceNow** | 4 | Incidents, CMDB |
| **Power BI** | 4 | Reports, datasets |
| **Purview** | 4 | Classifications, lineage |

### Using Tools

Agents automatically discover and use MCP tools. You can also execute tools directly:

```bash
curl -X POST http://localhost:8001/api/mcp/tools/execute \
  -d '{"server_name":"snowflake","tool_name":"snowflake.list_databases","params":{}}'
```

### Demo Mode

Without credentials, adapters connect in demo mode — returning simulated data. Add real credentials to use production systems.

---

## 6. Exploring the Knowledge Graph

The knowledge graph stores governance relationships: what data exists, how it's regulated, what risks it carries.

### Graph Explorer

Go to **Knowledge Graph** to see:

- **Node Types**: Distribution of domains, tables, columns, policies, controls, risks
- **Risk Heatmap**: Top risks by likelihood×impact score, with severity badges
- **Lineage Trace**: Follow a column's full governance chain

### Lineage Example

```
email column → customers table → Customer 360 product → Customer Data domain
       │
       ├── REGULATED_BY → CDP-ART-34 → MAPPED_TO → Control-Enc-01
       ├── REGULATED_BY → GDPR Art.32
       └── HAS_RISK → Unencrypted PII at rest (CRITICAL, 72%)
```

### Compliance Gaps

The graph automatically detects PII columns with no mapped security control:

```
⚠️ email — no encryption control mapped
⚠️ phone — no encryption control mapped
⚠️ address — no control at all
```

### API Queries

```bash
# Trace lineage
curl "http://localhost:8001/api/knowledge/lineage?column=email"

# Get risk heatmap
curl http://localhost:8001/api/knowledge/risks

# Find compliance gaps
curl http://localhost:8001/api/knowledge/compliance/gaps
```

---

## 7. Governance & Security Dashboards

### Governance Dashboard

Shows your data estate:

- **Data Domains**: Customer Data, Analytics, Marketing — with sensitivity levels
- **Column Classifications**: Total, PII, Encrypted PII, Unencrypted PII — with progress bar
- **Lineage Depth**: How many upstream and downstream connections each column has
- **Data Stewardship**: Who owns each domain

### Security Dashboard

Security posture at a glance:

- **Findings**: Encryption gaps, IAM issues, network exposure — with severity badges
- **Risk Heatmap**: Visual score bars for each risk
- **Controls**: How many security controls are implemented vs pending
- **Compliance Gaps**: Unprotected data columns

---

## 8. Compliance Dashboard

Track compliance across 5 regulatory frameworks:

### Framework Score Cards

| Framework | Score | Status |
|-----------|-------|--------|
| GDPR | 78% | Partially Compliant |
| CDP-Senegal | 55% | Non-Compliant |
| PIPEDA | 85% | Partially Compliant |
| SOC2 | 72% | Partially Compliant |
| ISO 27001 | 48% | Non-Compliant |

Each card shows:
- **Score** percentage with color-coded progress bar
- **Gap count**: How many compliance gaps exist
- **Controls implemented**: Security controls mapped to this framework

### Detail Table

The full table below the cards shows:
- Framework name, score, status badge
- Number of gaps, policies mapped, controls implemented
- Last audit date

---

## 9. Generating Reports

Generate audit-ready documentation with one click.

### Report Types

| Report | Content | Use Case |
|--------|---------|----------|
| **Executive Summary** | Overview, risk summary, critical actions | Board presentations |
| **Audit Report** | Detailed findings, evidence, risk assessment | Compliance audits |
| **Remediation Plan** | Prioritized action items with deadlines | Engineering backlog |

### Generating a Report

1. Go to **Reports**
2. Click any report type card
3. The report is generated instantly

### Downloading

Each report can be downloaded as:
- **TXT**: Plain text for sharing
- **JSON**: Machine-readable for integration

### Report Contents

**Executive Summary** includes:
```
Overview: Governance audit across 29 assets. 3 risks, 3 compliance gaps.
Risk Summary: 3 total risks, 1 critical
Top Risks: Unencrypted PII (72%), Cross-border transfer (51%), IAM roles (35%)
Critical Actions:
  1. Enable TDE encryption on customer PII
  2. Submit cross-border transfer authorization
  3. Apply least-privilege IAM policy
```

**Audit Report** includes:
- Scope definition
- Findings with severity, description, regulation, and evidence
- Risk assessment
- Remediation items with priorities and deadlines

---

## 10. Organization Management

Mission Control supports multi-tenant operation with role-based access control.

### Viewing Your Organization

Go to **Organization** to see:
- Organization name, plan, member count
- Your role and permissions
- Member list with role badges

### Roles

| Role | Capabilities |
|------|-------------|
| **Admin** | Full access: manage org, users, workflows, MCP, reports |
| **Editor** | Create/edit workflows, execute, generate reports, resolve approvals |
| **Viewer** | Read-only: view workflows, dashboards, audit trail |
| **Auditor** | Read audit trail, generate reports, view all data |

### Managing Members

Admins can:
- **Add members** with specific roles
- **Remove members**
- **Change roles** (promote Viewer → Editor, etc.)

### Profile

Go to **Profile** to see:
- Your name, email, role
- Organization context
- API headers used for multi-tenant scoping

---

## 11. Audit Trail

Every action in Mission Control is logged immutably.

### What's Logged

| Event | Details |
|-------|---------|
| Workflow created/updated/deleted | Who, when, what changed |
| Workflow executed | Trigger, duration, outcome |
| Agent started/completed/failed | Tokens, cost, confidence |
| Approval requested/granted/rejected | Decision, reason, approver |
| MCP server connected | System, tools discovered |
| Report generated | Type, format |

### Accessing the Audit Trail

Go to **Audit Trail** in the sidebar. Records are append-only — they cannot be modified or deleted (enforced at the database level with a trigger).

---

## 12. API Access

All features are available via REST API. Full OpenAPI docs at:

```
http://localhost:8001/docs
```

### Authentication

Currently, requests use header-based identification:

```bash
curl -H "X-User-Id: user-ibfaye" \
     -H "X-Org-Id: senanalytics-org" \
     http://localhost:8001/api/workflows
```

### WebSocket Streaming

Connect to live execution events:

```javascript
const ws = new WebSocket("ws://localhost:8001/ws/workflows/wf-001");

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // msg.event: "node.started" | "node.completed" | "approval.requested" | ...
  // msg.data: { nodeId, executionId, metrics, ... }
};

// Send approval
ws.send(JSON.stringify({
  action: "approval.respond",
  data: { approvalId: "...", decision: "approved" }
}));
```

---

## 13. Troubleshooting

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Pages return 404 | Frontend not running | `cd frontend && pnpm dev` |
| "Backend unreachable" | Backend not running | `uvicorn app.main:app --port 8001` |
| "Cannot connect to database" | PostgreSQL not started | `cd docker && docker compose up -d postgres` |
| WebSocket fails | Port mismatch or CORS | Ensure backend is on 8001, frontend on 3000 |
| Execute button does nothing | No workflow nodes | Add nodes to the canvas and save first |
| Approval dialog doesn't appear | WebSocket not connected | Check browser console for WS errors |

### Health Check

```bash
curl http://localhost:8001/api/health
```

Response:
```json
{
  "status": "operational",
  "version": "0.2.0",
  "postgres": "connected",
  "neo4j": "connected"
}
```

### Restarting Everything

```bash
# Stop all
docker compose down
cd docker && docker compose down

# Start fresh
cd docker && docker compose up -d
cd .. && uvicorn app.main:app --port 8001 &
cd frontend && pnpm dev --turbopack -p 3000
```
