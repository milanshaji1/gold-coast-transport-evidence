"""Read-only in-memory queries over canonical aggregates; no arbitrary SQL surface."""

import re

from transport.retrieval import Retriever


class EvidenceTools:
    def __init__(self, results, documents):
        self.results = results
        self.retriever = Retriever(documents)

    def envelope(self, period=None, filters=None):
        return {
            "snapshot_id": self.results["snapshot_id"],
            "period": period,
            "filters": filters or {},
            "metric_definitions": {
                "crashes": "distinct casualty crash events",
                "serious_crashes": "Fatal or Hospitalisation crash events",
                "serious_casualties": "fatal plus hospitalised people",
            },
            "source_locators": ["evidence/results.json", "evidence/source-manifest.json"],
        }

    def aggregate_stats(self, start_year, end_year, severity="All"):
        if (
            type(start_year) is not int
            or type(end_year) is not int
            or not 2020 <= start_year <= end_year <= 2024
        ):
            raise ValueError("explicit period within 2020–2024 required")
        if severity not in ("All", "Fatal", "Hospitalisation", "Medical treatment", "Minor injury"):
            raise ValueError("unsupported severity")
        rows = [
            r
            for r in self.results["monthly"]
            if start_year <= r["year"] <= end_year
            and (severity == "All" or r["severity"] == severity)
        ]
        return self.envelope([start_year, end_year], {"severity": severity}) | {
            "status": "ok" if rows else "no_records",
            **{
                k: sum(r[k] for r in rows)
                for k in ["crashes", "serious_crashes", "serious_casualties"]
            },
        }

    def inspect_area(self, cell_id):
        if not isinstance(cell_id, str) or not re.fullmatch(r"-?\d{1,6}_-?\d{1,6}", cell_id):
            raise ValueError("invalid cell ID")
        area = next((r for r in self.results["shortlist"] if r["cell_id"] == cell_id), None)
        if area is None:
            raise ValueError("cell not in published top-40 shortlist")
        return self.envelope([2021, 2023], {"cell_id": cell_id}) | {
            "area": area,
            "holdout_period": [2024, 2024],
            "interpretation": "Investigation candidate; not a risk-per-trip or engineering treatment recommendation.",
        }

    def quality_provenance(self):
        return self.envelope([2020, 2024]) | {
            "quality": self.results["quality"],
            "limitations": [
                "Current revised source snapshot, not historical as-of data",
                "No traffic exposure denominator",
                "Current boundary may disagree with source jurisdiction",
                "Independent project; no council endorsement",
            ],
        }

    def search_documents(self, query, limit=5):
        return self.envelope(filters={"query": query}) | {
            "documents": self.retriever.search(query, limit),
            "guidance_checked": "2026-10-05",
            "status_note": "Only current corpus passages returned; check publisher for later changes.",
        }
