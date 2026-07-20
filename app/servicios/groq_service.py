import re
import logging
import json
from groq import Groq
from app.config import get_settings

logger = logging.getLogger(__name__)


class GroqService:

    def __init__(self):
        settings = get_settings()
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
        self.max_tokens = settings.groq_max_tokens

    async def generate_plan_for_indicator(self, indicator: str, violations_count: int, elements: list):

        indicator_name = {"forms": "etiquetas de formulario", "headings": "estructura de títulos",
                          "links": "descripción de enlaces"}.get(indicator, indicator)

        elements_sample = elements[:3] if elements else []
        elements_str = json.dumps(elements_sample, indent=2, ensure_ascii=False)

        prompt = f"""Mi sitio web tiene {violations_count} problemas de {indicator_name}.

        Ejemplos de problemas encontrados:
        {elements_str}

        Responde EXACTAMENTE así (sin incluir instrucciones, SOLO respuestas):

        [QUÉ]
        Qué está mal específicamente en estos ejemplos. Máximo 50 palabras.
        [FIN_QUÉ]

        [POR_QUÉ]
        Por qué afecta a usuarios con discapacidad. Máximo 50 palabras.
        [FIN_POR_QUÉ]

        [CÓMO]
        Cómo se arregla. Pasos concretos. Máximo 50 palabras.
        [FIN_CÓMO]"""

        try:
            logger.info(f"[GROQ] Enviando request para {indicator}...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "Eres un experto en accesibilidad web. Responde en español, lenguaje simple."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.5
            )

            logger.info(f"[GROQ] Status OK, parseando...")
            text = response.choices[0].message.content
            result = self._parse_sections(text)
            logger.info(f"[GROQ] Resultado: {result}")
            return result

        except Exception as e:
            logger.error(f"[GROQ ERROR] {type(e).__name__}: {str(e)}")
            return {"what": "", "why": "", "how": ""}

    @staticmethod
    def _parse_sections(text):
        sections = {"what": "", "why": "", "how": ""}

        que_match = re.search(r'\[QUÉ\](.*?)\[FIN_QUÉ\]', text, re.DOTALL)
        por_que_match = re.search(r'\[POR_QUÉ\](.*?)\[FIN_POR_QUÉ\]', text, re.DOTALL)
        como_match = re.search(r'\[CÓMO\](.*?)\[FIN_CÓMO\]', text, re.DOTALL)

        if que_match:
            sections["what"] = que_match.group(1).strip()
        if por_que_match:
            sections["why"] = por_que_match.group(1).strip()
        if como_match:
            sections["how"] = como_match.group(1).strip()

        return sections
