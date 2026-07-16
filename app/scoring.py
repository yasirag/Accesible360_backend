from typing import Dict, Any


def calculate_score(indicators: Dict[str, Any]) -> int:

    total_violations = 0
    for indicator_name, indicator_data in indicators.items():
        violations = indicator_data.get("violations", 0)
        total_violations += violations

    score = max(0, 100 - (total_violations * 5))

    return int(score)