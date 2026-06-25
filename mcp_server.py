import json
import hashlib
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from api.services.rag import rag_retrieve
from api.services.cbr_core import ExportCase, SimilarityWeights
from api.services.cbr_retrieval import retrieve_similar_cases, estimate_success_rate

mcp = FastMCP("caol-agent")

AUDIT_LOG: list[dict] = []


def _audit(user_id: str, tool_name: str, input_summary: str, output_ref: str):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "tool_name": tool_name,
        "input_summary": input_summary,
        "output_reference": output_ref,
        "checksum": hashlib.sha256(
            f"{user_id}{tool_name}{input_summary}{output_ref}".encode()
        ).hexdigest(),
    }
    AUDIT_LOG.append(record)
    return record


@mcp.tool()
async def search_regulation(regulation_id: str, user_id: str = "anonymous") -> str:
    """Search for a regulation by its ID (e.g. 'IN 23/2024') and return full text with citations."""
    result = await rag_retrieve(regulation_id)
    _audit(user_id, "search_regulation", regulation_id, f"regulation:{regulation_id}")
    return result


@mcp.tool()
async def get_caol_step(request_id: str, user_id: str = "anonymous") -> str:
    """Get the current CAOL step description and status for a given request ID."""
    _audit(user_id, "get_caol_step", request_id, f"step:{request_id}")

    steps = {
        "draft": "Rascunho inicial sendo preenchido",
        "submitted": "Submetido para análise documental",
        "document_analysis": "Em análise documental",
        "technical_analysis": "Em análise técnica",
        "approved": "Aprovado",
        "rejected": "Rejeitado",
    }

    status = steps.get(request_id, "Unknown step")
    return json.dumps({"request_id": request_id, "status": status}, indent=2)


@mcp.tool()
async def submit_dispatch(
    data: dict,
    user_id: str = "anonymous",
    confirmed: bool = False,
) -> str:
    """Submit a technical dispatch for CAOL. Requires explicit human confirmation (confirmed=True)."""
    if not confirmed:
        return json.dumps(
            {
                "error": "Human confirmation required. Set confirmed=True to proceed.",
                "data_preview": {k: v for k, v in data.items() if k != "notasFiscais"},
            },
            indent=2,
        )

    _audit(user_id, "submit_dispatch", str(list(data.keys())), f"dispatch:{data.get('uuid', 'new')}")

    return json.dumps(
        {
            "message": "Dispatch submitted successfully",
            "uuid": data.get("uuid", "new"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        indent=2,
    )


@mcp.tool()
async def get_similar_cases(
    product_type: str = "",
    destination_country: str = "",
    export_quantity_kg: float = 0,
    species: list[str] | None = None,
    top_k: int = 5,
    user_id: str = "anonymous",
) -> str:
    """Find similar historical CAOL cases and estimate success rate based on provided criteria."""
    from api.services.repository import load_all_cases

    all_cases = load_all_cases()
    if not all_cases:
        return json.dumps({"error": "No cases loaded in the repository."}, indent=2)

    query = ExportCase(
        case_id="query",
        product_type=product_type or "UNKNOWN",
        destination_country=destination_country or "UNKNOWN",
        export_quantity_kg=export_quantity_kg,
        raw_material_kg=export_quantity_kg,
        species=frozenset(species or []),
        suppliers=frozenset(),
        invoice_count=0,
        company_cnpj="",
        company_rgp="",
        outcome="",
    )

    weights = SimilarityWeights()
    similar = retrieve_similar_cases(query, weights, top_k)
    success = estimate_success_rate(query, weights, top_k)

    _audit(
        user_id,
        "get_similar_cases",
        f"product_type={product_type}, destination={destination_country}",
        f"top_{top_k}_similar",
    )

    return json.dumps(
        {
            "success_rate": success,
            "similar_cases": [
                {
                    "case_id": c.case_id,
                    "product_type": c.product_type,
                    "destination_country": c.destination_country,
                    "export_quantity_kg": c.export_quantity_kg,
                    "outcome": c.outcome,
                    "score": round(s, 4),
                }
                for c, s in similar
            ],
        },
        indent=2,
        ensure_ascii=False,
    )


@mcp.tool()
async def get_audit_log(user_id: str = "admin") -> str:
    """Retrieve the immutable audit log (admin only)."""
    if user_id != "admin":
        return json.dumps({"error": "Unauthorized. Admin access required."}, indent=2)
    return json.dumps(AUDIT_LOG[-50:], indent=2, default=str)


@mcp.resource("regulation://{regulation_id}")
def get_regulation_resource(regulation_id: str) -> str:
    """Read-only resource for regulation documents."""
    return f"Regulation data for {regulation_id} (requires RAG retrieval)."


@mcp.resource("casestats://summary")
def get_case_stats_resource() -> str:
    """Read-only resource for CBR case statistics summary."""
    from api.services.repository import get_case_count
    count = get_case_count()
    return json.dumps({"total_cases": count}, indent=2)


def run_server(host: str = "0.0.0.0", port: int = 8002):
    """Run the MCP server."""
    mcp.run(host=host, port=port)


if __name__ == "__main__":
    run_server()
