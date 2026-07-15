from playwright.async_api import Page
from typing import Dict, Any


async def run_axe_aria(page: Page) -> Dict[str, Any]:

    axe_script = """
    (async () => {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js';
        document.head.appendChild(script);

        await new Promise(resolve => {
            script.onload = resolve;
        });

        const results = await axe.run({
            runOnly: {
                type: 'rule',
                values: [
                    'aria-valid-attr',
                    'aria-valid-attr-value',
                    'button-name',
                    'link-name',
                    'aria-role',
                    'aria-hidden-focus'
                ]
            }
        });

        return results;
    })()
    """

    try:
        results = await page.evaluate(axe_script)
        return results
    except Exception as e:
        raise Exception(f"Error ejecutando axe-core (ARIA): {str(e)}")


async def parse_aria(page: Page) -> Dict[str, Any]:

    try:
        axe_results = await run_axe_aria(page)

        violations = axe_results.get("violations", [])

        violation_count = sum(len(v.get("nodes", [])) for v in violations)

        elements = []
        for violation in violations:
            for node in violation.get("nodes", []):
                elements.append({
                    "selector": node.get("target", ["unknown"])[0],
                    "html": node.get("html", "")[:100],
                    "issue": node.get("message", "Problema ARIA"),
                    "rule_id": violation.get("id", "unknown")
                })

        return {
            "indicator": "aria",
            "violations": violation_count,
            "severity": "serious" if violation_count > 0 else "none",
            "elements": elements[:10],
            "wcag_criterion": "4.1.2",
            "description": "Atributos ARIA inválidos o nombres accesibles faltantes"
        }

    except Exception as e:
        return {
            "indicator": "aria",
            "violations": 0,
            "severity": "error",
            "elements": [],
            "wcag_criterion": "4.1.2",
            "description": "Error ejecutando auditoría",
            "error": str(e)
        }