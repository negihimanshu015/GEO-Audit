from typing import Optional
from urllib.parse import urlparse

# Keyword groups for each schema type
_SCHEMA_KEYWORDS: dict[str, list[str]] = {
    "Article":       ["blog", "post", "author", "published", "news", "article"],
    "Product":       ["price", "buy", "cart", "shop", "sku", "add to"],
    "Organization":  [
        "about us", "our team", "founded", "mission", "contact",
        "learn more", "foundation", "nonprofit", "software foundation",
        "jobs", "download", "docs", "events"
    ],
    "FAQPage":       ["faq", "frequently asked", "question"],
    "LocalBusiness": ["hours", "address", "directions", "location"],
}


def detect_schema_type(
    url: str,
    title: str,
    meta_description: Optional[str],
    headings: list[str],
) -> str:
    """Score keyword groups against page text and URL path; return the winning schema type.

    Prioritizes URIs (homepages/blogs) before keyword scoring.
    Falls back to 'Organization' when no group reaches a score of 1.
    """
    parsed = urlparse(url)
    path = parsed.path.lower().strip("/")    
    
    if not path:
        return "Organization"  
    
    if any(p in path for p in ["blog", "news", "articles"]):
        return "Article"
    
    corpus = " ".join(
        filter(None, [title, meta_description or "", *headings])
    ).lower()

    scores: dict[str, int] = {}
    for schema_type, keywords in _SCHEMA_KEYWORDS.items():
        scores[schema_type] = sum(kw in corpus for kw in keywords)

    best_type = max(scores, key=lambda k: scores[k])
    return best_type if scores[best_type] > 0 else "Organization"
