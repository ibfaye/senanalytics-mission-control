"""Dashboard API — aggregated metrics for Mission Control, Governance, Security, and Compliance."""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter

from app.knowledge.queries import (
    get_graph_summary,
    get_compliance_gaps,
    get_risk_heatmap,
    get_lineage,
)
from app.core.engine import get_pending_approvals

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])


@router.get("/mission-control")
async def mission_control_metrics():
    """Aggregate metrics for the main Mission Control dashboard."""
    graph = get_graph_summary()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "nodes": {
            "total": graph["total_nodes"],
            "edges": graph["total_edges"],
            "domains": graph["labels"].get("DataDomain", 0),
            "tables": graph["labels"].get("Table", 0),
            "columns": graph["labels"].get("Column", 0),
        },
        "risks": {
            "total": graph["labels"].get("Risk", 0),
            "critical": sum(
                1 for r in get_risk_heatmap() if r["properties"].get("severity") == "CRITICAL"
            ),
            "high": sum(
                1 for r in get_risk_heatmap() if r["properties"].get("severity") == "HIGH"
            ),
        },
        "compliance": {
            "gaps": len(get_compliance_gaps()),
            "policies": graph["labels"].get("Policy", 0),
            "controls": graph["labels"].get("Control", 0),
        },
        "pending_approvals": len(get_pending_approvals()),
    }


@router.get("/governance")
async def governance_metrics():
    """Governance dashboard — domains, ownership, classifications."""
    graph = get_graph_summary()

    # Build domain details
    domains = []
    from app.knowledge.queries import get_all_nodes
    for node in get_all_nodes("DataDomain"):
        domains.append({
            "name": node["properties"].get("name", ""),
            "sensitivity": node["properties"].get("sensitivity", "UNKNOWN"),
            "owner": node["properties"].get("owner", "Unknown"),
        })

    # Column classifications
    columns = get_all_nodes("Column")
    pii_columns = [c for c in columns if c["properties"].get("is_pii")]
    encrypted = sum(
        1 for c in pii_columns
        if "encrypted" in c["properties"].get("encryption_status", "")
    )

    # Lineage examples
    email_lineage = get_lineage("email")

    return {
        "domains": {"count": len(domains), "items": domains},
        "data_products": graph["labels"].get("DataProduct", 0),
        "tables": graph["labels"].get("Table", 0),
        "classifications": {
            "total_columns": len(columns),
            "pii_columns": len(pii_columns),
            "encrypted_pii": encrypted,
            "unencrypted_pii": len(pii_columns) - encrypted,
        },
        "lineage_example": {
            "column": "email",
            "upstream_count": len(email_lineage.get("upstream_lineage", [])),
            "downstream_count": len(email_lineage.get("downstream_mappings", [])),
        },
        "ownership": {
            "stewards": graph["labels"].get("Owner", 0),
        },
    }


@router.get("/security")
async def security_metrics():
    """Security dashboard — findings, vulnerabilities, posture."""
    risks = get_risk_heatmap()
    gaps = get_compliance_gaps()

    # Simulated security findings (from agents in production)
    findings = [
        {"id": "SEC-001", "category": "encryption", "severity": "CRITICAL",
         "description": "PII fields unencrypted at rest", "affected": "customers table",
         "remediation": "Enable TDE"},
        {"id": "SEC-002", "category": "iam", "severity": "HIGH",
         "description": "Overly permissive IAM roles", "affected": "analytics pipeline",
         "remediation": "Apply least-privilege"},
        {"id": "SEC-003", "category": "network", "severity": "MEDIUM",
         "description": "DB publicly accessible", "affected": "marketing CRM",
         "remediation": "Restrict to VPC"},
        {"id": "SEC-004", "category": "encryption", "severity": "HIGH",
         "description": "No key rotation policy", "affected": "all encrypted data",
         "remediation": "Enable auto-rotation"},
    ]

    return {
        "risk_heatmap": [
            {
                "name": r["properties"].get("name", ""),
                "score": r["properties"].get("score", 0),
                "severity": r["properties"].get("severity", "LOW"),
                "likelihood": r["properties"].get("likelihood", 0),
                "impact": r["properties"].get("impact", 0),
            }
            for r in risks
        ],
        "findings": findings,
        "compliance_gaps": [
            {"name": c["properties"].get("name", ""), "type": c["properties"].get("classification", "PII")}
            for c in gaps[:5]
        ],
        "controls": {
            "implemented": 0,
            "partial": 1,  # IAM control
            "not_implemented": 2,  # encryption, cross-border
        },
    }


@router.get("/compliance")
async def compliance_metrics():
    """Compliance dashboard — framework coverage and status."""
    frameworks = {
        "GDPR": {
            "status": "PARTIALLY_COMPLIANT",
            "score": 78,
            "gaps": 3,
            "policies_mapped": 1,
            "controls_implemented": 1,
            "last_audit": "2026-06-07",
        },
        "CDP-Senegal": {
            "status": "NON_COMPLIANT",
            "score": 55,
            "gaps": 5,
            "policies_mapped": 2,
            "controls_implemented": 0,
            "last_audit": "2026-06-07",
        },
        "PIPEDA": {
            "status": "PARTIALLY_COMPLIANT",
            "score": 85,
            "gaps": 2,
            "policies_mapped": 1,
            "controls_implemented": 0,
            "last_audit": "2026-06-01",
        },
        "SOC2": {
            "status": "PARTIALLY_COMPLIANT",
            "score": 72,
            "gaps": 4,
            "policies_mapped": 1,
            "controls_implemented": 1,
            "last_audit": "2026-05-15",
        },
        "ISO27001": {
            "status": "NON_COMPLIANT",
            "score": 48,
            "gaps": 7,
            "policies_mapped": 0,
            "controls_implemented": 0,
            "last_audit": "2026-05-01",
        },
    }

    return {
        "frameworks": frameworks,
        "total_policies": get_graph_summary()["labels"].get("Policy", 0),
        "total_controls": get_graph_summary()["labels"].get("Control", 0),
        "compliance_gaps_count": len(get_compliance_gaps()),
    }
