from api.services.cbr_core import ExportCase, SimilarityWeights
from api.services.cbr_retrieval import retrieve_similar_cases


def suggest_improvements(
    query: ExportCase,
    weights: SimilarityWeights | None = None,
    top_k: int = 5,
) -> list[str]:
    similar = retrieve_similar_cases(query, weights, top_k)
    if not similar:
        return ["No similar cases found for comparison."]

    approved = [case for case, _ in similar if case.outcome == "DEFERIDA"]
    rejected = [case for case, _ in similar if case.outcome != "DEFERIDA"]

    suggestions = []

    if rejected:
        suggestions.append(
            f"{len(rejected)} of {len(similar)} similar cases had issues. "
            "Review their profiles to avoid common pitfalls."
        )
        rejected_species = set()
        for case in rejected:
            rejected_species.update(case.species)
        if rejected_species:
            suggestions.append(
                f"Species that appeared in rejected cases: "
                f"{', '.join(sorted(rejected_species)[:5])}"
            )

    if approved:
        avg_quantity = sum(case.export_quantity_kg for case in approved) / len(approved)
        suggestions.append(
            f"Approved cases averaged {avg_quantity:,.0f} kg exported. "
            f"Your quantity: {query.export_quantity_kg:,.0f} kg."
        )
        common_destinations = {}
        for case in approved:
            common_destinations[case.destination_country] = (
                common_destinations.get(case.destination_country, 0) + 1
            )
        top_dest = max(common_destinations, key=common_destinations.get)
        if top_dest != query.destination_country:
            suggestions.append(
                f"Most common destination in approved cases: {top_dest}. "
                f"Your destination: {query.destination_country}."
            )

    return suggestions
