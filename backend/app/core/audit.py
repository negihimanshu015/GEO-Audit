from datetime import datetime, timezone
from app.services.scraper import scrape_page, ScrapingError
from app.core.schema_rules import detect_schema_type
from app.services.llm import generate_json_ld
from app.models.response import AuditResponse, GeoNote


def _generate_geo_notes(
    meta_description: str | None,
    headings: list[str],
    detected_schema_type: str,
    canonical_url: str | None,
    author_found: bool,
    date_found: bool,
    social_links: list[str],
) -> list[GeoNote]:
    notes: list[GeoNote] = []

    if not meta_description:
        notes.append(GeoNote(
            message="No meta description found — add one for better AI snippet coverage.",
            severity="warning"
        ))
    else:
        notes.append(GeoNote(
            message="Meta description present",
            severity="info"
        ))

    h1_count = sum(1 for h in headings if h.lower().startswith("h1:"))
    if h1_count < 1:
        notes.append(GeoNote(
            message="No H1 detected — help AI engines identify your primary entity with a clear H1.",
            severity="critical"
        ))
    elif h1_count > 1:
        notes.append(GeoNote(
            message="Multiple H1 tags found — ensure the primary H1 clearly states the organization name.",
            severity="critical"
        ))
    else:
        notes.append(GeoNote(
            message="Structured headings present",
            severity="info"
        ))

    if detected_schema_type in ("Article", "BlogPosting", "NewsArticle"):
        if not author_found:
            notes.append(GeoNote(
                message="No author found on page — add visible author markup for AI citation trust.",
                severity="critical"
            ))
        if not date_found:
            notes.append(GeoNote(
                message="No publish date detected — add a visible date for temporal relevance scoring.",
                severity="critical"
            ))

    if len([h for h in headings if "?" in h]) >= 2 and detected_schema_type != "FAQPage":
        notes.append(GeoNote(
            message="Multiple question headings detected — consider adding FAQ schema for natural language query coverage.",
            severity="warning"
        ))

    if not social_links:
        notes.append(GeoNote(
            message="No entity links found — link to your LinkedIn, Wikipedia, or Wikidata profile via sameAs.",
            severity="warning"
        ))
    else:
        notes.append(GeoNote(
            message="Social profile detected",
            severity="info"
        ))

    if not canonical_url:
        notes.append(GeoNote(
            message="No canonical URL tag detected — add one to establish a stable citation source for AI engines.",
            severity="warning"
        ))
    else:
        notes.append(GeoNote(
            message="Canonical URL detected",
            severity="info"
        ))

    return notes


async def run_audit(url: str) -> AuditResponse:
    try:
        page_data = await scrape_page(url)
    except ScrapingError as e:
        raise ScrapingError(f"Audit failed during scrape: {e.message}") from e

    detected_schema_type = detect_schema_type(
        url=url,
        title=page_data.title,
        meta_description=page_data.meta_description,
        headings=page_data.headings,
    )

    json_ld = await generate_json_ld(
        url=url,
        schema_type=detected_schema_type,
        title=page_data.title,
        meta_description=page_data.meta_description,
        headings=page_data.headings,
    )

    if "@type" in json_ld:
        detected_schema_type = str(json_ld["@type"])

    # Inject detected social links into the schema for better entity linkage
    if page_data.social_links:
        json_ld["sameAs"] = list(dict.fromkeys(
            (json_ld.get("sameAs") if isinstance(json_ld.get("sameAs"), list) else [json_ld["sameAs"]] if "sameAs" in json_ld else []) + 
            page_data.social_links
        ))

    geo_notes = _generate_geo_notes(
        meta_description=page_data.meta_description,
        headings=page_data.headings,
        detected_schema_type=detected_schema_type,
        canonical_url=page_data.canonical_url,
        author_found=page_data.author_found,
        date_found=page_data.date_found,
        social_links=page_data.social_links,
    )

    return AuditResponse(
        url=url,
        page_data=page_data,
        detected_schema_type=detected_schema_type,
        json_ld=json_ld,
        geo_notes=geo_notes,
        audit_timestamp=datetime.now(timezone.utc),
    )