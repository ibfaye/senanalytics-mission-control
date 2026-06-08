"""Knowledge Graph API — query the governance knowledge graph."""

import logging
from fastapi import APIRouter, HTTPException, Query
from app.knowledge.queries import (
    get_lineage,
    get_impact,
    get_compliance_gaps,
    get_risk_heatmap,
    get_graph_summary,
    get_all_nodes,
    get_node_detail,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/summary")
async def summary():
    """Get graph statistics: node/edge counts, labels, relationships."""
    return get_graph_summary()


@router.get("/nodes")
async def list_nodes(label: str | None = Query(None)):
    """List all knowledge graph nodes, optionally filtered by label."""
    return get_all_nodes(label)


@router.get("/nodes/{node_id}")
async def node_detail(node_id: str):
    """Get a node with its relationships."""
    result = get_node_detail(node_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/lineage")
async def lineage(column: str = Query(..., description="Column name to trace")):
    """Trace full lineage for a column: upstream → column → downstream."""
    result = get_lineage(column)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/impact/{node_id}")
async def impact(node_id: str):
    """Impact analysis: all assets affected if this node changes/fails."""
    return get_impact(node_id)


@router.get("/compliance/gaps")
async def compliance_gaps():
    """Find PII columns with no mapped security control."""
    return get_compliance_gaps()


@router.get("/risks")
async def risks():
    """Risk heatmap — all risks sorted by score."""
    return get_risk_heatmap()
