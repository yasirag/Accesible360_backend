from typing import Dict, Any


def calculate_score(indicators: Dict[str, Any]) -> int:

    forms_violations = indicators.get("forms", {}).get("violations", 0)

    # Score base 100, restar puntos por violaciones
    score = max(0, 100 - (forms_violations * 5))

    return int(score)