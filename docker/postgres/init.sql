-- Sen'Analytics Mission Control — PostgreSQL Init
-- This script runs once when the container is first created.

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
DO $$ BEGIN
    CREATE TYPE workflow_status AS ENUM ('draft', 'active', 'archived', 'deleted');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE node_status AS ENUM ('idle', 'running', 'success', 'failed', 'paused');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'paused', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE step_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected', 'changes_requested');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE audit_action_type AS ENUM (
        'workflow_created', 'workflow_updated', 'workflow_deleted',
        'workflow_executed', 'workflow_paused', 'workflow_resumed',
        'agent_created', 'agent_updated', 'agent_deleted',
        'tool_registered', 'tool_removed',
        'approval_requested', 'approval_granted', 'approval_rejected',
        'node_started', 'node_completed', 'node_failed',
        'user_login', 'user_logout', 'config_changed'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE agent_type AS ENUM (
        'supervisor', 'discovery', 'classification',
        'security', 'compliance', 'risk', 'reporting'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer', 'auditor');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE knowledge_node_type AS ENUM (
        'data_domain', 'data_product', 'table', 'column',
        'report', 'control', 'policy', 'owner', 'risk', 'incident'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE IF NOT EXISTS users (
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

-- Seed default org
INSERT INTO organizations (id, name, slug) VALUES
    (gen_random_uuid(), 'Sen''Analytics', 'senanalytics')
ON CONFLICT (slug) DO NOTHING;

-- Seed admin user
INSERT INTO users (email, name, role, organization_id) 
SELECT 'iboufaye2000@hotmail.com', 'Ibrahim Faye', 'admin', id
FROM organizations WHERE slug = 'senanalytics'
ON CONFLICT (email) DO NOTHING;

-- Workflows
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status workflow_status DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    organization_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id),
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Workflow Nodes
CREATE TABLE IF NOT EXISTS workflow_nodes (
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

-- Workflow Edges
CREATE TABLE IF NOT EXISTS workflow_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    source_node_id UUID NOT NULL REFERENCES workflow_nodes(id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES workflow_nodes(id) ON DELETE CASCADE,
    source_handle VARCHAR(50),
    target_handle VARCHAR(50),
    edge_type VARCHAR(20) DEFAULT 'default',
    label VARCHAR(255),
    condition JSONB,
    animated BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agents
CREATE TABLE IF NOT EXISTS agents (
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

-- Workflow Executions
CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id),
    workflow_version INTEGER,
    status execution_status DEFAULT 'pending',
    triggered_by UUID REFERENCES users(id),
    trigger_type VARCHAR(50) DEFAULT 'manual',
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

-- Execution Steps
CREATE TABLE IF NOT EXISTS execution_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(id) ON DELETE CASCADE,
    node_id UUID REFERENCES workflow_nodes(id),
    agent_id UUID REFERENCES agents(id),
    step_order INTEGER NOT NULL DEFAULT 0,
    step_type VARCHAR(50) NOT NULL,
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

-- Approvals
CREATE TABLE IF NOT EXISTS approvals (
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

-- Audit Logs (immutable)
CREATE TABLE IF NOT EXISTS audit_logs (
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

-- MCP Servers
CREATE TABLE IF NOT EXISTS mcp_servers (
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

-- Knowledge Graph Nodes (mirrored in Neo4j)
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_type knowledge_node_type NOT NULL,
    label VARCHAR(255) NOT NULL,
    properties JSONB DEFAULT '{}',
    neo4j_id VARCHAR(100),
    organization_id UUID REFERENCES organizations(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge Graph Edges
CREATE TABLE IF NOT EXISTS knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES knowledge_nodes(id) ON DELETE CASCADE,
    relationship VARCHAR(100) NOT NULL,
    properties JSONB DEFAULT '{}',
    neo4j_rel_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_org ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_workflows_org ON workflows(organization_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_executions_wf ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);

-- Seed Agents
INSERT INTO agents (name, display_name, agent_type, description, is_active) VALUES
    ('supervisor', 'Supervisor Agent', 'supervisor', 'Orchestrates workflow execution', true),
    ('discovery', 'Discovery Agent', 'discovery', 'Discovers and catalogs data sources', true),
    ('classification', 'Classification Agent', 'classification', 'Detects PII and sensitive data', true),
    ('security', 'Security Agent', 'security', 'Reviews security posture and IAM', true),
    ('compliance', 'Compliance Agent', 'compliance', 'Maps data to regulatory frameworks', true),
    ('risk', 'Risk Agent', 'risk', 'Scores and prioritizes risks', true),
    ('reporting', 'Reporting Agent', 'reporting', 'Generates audit and compliance reports', true)
ON CONFLICT (name) DO NOTHING;

-- Seed MCP Servers
INSERT INTO mcp_servers (name, adapter_type, connection_config, is_active) VALUES
    ('local-postgres', 'postgres', '{"host": "localhost", "port": 5432, "database": "senanalytics"}', false),
    ('snowflake-default', 'snowflake', '{"account": "", "warehouse": "COMPUTE_WH", "database": ""}', false),
    ('databricks-default', 'databricks', '{"host": "", "token": ""}', false),
    ('aws-default', 'aws', '{"region": "us-east-1", "services": ["s3", "rds", "glue", "athena"]}', false)
ON CONFLICT (name) DO NOTHING;
