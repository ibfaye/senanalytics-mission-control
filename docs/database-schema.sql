-- ============================================================================
-- Sen'Analytics Mission Control — PostgreSQL Database Schema
-- Phase 1: Foundation tables for workflows, agents, executions, audit
-- ============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- Enums
-- ============================================================================

CREATE TYPE workflow_status AS ENUM ('draft', 'active', 'archived', 'deleted');
CREATE TYPE node_status AS ENUM ('idle', 'running', 'success', 'failed', 'paused');
CREATE TYPE execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'paused', 'cancelled');
CREATE TYPE step_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'changes_requested');
CREATE TYPE audit_action_type AS ENUM (
    'workflow_created', 'workflow_updated', 'workflow_deleted',
    'workflow_executed', 'workflow_paused', 'workflow_resumed',
    'agent_created', 'agent_updated', 'agent_deleted',
    'tool_registered', 'tool_removed',
    'approval_requested', 'approval_granted', 'approval_rejected',
    'node_started', 'node_completed', 'node_failed',
    'user_login', 'user_logout', 'config_changed'
);
CREATE TYPE agent_type AS ENUM (
    'supervisor', 'discovery', 'classification',
    'security', 'compliance', 'risk', 'reporting'
);
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer', 'auditor');
CREATE TYPE knowledge_node_type AS ENUM (
    'data_domain', 'data_product', 'table', 'column',
    'report', 'control', 'policy', 'owner', 'risk', 'incident'
);

-- ============================================================================
-- Organizations (multi-tenant foundation)
-- ============================================================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Users (extended NextAuth user profile)
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    image VARCHAR(500),
    role user_role DEFAULT 'viewer',
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org ON users(organization_id);

-- ============================================================================
-- Workflows
-- ============================================================================

CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status workflow_status DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    organization_id UUID REFERENCES organizations(id),
    created_by UUID NOT NULL REFERENCES users(id),
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_workflows_org ON workflows(organization_id);
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_created ON workflows(created_at DESC);

-- ============================================================================
-- Workflow Nodes (React Flow node state, persisted)
-- ============================================================================

CREATE TABLE workflow_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    node_type VARCHAR(50) NOT NULL CHECK (node_type IN (
        'agent', 'tool', 'workflow', 'approval', 'policy', 'condition', 'trigger'
    )),
    label VARCHAR(255) NOT NULL,
    position_x FLOAT NOT NULL DEFAULT 0,
    position_y FLOAT NOT NULL DEFAULT 0,
    width FLOAT,
    height FLOAT,
    config JSONB DEFAULT '{}',
    status node_status DEFAULT 'idle',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workflow_nodes_wf ON workflow_nodes(workflow_id);

-- ============================================================================
-- Workflow Edges
-- ============================================================================

CREATE TABLE workflow_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    source_node_id UUID NOT NULL REFERENCES workflow_nodes(id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES workflow_nodes(id) ON DELETE CASCADE,
    source_handle VARCHAR(50),
    target_handle VARCHAR(50),
    edge_type VARCHAR(20) DEFAULT 'default' CHECK (edge_type IN (
        'default', 'smoothstep', 'straight', 'step'
    )),
    label VARCHAR(255),
    condition JSONB,
    animated BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_workflow_edges_wf ON workflow_edges(workflow_id);
CREATE INDEX idx_workflow_edges_src ON workflow_edges(source_node_id);
CREATE INDEX idx_workflow_edges_tgt ON workflow_edges(target_node_id);

-- ============================================================================
-- Agent Registry
-- ============================================================================

CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    agent_type agent_type NOT NULL,
    description TEXT,
    system_prompt TEXT,
    model_provider VARCHAR(100),
    model_name VARCHAR(100),
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agents_type ON agents(agent_type);
CREATE INDEX idx_agents_org ON agents(organization_id);

-- ============================================================================
-- Agent Tools (MCP registered tools)
-- ============================================================================

CREATE TABLE agent_tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    description TEXT,
    tool_schema JSONB NOT NULL,
    mcp_server VARCHAR(255),
    mcp_adapter VARCHAR(100),
    rate_limit_per_min INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_id, tool_name)
);

CREATE INDEX idx_agent_tools_agent ON agent_tools(agent_id);

-- ============================================================================
-- Workflow Executions
-- ============================================================================

CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id),
    workflow_version INTEGER,
    status execution_status DEFAULT 'pending',
    triggered_by UUID REFERENCES users(id),
    trigger_type VARCHAR(50) DEFAULT 'manual' CHECK (trigger_type IN (
        'manual', 'scheduled', 'webhook', 'event'
    )),
    input JSONB,
    output JSONB,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    total_tokens INTEGER DEFAULT 0,
    total_cost_cents INTEGER DEFAULT 0,
    error_message TEXT,
    error_stack TEXT,
    execution_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_executions_wf ON workflow_executions(workflow_id);
CREATE INDEX idx_executions_status ON workflow_executions(status);
CREATE INDEX idx_executions_started ON workflow_executions(started_at DESC);

-- ============================================================================
-- Execution Steps
-- ============================================================================

CREATE TABLE execution_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    node_id UUID REFERENCES workflow_nodes(id),
    agent_id UUID REFERENCES agents(id),
    step_order INTEGER NOT NULL DEFAULT 0,
    step_type VARCHAR(50) NOT NULL CHECK (step_type IN (
        'agent_call', 'tool_call', 'approval', 'condition', 'sub_workflow', 'transform'
    )),
    status step_status DEFAULT 'pending',
    input JSONB,
    output JSONB,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    execution_time_ms INTEGER,
    token_usage INTEGER,
    cost_cents INTEGER,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    error_retryable BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_execution_steps_exec ON execution_steps(execution_id);
CREATE INDEX idx_execution_steps_node ON execution_steps(node_id);
CREATE INDEX idx_execution_steps_order ON execution_steps(execution_id, step_order);

-- ============================================================================
-- Approval Checkpoints
-- ============================================================================

CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id),
    step_id UUID NOT NULL REFERENCES execution_steps(id),
    node_id UUID REFERENCES workflow_nodes(id),
    status approval_status DEFAULT 'pending',
    requested_by VARCHAR(255) NOT NULL,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    rejection_reason TEXT,
    changes_requested JSONB,
    timeout_seconds INTEGER DEFAULT 3600,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_approvals_exec ON approvals(execution_id);
CREATE INDEX idx_approvals_status ON approvals(status);

-- ============================================================================
-- Audit Logs (immutable append-only)
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES workflow_executions(id),
    step_id UUID REFERENCES execution_steps(id),
    agent_id UUID REFERENCES agents(id),
    workflow_id UUID REFERENCES workflows(id),
    action VARCHAR(255) NOT NULL,
    action_type audit_action_type NOT NULL,
    actor UUID REFERENCES users(id),
    actor_email VARCHAR(255),
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_execution ON audit_logs(execution_id);
CREATE INDEX idx_audit_action_type ON audit_logs(action_type);
CREATE INDEX idx_audit_actor ON audit_logs(actor);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_workflow ON audit_logs(workflow_id);

-- Prevent modifications to audit logs
CREATE OR REPLACE FUNCTION prevent_audit_update_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit logs are immutable and cannot be modified or deleted';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_no_update
    BEFORE UPDATE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_update_delete();

CREATE TRIGGER trg_audit_no_delete
    BEFORE DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_update_delete();

-- ============================================================================
-- Knowledge Graph Nodes (mirrored in Neo4j)
-- ============================================================================

CREATE TABLE knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_type knowledge_node_type NOT NULL,
    label VARCHAR(255) NOT NULL,
    properties JSONB DEFAULT '{}',
    neo4j_id VARCHAR(100),
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_knowledge_nodes_type ON knowledge_nodes(node_type);
CREATE INDEX idx_knowledge_nodes_org ON knowledge_nodes(organization_id);

-- ============================================================================
-- Knowledge Graph Edges (mirrored in Neo4j)
-- ============================================================================

CREATE TABLE knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    relationship VARCHAR(100) NOT NULL,
    properties JSONB DEFAULT '{}',
    neo4j_rel_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_knowledge_edges_src ON knowledge_edges(source_id);
CREATE INDEX idx_knowledge_edges_tgt ON knowledge_edges(target_id);

-- ============================================================================
-- MCP Server Registry
-- ============================================================================

CREATE TABLE mcp_servers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    adapter_type VARCHAR(100) NOT NULL,
    connection_config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_health_check TIMESTAMPTZ,
    health_status VARCHAR(20),
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Webhook Subscriptions
-- ============================================================================

CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    event_types TEXT[] NOT NULL,
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Notification Preferences
-- ============================================================================

CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type audit_action_type NOT NULL,
    channel VARCHAR(20) DEFAULT 'email' CHECK (channel IN (
        'email', 'in_app', 'webhook', 'slack', 'teams'
    )),
    is_enabled BOOLEAN DEFAULT true,
    UNIQUE(user_id, event_type, channel)
);

-- ============================================================================
-- Functions & Triggers
-- ============================================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_workflows_updated
    BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_agents_updated
    BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_users_updated
    BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_organizations_updated
    BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_knowledge_nodes_updated
    BEFORE UPDATE ON knowledge_nodes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Seed Data: Built-in Agent Definitions
-- ============================================================================

INSERT INTO agents (name, display_name, agent_type, description, is_active) VALUES
    ('supervisor', 'Supervisor Agent', 'supervisor',
     'Orchestrates workflow execution: plans, routes, delegates tasks to specialized agents, manages approval checkpoints, and aggregates results.',
     true),
    ('discovery', 'Discovery Agent', 'discovery',
     'Discovers and catalogs data sources, analyzes schemas, extracts metadata from databases, data warehouses, and lakes.',
     true),
    ('classification', 'Classification Agent', 'classification',
     'Detects and classifies PII, PHI, SPI, and other sensitive data types across all registered data sources.',
     true),
    ('security', 'Security Agent', 'security',
     'Reviews security posture, evaluates IAM policies, identifies vulnerabilities, and assesses encryption configurations.',
     true),
    ('compliance', 'Compliance Agent', 'compliance',
     'Maps data assets to regulatory frameworks: GDPR, CDP (Senegal), PIPEDA, SOC2, ISO 27001. Flags compliance gaps.',
     true),
    ('risk', 'Risk Agent', 'risk',
     'Scores and prioritizes risks based on likelihood and impact. Produces risk heatmaps and remediation priorities.',
     true),
    ('reporting', 'Reporting Agent', 'reporting',
     'Generates executive summaries, audit reports, compliance documentation, and detailed remediation plans.',
     true)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- Seed Data: Default MCP Server Configurations
-- ============================================================================

INSERT INTO mcp_servers (name, adapter_type, connection_config, is_active) VALUES
    ('local-postgres', 'postgres', '{"host": "localhost", "port": 5432, "database": "senanalytics"}', false),
    ('snowflake-default', 'snowflake', '{"account": "", "warehouse": "COMPUTE_WH", "database": ""}', false),
    ('databricks-default', 'databricks', '{"host": "", "token": ""}', false),
    ('aws-default', 'aws', '{"region": "us-east-1", "services": ["s3", "rds", "glue", "athena"]}', false)
ON CONFLICT (name) DO NOTHING;
