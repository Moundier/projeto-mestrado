from api.services.cbr_core import ExportCase, SimilarityWeights, similarity
from api.services.repository import load_all_cases


def retrieve_similar_cases(
    query: ExportCase,
    weights: SimilarityWeights | None = None,
    top_k: int = 5,
    cases: list[ExportCase] | None = None,
) -> list[tuple[ExportCase, float]]:
    if weights is None:
        weights = SimilarityWeights()

    if cases is None:
        cases = load_all_cases()
    if not cases:
        return []

    ranked = [(case, similarity(case, query, weights)) for case in cases]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def estimate_success_rate(
    query: ExportCase,
    weights: SimilarityWeights | None = None,
    top_k: int = 5,
    cases: list[ExportCase] | None = None,
) -> dict:
    similar = retrieve_similar_cases(query, weights, top_k, cases)
    if not similar:
        return {"rate": 0.0, "total": 0, "approved": 0, "cases": []}

    approved = sum(1 for case, _ in similar if case.outcome == "DEFERIDA")
    total = len(similar)

    return {
        "rate": round(approved / total * 100, 1) if total > 0 else 0.0,
        "total": total,
        "approved": approved,
        "cases": [
            {
                "case_id": case.case_id,
                "product_type": case.product_type,
                "destination_country": case.destination_country,
                "export_quantity_kg": case.export_quantity_kg,
                "outcome": case.outcome,
                "score": round(score, 4),
            }
            for case, score in similar
        ],
    }
