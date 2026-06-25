import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.services.cbr_core import ExportCase
from api.services.repository import load_all_cases, get_case_count, search_cases, add_case


class TestRepository:
    def test_load_all_cases(self):
        cases = load_all_cases()
        assert len(cases) == 379
        assert all(isinstance(c, ExportCase) for c in cases)

    def test_get_case_count(self):
        count = get_case_count()
        assert count == 379

    def test_search_cases_all(self):
        cases = search_cases(limit=50)
        assert len(cases) <= 50

    def test_search_cases_by_status_approved(self):
        cases = search_cases(status_filter="DEFERIDA", limit=10)
        assert len(cases) <= 10
        assert all(c.outcome == "DEFERIDA" for c in cases)

    def test_search_cases_by_status_rejected(self):
        cases = search_cases(status_filter="INDEFERIDA")
        assert all(c.outcome == "INDEFERIDA" for c in cases)

    def test_first_case_has_expected_structure(self):
        cases = load_all_cases()
        c = cases[0]
        assert c.case_id is not None
        assert c.product_type is not None
        assert c.destination_country is not None
        assert c.export_quantity_kg > 0
        assert c.outcome != ""

    def test_add_case(self):
        count_before = get_case_count()
        new_case = ExportCase(
            case_id="new-test",
            product_type="TESTE",
            destination_country="BRASIL",
            export_quantity_kg=100.0,
            raw_material_kg=100.0,
            species=frozenset(),
            suppliers=frozenset(),
            invoice_count=0,
            company_cnpj="",
            company_rgp="",
            outcome="PENDENTE",
        )
        add_case(new_case)
        assert get_case_count() == count_before + 1
