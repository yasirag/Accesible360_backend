import logging
from typing import List, Dict, Any
from app.servicios.groq_service import GroqService

logger = logging.getLogger(__name__)

SEVERITY_ORDER = {
    "links": 1,
    "forms": 2,
    "headings": 3
}


class PlanEnricher:
    def __init__(self):
        self.groq = GroqService()

    async def enrich_violations(self, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        sorted_indicators = self._sort_by_severity(indicators)
        plan = []

        for rank, (indicator, indicator_data) in enumerate(sorted_indicators, 1):
            violations_count = indicator_data.get("violations", 0)
            elements = indicator_data.get("elements", [])

            # Obtener explicación general (what/why/how)
            explanation = await self._generate_explanations(indicator, indicator_data)

            # Aplicar MISMA explicación a TODOS los elementos
            enriched_elements = []
            for idx, element in enumerate(elements):
                enriched_elements.append({
                    "index": idx,
                    "element": element,
                    "what": explanation.get("what", ""),
                    "why": explanation.get("why", ""),
                    "how": explanation.get("how", "")
                })

            plan.append({
                "rank": rank,
                "indicator": indicator,
                "violations": violations_count,
                "severity": self._get_severity(rank),
                "elements": enriched_elements
            })

        return plan

    async def _generate_explanations(self, indicator: str, indicator_data: dict):

        violations_count = indicator_data.get("violations", 0)
        elements = indicator_data.get("elements", [])

        return await self.groq.generate_plan_for_indicator(indicator, violations_count, elements)

    def _sort_by_severity(self, indicators: Dict[str, Any]) -> List[tuple]:
        sorted_list = sorted(
            indicators.items(),
            key=lambda x: SEVERITY_ORDER.get(x[0], 999)
        )
        return sorted_list

    def _get_severity(self, rank: int) -> str:
        if rank == 1:
            return "CRÍTICO"
        elif rank == 2:
            return "SERIO"
        else:
            return "MEDIO"