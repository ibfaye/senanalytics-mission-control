"""
Knowledge Graph Queries — pre-built query functions for governance analysis.
Also seeds the graph with demo data on first import.
"""

import logging
from app.knowledge.graph import knowledge_graph as kg

logger = logging.getLogger(__name__)

_SEEDED = False


def seed_demo_graph():
    """Populate the knowledge graph with a realistic governance dataset."""
    global _SEEDED
    if _SEEDED or kg.summary()["total_nodes"] > 0:
        return

    logger.info("[KG] Seeding demo knowledge graph...")

    # ── Data Domains ──
    kg.add_node("domain-customer", ["DataDomain"], {
        "name": "Customer Data", "description": "All customer-related data assets",
        "owner": "Data Governance Team", "sensitivity": "HIGH",
    })
    kg.add_node("domain-analytics", ["DataDomain"], {
        "name": "Analytics", "description": "Data analytics and reporting",
        "owner": "Analytics Team", "sensitivity": "MEDIUM",
    })
    kg.add_node("domain-marketing", ["DataDomain"], {
        "name": "Marketing", "description": "Marketing and campaign data",
        "owner": "Marketing Team", "sensitivity": "MEDIUM",
    })

    # ── Data Products ──
    kg.add_node("product-c360", ["DataProduct"], {
        "name": "Customer 360", "description": "Unified customer profile",
        "domain": "Customer Data",
    })
    kg.add_node("product-reports", ["DataProduct"], {
        "name": "Governance Reports", "description": "Compliance and audit reports",
        "domain": "Analytics",
    })

    # ── Tables ──
    kg.add_node("table-customers", ["Table"], {
        "name": "customers", "database": "prod-db", "schema": "public",
        "row_count": 1500000, "storage_gb": 2.4,
    })
    kg.add_node("table-analytics", ["Table"], {
        "name": "analytics_events", "database": "analytics-db", "schema": "raw",
        "row_count": 5000000, "storage_gb": 8.1,
    })
    kg.add_node("table-contacts", ["Table"], {
        "name": "contacts", "database": "marketing-db", "schema": "dbo",
        "row_count": 300000, "storage_gb": 0.6,
    })

    # ── Columns ──
    kg.add_node("col-id", ["Column"], {
        "name": "id", "data_type": "UUID", "nullable": False, "is_pii": False,
    })
    kg.add_node("col-email", ["Column"], {
        "name": "email", "data_type": "VARCHAR(255)", "nullable": True,
        "is_pii": True, "classification": "PII-EMAIL", "sensitivity": "HIGH",
        "encryption_status": "unencrypted",
    })
    kg.add_node("col-name", ["Column"], {
        "name": "full_name", "data_type": "VARCHAR(255)", "nullable": True,
        "is_pii": True, "classification": "PII-NAME", "sensitivity": "HIGH",
    })
    kg.add_node("col-phone", ["Column"], {
        "name": "phone", "data_type": "VARCHAR(20)", "nullable": True,
        "is_pii": True, "classification": "PII-PHONE", "sensitivity": "HIGH",
        "encryption_status": "unencrypted",
    })
    kg.add_node("col-address", ["Column"], {
        "name": "address", "data_type": "TEXT", "nullable": True,
        "is_pii": True, "classification": "PII-ADDRESS", "sensitivity": "MEDIUM",
    })
    kg.add_node("col-ip", ["Column"], {
        "name": "ip_address", "data_type": "VARCHAR(45)", "nullable": True,
        "is_pii": True, "classification": "PII-NETWORK", "sensitivity": "MEDIUM",
    })

    # ── Policies (Compliance Rules) ──
    kg.add_node("policy-gdpr32", ["Policy"], {
        "name": "GDPR Art. 32", "framework": "GDPR",
        "description": "Security of processing — appropriate technical measures",
        "severity": "CRITICAL",
    })
    kg.add_node("policy-cdp34", ["Policy"], {
        "name": "CDP-ART-34", "framework": "Senegal-CDP",
        "description": "PII must be encrypted at rest and in transit",
        "severity": "CRITICAL",
    })
    kg.add_node("policy-cdp49", ["Policy"], {
        "name": "CDP-ART-49", "framework": "Senegal-CDP",
        "description": "Cross-border data transfers require authorization",
        "severity": "HIGH",
    })
    kg.add_node("policy-soc2cc6", ["Policy"], {
        "name": "SOC2-CC6.1", "framework": "SOC2",
        "description": "Logical and physical access controls",
        "severity": "MEDIUM",
    })
    kg.add_node("policy-pipeda", ["Policy"], {
        "name": "PIPEDA-Sch.1-4.7", "framework": "PIPEDA",
        "description": "Safeguards for personal information",
        "severity": "HIGH",
    })

    # ── Controls ──
    kg.add_node("ctrl-enc", ["Control"], {
        "name": "Control-Enc-01", "description": "Encryption at rest for PII data",
        "status": "NOT_IMPLEMENTED", "last_assessed": "2026-06-01",
    })
    kg.add_node("ctrl-iam", ["Control"], {
        "name": "Control-IAM-02", "description": "Least-privilege IAM policy enforcement",
        "status": "PARTIALLY_IMPLEMENTED", "last_assessed": "2026-06-01",
    })
    kg.add_node("ctrl-cb", ["Control"], {
        "name": "Control-CB-03", "description": "Cross-border transfer authorization workflow",
        "status": "NOT_IMPLEMENTED", "last_assessed": "2026-05-15",
    })

    # ── Owners ──
    kg.add_node("owner-aminata", ["Owner"], {
        "name": "Aminata Diop", "role": "Data Steward",
        "department": "Governance", "email": "aminata@example.com",
    })
    kg.add_node("owner-ibrahim", ["Owner"], {
        "name": "Ibrahim Faye", "role": "Platform Architect",
        "department": "Engineering", "email": "ibfaye@example.com",
    })

    # ── Risks ──
    kg.add_node("risk-enc", ["Risk"], {
        "name": "Unencrypted PII at rest", "likelihood": 0.8, "impact": 0.9,
        "score": 0.72, "severity": "CRITICAL", "status": "OPEN",
    })
    kg.add_node("risk-cb", ["Risk"], {
        "name": "Unauthorized cross-border transfer", "likelihood": 0.6,
        "impact": 0.85, "score": 0.51, "severity": "HIGH", "status": "OPEN",
    })
    kg.add_node("risk-iam", ["Risk"], {
        "name": "Overly permissive IAM roles", "likelihood": 0.5,
        "impact": 0.7, "score": 0.35, "severity": "MEDIUM", "status": "OPEN",
    })

    # ── Incidents ──
    kg.add_node("inc-cb", ["Incident"], {
        "name": "Cross-border PII transfer to US servers",
        "severity": "CRITICAL", "status": "INVESTIGATING",
        "detected_by": "PolicyEvaluator", "detected_at": "2026-06-07T08:00:00Z",
    })

    # ── Reports ──
    kg.add_node("report-gdpr", ["Report"], {
        "name": "GDPR Compliance Audit Q2 2026",
        "type": "COMPLIANCE", "format": "PDF",
        "generated_by": "ReportingAgent", "generated_at": "2026-06-07",
    })

    # ── Relationships ──
    # Domain → Product
    kg.add_edge("r-d1", "domain-customer", "product-c360", "CONTAINS", {})
    kg.add_edge("r-d2", "domain-analytics", "product-reports", "CONTAINS", {})

    # Product → Table
    kg.add_edge("r-p1", "product-c360", "table-customers", "CONTAINS", {})
    kg.add_edge("r-p2", "product-reports", "table-analytics", "CONTAINS", {})
    kg.add_edge("r-p3", "domain-marketing", "table-contacts", "CONTAINS", {})

    # Table → Column
    kg.add_edge("r-t1", "table-customers", "col-id", "HAS_COLUMN", {})
    kg.add_edge("r-t2", "table-customers", "col-email", "HAS_COLUMN", {})
    kg.add_edge("r-t3", "table-customers", "col-name", "HAS_COLUMN", {})
    kg.add_edge("r-t4", "table-customers", "col-phone", "HAS_COLUMN", {})
    kg.add_edge("r-t5", "table-customers", "col-address", "HAS_COLUMN", {})
    kg.add_edge("r-t6", "table-analytics", "col-ip", "HAS_COLUMN", {})

    # Column → Policy (regulated by)
    kg.add_edge("r-reg1", "col-email", "policy-gdpr32", "REGULATED_BY", {})
    kg.add_edge("r-reg2", "col-email", "policy-cdp34", "REGULATED_BY", {})
    kg.add_edge("r-reg3", "col-phone", "policy-cdp34", "REGULATED_BY", {})
    kg.add_edge("r-reg4", "col-email", "policy-cdp49", "REGULATED_BY", {})
    kg.add_edge("r-reg5", "col-ip", "policy-pipeda", "REGULATED_BY", {})

    # Policy → Control (mapped to)
    kg.add_edge("r-ctrl1", "policy-cdp34", "ctrl-enc", "MAPPED_TO", {})
    kg.add_edge("r-ctrl2", "policy-soc2cc6", "ctrl-iam", "MAPPED_TO", {})
    kg.add_edge("r-ctrl3", "policy-cdp49", "ctrl-cb", "MAPPED_TO", {})
    kg.add_edge("r-ctrl4", "policy-gdpr32", "ctrl-enc", "MAPPED_TO", {})

    # Column → Risk (has risk)
    kg.add_edge("r-risk1", "col-email", "risk-enc", "HAS_RISK", {})
    kg.add_edge("r-risk2", "col-email", "risk-cb", "HAS_RISK", {})
    kg.add_edge("r-risk3", "table-analytics", "risk-iam", "HAS_RISK", {})

    # Risk → Incident (caused)
    kg.add_edge("r-inc1", "risk-cb", "inc-cb", "CAUSED", {})

    # Risk → Control (mitigated by)
    kg.add_edge("r-mit1", "risk-enc", "ctrl-enc", "MITIGATED_BY", {})
    kg.add_edge("r-mit2", "risk-cb", "ctrl-cb", "MITIGATED_BY", {})
    kg.add_edge("r-mit3", "risk-iam", "ctrl-iam", "MITIGATED_BY", {})

    # Ownership
    kg.add_edge("r-own1", "domain-customer", "owner-aminata", "OWNED_BY", {})
    kg.add_edge("r-own2", "table-customers", "owner-aminata", "STEWARDED_BY", {})
    kg.add_edge("r-own3", "domain-analytics", "owner-ibrahim", "OWNED_BY", {})

    # Incident → Report
    kg.add_edge("r-rep1", "inc-cb", "report-gdpr", "DOCUMENTED_IN", {})

    _SEEDED = True
    logger.info(f"[KG] Seeded {kg.summary()['total_nodes']} nodes, {kg.summary()['total_edges']} edges")


# ── Query Functions ──

def get_lineage(column_name: str) -> dict:
    """Trace full lineage for a column through domains, tables, policies, controls."""
    seed_demo_graph()
    column_node = None
    for node in kg._nodes.values():
        if "Column" in node.labels and node.properties.get("name") == column_name:
            column_node = node
            break
    if not column_node:
        return {"error": f"Column '{column_name}' not found"}

    # Walk up: column → table → product → domain
    upstream = []
    current_id = column_node.id
    for _ in range(3):
        neighbors = kg.neighbors(current_id, "in")
        if neighbors:
            edge, node = neighbors[0]
            upstream.append({"node": kg._node_dict(node.id), "relationship": edge.relationship})
            current_id = node.id
        else:
            break

    # Walk down: column → policy → control, risk
    downstream = []
    for edge, node in kg.neighbors(column_node.id, "out"):
        downstream.append({"node": kg._node_dict(node.id), "relationship": edge.relationship})

    return {
        "column": kg._node_dict(column_node.id),
        "upstream_lineage": upstream,
        "downstream_mappings": downstream,
    }


def get_impact(node_id: str) -> dict:
    """Impact analysis: what breaks if this node changes."""
    seed_demo_graph()
    return kg.impact_analysis(node_id)


def get_compliance_gaps() -> list[dict]:
    """Find PII columns with no mapped control."""
    seed_demo_graph()
    gaps = []
    columns = kg.nodes_by_label("Column")
    for col in columns:
        if not col.properties.get("is_pii"):
            continue
        # Check if column has a path to a Control node
        has_control = False
        for edge, target in kg.neighbors(col.id, "out"):
            if "Policy" in target.labels:
                for e2, t2 in kg.neighbors(target.id, "out"):
                    if "Control" in t2.labels:
                        has_control = True
                        break
            if has_control:
                break
        if not has_control:
            gaps.append(kg._node_dict(col.id))
    return gaps


def get_risk_heatmap() -> list[dict]:
    """All risks sorted by score (highest first)."""
    seed_demo_graph()
    return kg.risk_heatmap()


def get_graph_summary() -> dict:
    """Overall graph statistics."""
    seed_demo_graph()
    return kg.summary()


def get_all_nodes(label: str = None) -> list[dict]:
    """Get all nodes, optionally filtered by label."""
    seed_demo_graph()
    nodes = kg.nodes_by_label(label) if label else list(kg._nodes.values())
    return [kg._node_dict(n.id) for n in nodes]


def get_node_detail(node_id: str) -> dict:
    """Get a node with its relationships."""
    seed_demo_graph()
    node = kg.get_node(node_id)
    if not node:
        return {"error": f"Node '{node_id}' not found"}
    return {
        "node": kg._node_dict(node_id),
        "neighbors": [
            {"edge": {"id": e.id, "relationship": e.relationship},
             "node": kg._node_dict(n.id)}
            for e, n in kg.neighbors(node_id, "both")
        ],
    }
