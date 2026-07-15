
from typing import Dict, Any
from playwright.async_api import Page


async def run_axe_contrast(page: Page) -> Dict[str, Any]:


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
                values: ['color-contrast']
            }
        });

        return results;
    })()
    """

    try:
        results = await page.evaluate(axe_script)
        return results
    except Exception as e:
        raise Exception(f"Error ejecutando axe-core: {str(e)}")


async def parse_contrast(page: Page) -> Dict[str, Any]:

    try:
        axe_results = await run_axe_contrast(page)

        violations = axe_results.get("violations", [])
        contrast_violations = [v for v in violations if v.get("id") == "color-contrast"]

        violation_count = sum(len(v.get("nodes", [])) for v in contrast_violations)

        elements = []
        for violation in contrast_violations:
            for node in violation.get("nodes", []):
                elements.append({
                    "selector": node.get("target", ["unknown"])[0],
                    "html": node.get("html", "")[:100],
                    "issue": node.get("message", "Contraste bajo")
                })

        return {
            "indicator": "contrast",
            "violations": violation_count,
            "severity": "critical" if violation_count > 0 else "none",
            "elements": elements[:10],
            "wcag_criterion": "1.4.3",
            "description": "Contraste insuficiente entre texto y fondo"
        }

    except Exception as e:
        return {
            "indicator": "contrast",
            "violations": 0,
            "severity": "error",
            "elements": [],
            "wcag_criterion": "1.4.3",
            "description": "Error ejecutando auditoría",
            "error": str(e)
        }