import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.services.cbr_core import (
    ExportCase,
    SimilarityWeights,
    build_case,
    jaccard,
    numeric_similarity,
    similarity,
)


def make_case(
    case_id="test",
    product_type="FARINHA DE PESCADO",
    destination_country="CHILE",
    export_quantity_kg=1000.0,
    raw_material_kg=1000.0,
    species=None,
    suppliers=None,
    invoice_count=1,
    outcome="DEFERIDA",
) -> ExportCase:
    return ExportCase(
        case_id=case_id,
        product_type=product_type,
        destination_country=destination_country,
        export_quantity_kg=export_quantity_kg,
        raw_material_kg=raw_material_kg,
        species=frozenset(species or []),
        suppliers=frozenset(suppliers or []),
        invoice_count=invoice_count,
        company_cnpj="",
        company_rgp="",
        outcome=outcome,
    )


class TestJaccard:
    def test_empty_sets(self):
        assert jaccard(set(), set()) == 1.0

    def test_identical_sets(self):
        assert jaccard({"a", "b"}, {"a", "b"}) == 1.0

    def test_partial_overlap(self):
        assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3

    def test_disjoint(self):
        assert jaccard({"a"}, {"b"}) == 0.0

    def test_one_empty(self):
        assert jaccard({"a"}, set()) == 0.0


class TestNumericSimilarity:
    def test_equal(self):
        assert numeric_similarity(100, 100) == 1.0

    def test_different(self):
        result = numeric_similarity(100, 50)
        assert 0.0 < result < 1.0
        assert result == 1 - 50 / 100

    def test_both_zero(self):
        assert numeric_similarity(0, 0) == 1.0

    def test_one_zero(self):
        result = numeric_similarity(0, 100)
        assert 0.0 <= result < 1.0


class TestSimilarity:
    def test_identical_cases(self):
        w = SimilarityWeights()
        a = make_case()
        score = similarity(a, a, w)
        assert score == pytest.approx(1.0, rel=1e-3)

    def test_no_match(self):
        w = SimilarityWeights()
        a = make_case(product_type="FARINHA DE PESCADO", destination_country="CHILE")
        b = make_case(product_type="PEIXE FRESCO", destination_country="JAPAN",
                      export_quantity_kg=999999, raw_material_kg=999999,
                      species={"X"}, suppliers={"Y"}, invoice_count=99)
        score = similarity(a, b, w)
        assert score < 0.5

    def test_partial_match(self):
        w = SimilarityWeights()
        a = make_case(product_type="FARINHA DE PESCADO", destination_country="CHILE",
                      export_quantity_kg=1000, species={"Atum"})
        b = make_case(product_type="FARINHA DE PESCADO", destination_country="JAPAN",
                      export_quantity_kg=5000, species={"Sardinha"})
        score = similarity(a, b, w)
        assert 0.2 < score < 0.6

    def test_weighted_score_components(self):
        w = SimilarityWeights(product_type=0.5, destination_country=0.5,
                              species=0, export_quantity=0, raw_material=0,
                              suppliers=0, invoice_count=0)
        a = make_case(product_type="A", destination_country="X")
        b = make_case(product_type="A", destination_country="Y")
        assert similarity(a, b, w) == pytest.approx(0.5)


class TestBuildCase:
    def test_build_case(self):
        data = {
            "uuid": "abc-123",
            "tipoProduto": "PEIXE CONGELADO",
            "paisImportador": "ESPANHA",
            "totalProdutoExportar": "50000",
            "totalMateriaPrimaNecessaria": "60000",
            "especies": ["Atum", "Sardinha"],
            "notasFiscais": [
                {"cnpjEmpresaNota": "123456"},
                {"cnpjEmpresaNota": "789012"},
            ],
            "cnpjEmpresa": "00.000.000/0001-00",
            "numRgp": "SP-I000123",
            "status": "DEFERIDA",
        }
        case = build_case(data)
        assert case.case_id == "abc-123"
        assert case.product_type == "PEIXE CONGELADO"
        assert case.destination_country == "ESPANHA"
        assert case.export_quantity_kg == 50000.0
        assert case.raw_material_kg == 60000.0
        assert case.species == frozenset({"Atum", "Sardinha"})
        assert case.suppliers == frozenset({"123456", "789012"})
        assert case.invoice_count == 2
        assert case.outcome == "DEFERIDA"

    def test_build_case_no_notas(self):
        data = {
            "uuid": "abc",
            "tipoProduto": "X",
            "paisImportador": "Y",
            "totalProdutoExportar": "100",
            "totalMateriaPrimaNecessaria": "100",
            "especies": [],
            "cnpjEmpresa": "",
            "numRgp": "",
            "status": "PENDENTE",
        }
        case = build_case(data)
        assert case.invoice_count == 0
        assert case.suppliers == frozenset()


import pytest
