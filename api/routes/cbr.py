from fastapi import APIRouter, HTTPException

from api.services.cbr_core import ExportCase, SimilarityWeights, build_case
from api.services.cbr_retrieval import estimate_success_rate
from api.services.cbr_adaptation import suggest_improvements
from api.services.repository import load_all_cases, get_case_count, add_case

router = APIRouter(prefix="/cbr", tags=["CBR"])


@router.post("/similarity")
async def similarity_endpoint(data: dict):
    try:
        query = build_case(data)
        weights = SimilarityWeights()
        success = estimate_success_rate(query, weights)
        suggestions = suggest_improvements(query, weights)
        return {
            "success_rate": success,
            "suggestions": suggestions,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cases")
async def list_cases(limit: int = 20, status: str | None = None):
    cases = load_all_cases()
    if status:
        cases = [c for c in cases if c.outcome == status]
    return {
        "total": len(cases),
        "cases": [
            {
                "case_id": c.case_id,
                "product_type": c.product_type,
                "destination_country": c.destination_country,
                "export_quantity_kg": c.export_quantity_kg,
                "outcome": c.outcome,
            }
            for c in cases[:limit]
        ],
    }


@router.get("/stats")
async def stats():
    return {"total_cases": get_case_count()}


@router.post("/ingest")
async def ingest_case(data: dict):
    try:
        case = build_case(data)
        add_case(case)
        return {"message": "Case ingested", "case_id": case.case_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
