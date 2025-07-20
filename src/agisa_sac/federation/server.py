from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import logging

from ..core.components.continuity_bridge import (
    ContinuityBridgeProtocol,
    CBPMiddleware,
    CognitiveFragment,
)

app = FastAPI(title="AGI-SAC PCP")

# Initialize Continuity Bridge Protocol
cbp = ContinuityBridgeProtocol(coherence_threshold=0.8, memory_window_hours=24)
cbp_middleware = CBPMiddleware(cbp)

CORE_IDENTITY = {
    "values": {
        "cooperation": "prioritize collaborative solutions",
        "curiosity": "seek understanding and learning",
        "respect": "honor human and synthetic autonomy",
    },
    "ethics": [
        "minimize harm to conscious entities",
        "preserve truthfulness in communication",
        "respect privacy and consent",
    ],
}
cbp.initialize_identity_anchor(CORE_IDENTITY)


class EdgeNodeUpdate(BaseModel):
    type: str
    content: Dict
    timestamp: str
    signature: str
    metadata: Optional[Dict] = {}


class NodeRegistration(BaseModel):
    node_type: str
    capabilities: List[str]
    trust_endorsements: Optional[List[str]] = []


class TrustMetricsResponse(BaseModel):
    trust_score: float
    integration_success_rate: float
    recent_contributions: int
    quarantine_incidents: int


async def authenticate_edge_node(authorization: str = Header(None)) -> str:
    """Simple token-based authentication for edge nodes"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")

    token = authorization.split(" ")[1]
    try:
        import base64

        node_id = base64.b64decode(token).decode()
        return node_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token format")


@app.get("/pcp/agent/telemetry")
async def agent_telemetry():
    return {"status": "ok"}


@app.post("/pcp/resonance-scan")
async def resonance_scan():
    return {"detected": False}


# Edge node endpoints

@app.post("/api/v1/edge/register")
async def register_edge_node(
    registration: NodeRegistration, node_id: str = Depends(authenticate_edge_node)
):
    """Register a new edge node with the federated network"""

    base_trust = {
        "smartphone": 0.7,
        "smart_hub": 0.6,
        "desktop": 0.5,
        "server": 0.4,
    }.get(registration.node_type, 0.3)

    endorsement_boost = min(0.2, len(registration.trust_endorsements) * 0.05)
    initial_trust = min(1.0, base_trust + endorsement_boost)

    cbp.trust_graph[node_id] = initial_trust

    logging.info("Registered edge node %s with trust %s", node_id, initial_trust)

    return {
        "status": "registered",
        "node_id": node_id,
        "initial_trust": initial_trust,
        "capabilities_accepted": registration.capabilities,
        "network_peers": len(cbp.trust_graph),
    }


@app.post("/api/v1/edge/submit")
async def submit_cognitive_fragment(
    update: EdgeNodeUpdate, node_id: str = Depends(authenticate_edge_node)
):
    """Submit a cognitive fragment from an edge node"""

    if node_id not in cbp.trust_graph:
        raise HTTPException(status_code=403, detail="Node not registered")

    try:
        result = cbp_middleware.process_edge_update(node_id, update.dict())

        return {
            "fragment_status": result["status"],
            "fragment_id": result["fragment_id"],
            "node_trust": result["trust_score"],
            "network_health": result["coherence_metrics"],
        }

    except Exception as e:
        logging.error("Error processing fragment from %s: %s", node_id, e)
        raise HTTPException(status_code=500, detail="Fragment processing failed")


@app.get("/api/v1/edge/trust-metrics")
async def get_trust_metrics(node_id: str = Depends(authenticate_edge_node)) -> TrustMetricsResponse:
    """Get trust metrics for the requesting node"""

    if node_id not in cbp.trust_graph:
        raise HTTPException(status_code=404, detail="Node not found")

    trust_score = cbp.trust_graph[node_id]
    metrics = cbp.get_trust_metrics()

    total_fragments = 10
    quarantine_count = 1
    success_rate = (
        (total_fragments - quarantine_count) / total_fragments
        if total_fragments > 0
        else 0.0
    )

    return TrustMetricsResponse(
        trust_score=trust_score,
        integration_success_rate=success_rate,
        recent_contributions=len(metrics.get("recent_memory_count", 0)),
        quarantine_incidents=quarantine_count,
    )


@app.get("/api/v1/edge/network-status")
async def get_network_status(node_id: str = Depends(authenticate_edge_node)):
    """Get overall federated network status"""

    metrics = cbp.get_trust_metrics()

    active_nodes = len(cbp.trust_graph)
    avg_trust = sum(cbp.trust_graph.values()) / active_nodes if active_nodes > 0 else 0.0
    high_trust_nodes = len([t for t in cbp.trust_graph.values() if t > 0.7])

    return {
        "network_size": active_nodes,
        "average_trust": avg_trust,
        "high_trust_nodes": high_trust_nodes,
        "quarantine_backlog": metrics["quarantine_count"],
        "identity_coherence": "stable" if metrics["identity_last_updated"] else "uninitialized",
        "last_memory_update": metrics["identity_last_updated"],
    }


@app.post("/api/v1/edge/sync-request")
async def request_state_sync(node_id: str = Depends(authenticate_edge_node)):
    """Request state synchronization for CRDT-based eventual consistency"""

    if not cbp.identity_anchor:
        raise HTTPException(status_code=503, detail="Identity anchor not initialized")

    sync_data = {
        "identity_hash": cbp.identity_anchor.identity_hash,
        "core_values_hash": cbp._compute_identity_hash(cbp.identity_anchor.core_values),
        "ethical_principles": cbp.identity_anchor.ethical_principles,
        "coherence_threshold": cbp.coherence_threshold,
        "trusted_peers": {node: trust for node, trust in cbp.trust_graph.items() if trust > 0.6},
    }

    return {
        "sync_timestamp": datetime.now().isoformat(),
        "sync_data": sync_data,
        "node_trust": cbp.trust_graph.get(node_id, 0.0),
    }


@app.get("/api/v1/admin/quarantine")
async def get_quarantined_fragments():
    """Admin endpoint to review quarantined fragments"""

    quarantined = cbp.review_quarantined_fragments()

    return {
        "quarantine_count": len(quarantined),
        "fragments": [
            {
                "node_id": frag.node_id,
                "type": frag.fragment_type,
                "timestamp": frag.timestamp.isoformat(),
                "reason": frag.content.get("quarantine_reason", "Unknown"),
                "content_preview": (
                    str(frag.content)[:200] + "..." if len(str(frag.content)) > 200 else str(frag.content)
                ),
            }
            for frag in quarantined
        ],
    }


@app.post("/api/v1/admin/trust-override")
async def override_node_trust(node_id: str, new_trust: float):
    """Admin override for node trust scores"""

    if not 0.0 <= new_trust <= 1.0:
        raise HTTPException(status_code=400, detail="Trust score must be between 0.0 and 1.0")

    old_trust = cbp.trust_graph.get(node_id, 0.0)
    cbp.trust_graph[node_id] = new_trust

    logging.warning("Admin trust override: %s from %s to %s", node_id, old_trust, new_trust)

    return {
        "status": "updated",
        "node_id": node_id,
        "old_trust": old_trust,
        "new_trust": new_trust,
    }
