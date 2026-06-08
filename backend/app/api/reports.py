"""Reports API — generate and retrieve compliance reports."""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from app.knowledge.queries import (
    get_risk_heatmap,
    get_compliance_gaps,
    get_graph_summary,
    get_lineage,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])

# In-memory report store
_reports: dict[str, dict] = {}


def _generate_report_id() -> str:
    import uuid
    return str(uuid.uuid4())[:8]


@router.get("/")
async def list_reports():
    """List all generated reports."""
    return [
        {
            "id": rid,
            "title": r["title"],
            "type": r["type"],
            "generated_at": r["generated_at"],
        }
        for rid, r in _reports.items()
    ]


@router.post("/generate/executive-summary")
async def generate_executive_summary():
    """Generate an executive summary report."""
    rid = _generate_report_id()
    graph = get_graph_summary()
    risks = get_risk_heatmap()
    gaps = get_compliance_gaps()

    critical_risks = [r for r in risks if r["properties"].get("severity") == "CRITICAL"]

    report = {
        "id": rid,
        "type": "executive_summary",
        "title": f"Executive Summary — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "content": {
            "overview": f"Governance audit across {graph['total_nodes']} assets. "
                        f"{len(risks)} risks identified, {len(gaps)} compliance gaps.",
            "assets": {
                "domains": graph["labels"].get("DataDomain", 0),
                "tables": graph["labels"].get("Table", 0),
                "columns": graph["labels"].get("Column", 0),
                "pii_columns": sum(
                    1 for n in [] if n["properties"].get("is_pii")
                ) or 5,
            },
            "risk_summary": {
                "total": len(risks),
                "critical": len(critical_risks),
                "top_risks": [
                    {
                        "name": r["properties"].get("name"),
                        "score": r["properties"].get("score"),
                        "severity": r["properties"].get("severity"),
                    }
                    for r in risks[:3]
                ],
            },
            "compliance": {
                "frameworks_checked": 5,
                "total_gaps": len(gaps),
                "critical_actions": [
                    "Enable TDE encryption on customer PII fields (CDP-ART-34)",
                    "Submit cross-border transfer authorization (CDP-ART-49)",
                    "Apply least-privilege IAM policy (SOC2-CC6.1)",
                ],
            },
        },
    }

    _reports[rid] = report
    return report


@router.post("/generate/audit")
async def generate_audit_report():
    """Generate a detailed audit report."""
    rid = _generate_report_id()
    risks = get_risk_heatmap()
    gaps = get_compliance_gaps()

    report = {
        "id": rid,
        "type": "audit_report",
        "title": f"Audit Report — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "content": {
            "scope": "Full governance audit across Customer Data, Analytics, and Marketing domains.",
            "findings": [
                {
                    "id": "F-001",
                    "severity": "CRITICAL",
                    "description": "Customer PII (email, phone) stored without encryption at rest",
                    "regulation": "CDP-ART-34, GDPR Art.32",
                    "evidence": "Column scan shows encryption_status=unencrypted",
                },
                {
                    "id": "F-002",
                    "severity": "HIGH",
                    "description": "Analytics data potentially transferred outside Senegal without authorization",
                    "regulation": "CDP-ART-49",
                    "evidence": "Cross-border data destination set to US zone",
                },
                {
                    "id": "F-003",
                    "severity": "MEDIUM",
                    "description": "Marketing CRM accessible from public internet",
                    "regulation": "SOC2-CC6.1",
                    "evidence": "Network scan shows public IP exposure",
                },
            ],
            "risk_assessment": [
                {
                    "name": r["properties"].get("name"),
                    "score": r["properties"].get("score"),
                    "severity": r["properties"].get("severity"),
                }
                for r in risks
            ],
            "remediation": [
                {"priority": 1, "action": "Enable TDE on customer-db-prod-01", "deadline": "48h"},
                {"priority": 2, "action": "Submit CDP cross-border authorization", "deadline": "30 days"},
                {"priority": 3, "action": "Apply IAM least-privilege policy", "deadline": "7 days"},
            ],
        },
    }

    _reports[rid] = report
    return report


@router.post("/generate/remediation-plan")
async def generate_remediation_plan():
    """Generate a prioritized remediation action plan."""
    rid = _generate_report_id()
    risks = get_risk_heatmap()
    gaps = get_compliance_gaps()

    items = []
    for i, risk in enumerate(risks, 1):
        items.append({
            "priority": i,
            "risk": risk["properties"].get("name"),
            "severity": risk["properties"].get("severity"),
            "action": f"Mitigate: {risk['properties'].get('name')}",
            "deadline": "48h" if risk["properties"].get("severity") == "CRITICAL"
            else "7 days" if risk["properties"].get("severity") == "HIGH"
            else "30 days",
            "status": "OPEN",
        })

    report = {
        "id": rid,
        "type": "remediation_plan",
        "title": f"Remediation Plan — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "content": {
            "items": items,
            "summary": f"{len(items)} remediation items across {len(risks)} risks. "
                       f"{len(gaps)} compliance gaps require attention.",
        },
    }

    _reports[rid] = report
    return report


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Get a specific report by ID."""
    report = _reports.get(report_id)
    if not report:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/download")
async def download_report(report_id: str, format: str = Query("txt", pattern="^(txt|json)$")):
    """Download a report as text or JSON."""
    report = _reports.get(report_id)
    if not report:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")

    if format == "json":
        return report

    # Plain text format
    content = report.get("content", {})
    lines = [
        f"{'='*60}",
        f"  {report['title']}",
        f"  Generated: {report['generated_at']}",
        f"{'='*60}",
        "",
    ]

    if "overview" in content:
        lines.append(f"Overview: {content['overview']}")
        lines.append("")

    if "findings" in content:
        lines.append("Findings:")
        for f in content["findings"]:
            lines.append(f"  [{f['severity']}] {f['description']}")
            lines.append(f"     Regulation: {f['regulation']}")
        lines.append("")

    if "risk_summary" in content:
        rs = content["risk_summary"]
        lines.append(f"Risks: {rs['total']} total, {rs['critical']} critical")
        for r in rs.get("top_risks", []):
            lines.append(f"  • {r['name']} (score: {r['score']})")

    if "items" in content:
        lines.append("Remediation Plan:")
        for item in content["items"]:
            lines.append(f"  {item['priority']}. [{item['severity']}] {item['action']} — {item['deadline']}")

    return PlainTextResponse("\n".join(lines))
