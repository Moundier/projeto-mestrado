import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.services.cbr_core import ExportCase, SimilarityWeights
from api.services.cbr_retrieval import retrieve_similar_cases, estimate_success_rate


def make_case(
    case_id="test",
    product_type="FARINHA DE PESCADO",
    destination_country="CHILE",
    export_quantity_kg=1000.0,
    species=None,
    outcome="DEFERIDA",
) -> ExportCase:
    return ExportCase(
        case_id=case_id,
        product_type=product_type,
        destination_country=destination_country,
        export_quantity_kg=export_quantity_kg,
        raw_material_kg=export_quantity_kg,
        species=frozenset(species or []),
        suppliers=frozenset(),
        invoice_count=1,
        company_cnpj="",
        company_rgp="",
        outcome=outcome,
    )


SAMPLE_CASES = [
    make_case("c1", "FARINHA DE PESCADO", "CHILE", 10000, {"Atum"}, "DEFERIDA"),
    make_case("c2", "FARINHA DE PESCADO", "CHILE", 20000, {"Sardinha"}, "DEFERIDA"),
    make_case("c3", "PEIXE FRESCO", "JAPAN", 5000, {"Atum"}, "DEFERIDA"),
    make_case("c4", "FARINHA DE PESCADO", "CHILE", 15000, {"Atum", "Sardinha"}, "INDEFERIDA"),
    make_case("c5", "CAMARAO CONGELADO", "EUA", 30000, {"Camarão"}, "DEFERIDA"),
]


class TestRetrieveSimilarCases:
    def test_returns_top_k(self):
        query = make_case("q", "FARINHA DE PESCADO", "CHILE", 12000, {"Atum"})
        w = SimilarityWeights()
        results = retrieve_similar_cases(query, w, top_k=3, cases=SAMPLE_CASES)
        assert len(results) == 3

    def test_ordering_by_score(self):
        query = make_case("q", "FARINHA DE PESCADO", "CHILE", 12000, {"Atum"})
        w = SimilarityWeights()
        results = retrieve_similar_cases(query, w, top_k=5, cases=SAMPLE_CASES)
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    def test_best_match_is_most_similar(self):
        query = make_case("q", "FARINHA DE PESCADO", "CHILE", 12000, {"Atum"})
        w = SimilarityWeights()
        results = retrieve_similar_cases(query, w, top_k=5, cases=SAMPLE_CASES)
        assert results[0][0].case_id == "c1"

    def test_empty_case_list(self):
        query = make_case()
        w = SimilarityWeights()
        results = retrieve_similar_cases(query, w, top_k=5, cases=[])
        assert results == []


class TestEstimateSuccessRate:
    def test_rate_calculation(self):
        query = make_case("q", "FARINHA DE PESCADO", "CHILE", 12000, {"Atum"})
        w = SimilarityWeights()
        result = estimate_success_rate(query, w, top_k=5, cases=SAMPLE_CASES)
        assert "rate" in result
        assert "approved" in result
        assert "total" in result
        assert result["total"] <= 5

    def test_no_cases(self):
        query = make_case()
        w = SimilarityWeights()
        result = estimate_success_rate(query, w, top_k=5, cases=[])
        assert result == {"rate": 0.0, "total": 0, "approved": 0, "cases": []}
