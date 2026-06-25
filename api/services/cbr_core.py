import os
from dataclasses import dataclass
from typing import FrozenSet


def get_env(key: str, default: str) -> str:
    return os.environ.get(key, default)


@dataclass(slots=True, frozen=True)
class ExportCase:
    case_id: str
    product_type: str
    destination_country: str
    export_quantity_kg: float
    raw_material_kg: float
    species: FrozenSet[str]
    suppliers: FrozenSet[str]
    invoice_count: int
    company_cnpj: str
    company_rgp: str
    outcome: str
    approval_days: int | None = None


@dataclass(slots=True, frozen=True)
class SimilarityWeights:
    product_type: float = float(get_env("CBR_WEIGHT_PRODUCT_TYPE", "0.25"))
    destination_country: float = float(get_env("CBR_WEIGHT_DESTINATION_COUNTRY", "0.15"))
    species: float = float(get_env("CBR_WEIGHT_SPECIES", "0.20"))
    export_quantity: float = float(get_env("CBR_WEIGHT_EXPORT_QUANTITY", "0.15"))
    raw_material: float = float(get_env("CBR_WEIGHT_RAW_MATERIAL", "0.10"))
    suppliers: float = float(get_env("CBR_WEIGHT_SUPPLIERS", "0.10"))
    invoice_count: float = float(get_env("CBR_WEIGHT_INVOICE_COUNT", "0.05"))


@dataclass(slots=True)
class CaseBase:
    cases: list[ExportCase]


def build_case(data: dict) -> ExportCase:
    suppliers = {
        nf["cnpjEmpresaNota"]
        for nf in data.get("notasFiscais", [])
        if nf.get("cnpjEmpresaNota")
    }

    return ExportCase(
        case_id=data["uuid"],
        product_type=data["tipoProduto"],
        destination_country=data["paisImportador"],
        export_quantity_kg=float(data["totalProdutoExportar"]),
        raw_material_kg=float(data["totalMateriaPrimaNecessaria"]),
        species=frozenset(data.get("especies", [])),
        suppliers=frozenset(suppliers),
        invoice_count=len(data.get("notasFiscais", [])),
        company_cnpj=data["cnpjEmpresa"],
        company_rgp=data["numRgp"],
        outcome=data["status"],
    )


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def numeric_similarity(a: float, b: float) -> float:
    if max(a, b) == 0:
        return 1.0
    return 1 - abs(a - b) / max(a, b)


def similarity(case: ExportCase, query: ExportCase, w: SimilarityWeights) -> float:
    score = 0.0
    score += w.product_type * (case.product_type == query.product_type)
    score += w.destination_country * (case.destination_country == query.destination_country)
    score += w.species * jaccard(set(case.species), set(query.species))
    score += w.suppliers * jaccard(set(case.suppliers), set(query.suppliers))
    score += w.export_quantity * numeric_similarity(case.export_quantity_kg, query.export_quantity_kg)
    score += w.invoice_count * numeric_similarity(case.invoice_count, query.invoice_count)
    score += w.raw_material * numeric_similarity(case.raw_material_kg, query.raw_material_kg)
    return score
