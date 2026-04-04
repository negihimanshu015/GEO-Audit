import json
import re
import logging
from google import genai
from app.config import get_settings

logger = logging.getLogger(__name__)

# Fallback templates (used when the LLM fails)
_FALLBACK_TEMPLATES: dict[str, dict] = {
    "Article": {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Untitled Article",
        "description": "",
        "author": {"@type": "Person", "name": "Unknown Author"},
        "datePublished": "2024-01-01",
    },
    "Product": {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Unnamed Product",
        "description": "",
        "offers": {"@type": "Offer", "priceCurrency": "USD", "price": "0.00"},
    },
    "Organization": {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Unknown Organization",
        "description": "",
        "url": "",
    },
    "FAQPage": {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What is this page about?",
                "acceptedAnswer": {"@type": "Answer", "text": ""},
            }
        ],
    },
    "LocalBusiness": {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Unknown Business",
        "description": "",
        "address": {"@type": "PostalAddress", "addressLocality": "", "addressCountry": ""},
    },
}


def _build_prompt(url: str, schema_type: str, title: str, meta_description: str | None, headings: list[str]) -> str:
    top_headings = "\n".join(f"- {h}" for h in headings[:5]) or "- (none)"
    meta = meta_description or "(not provided)"
    return f"""You are a structured data expert. Generate a JSON-LD block for the webpage described below.

AUDITED URL: {url}
SUGGESTED SCHEMA TYPE: {schema_type}

PAGE TITLE: {title}
META DESCRIPTION: {meta}
TOP HEADINGS:
{top_headings}

RULES:
1. Return ONLY valid JSON — no markdown fences, no explanation, no extra text.
2. The JSON must include "@context": "https://schema.org".
3. We think the type is {schema_type}, but YOU ARE THE EXPERT. If the page clearly fits a different type (Organization, Product, Article, FAQPage, LocalBusiness), use that instead.
4. Fill all fields with realistic values inferred from the page content above.
5. The 'url' field in the JSON-LD MUST be exactly the AUDITED URL provided above ({url}).
6. The output must be parseable by Python's json.loads() without any pre-processing.
"""


def _strip_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers if the LLM adds them anyway."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


async def generate_json_ld(
    url: str,
    schema_type: str,
    title: str,
    meta_description: str | None,
    headings: list[str],
) -> dict:
    """Call LLM to produce a JSON-LD block; fall back to a minimal template on any failure."""
    settings = get_settings()

    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — using fallback template for %s", schema_type)
        return _FALLBACK_TEMPLATES.get(schema_type, _FALLBACK_TEMPLATES["Organization"]).copy()

    try:
        # Initialize the new Client with the API key from settings
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = _build_prompt(url, schema_type, title, meta_description, headings)
        
        import asyncio
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=settings.GEMINI_MODEL, 
            contents=prompt
        )
        raw = response.text

        cleaned = _strip_fences(raw)
        result = json.loads(cleaned)

        # Sanity-check: must be a dict with @context and @type
        if not isinstance(result, dict) or "@context" not in result or "@type" not in result:
            raise ValueError("Response missing required @context / @type fields")

        logger.info("LLM JSON-LD generated for schema type: %s", schema_type)
        return result

    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON (%s) — falling back", e)
    except ValueError as e:
        logger.error("LLM response failed validation (%s) — falling back", e)
    except Exception as e:
        logger.error("LLM call failed (%s) — falling back", e)

    return _FALLBACK_TEMPLATES.get(schema_type, _FALLBACK_TEMPLATES["Organization"]).copy()
