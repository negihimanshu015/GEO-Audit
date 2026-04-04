import re
import copy
import logging
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.models.response import PageData

logger = logging.getLogger(__name__)

# Constants

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_SOCIAL_PATTERNS: dict[str, list[str]] = {
    "linkedin":  ["linkedin.com/in/", "linkedin.com/company/"],
    "x_twitter": ["twitter.com/", "x.com/"],
    "wikipedia": ["wikipedia.org/wiki/"],
    "wikidata":  ["wikidata.org/wiki/"],
}

_IMG_MAX = 5
_IMG_MIN_SIZE = 10  

# Custom Exception

class ScrapingError(Exception):
    pass

# Private Helpers

def _brand_from_url(url: str) -> str | None:
    """Extract the primary domain name to use as a brand hint."""
    parts = urlparse(url).netloc.split(".")
    if len(parts) < 2:
        return None
    brand = parts[-2]
    # Skip 'www' and step back one level
    if brand == "www" and len(parts) >= 3:
        brand = parts[-3]
    return brand


def _clean_title(title: str, brand_hint: str | None = None) -> str:
    """Remove trailing brand/duplicate segments from a page title."""
    if not title:
        return ""
    title = title.replace("\\", "/").strip()

    # Split on common title separators, keeping the separators
    parts = re.split(r"(\s*[|/\-·—:]\s*)", title)
    segments = [p.strip() for p in parts[0::2]]  # even indices = content
    seps     = parts[1::2]                        # odd  indices = separators

    # Drop trailing segments that repeat an earlier one or match the brand
    while len(segments) > 1:
        last = segments[-1].lower()
        if not last:
            segments.pop(); seps and seps.pop()
            continue
        is_repeat = (brand_hint and last == brand_hint.lower()) or any(
            prev.lower() and (last == prev.lower() or last in prev.lower())
            for prev in segments[:-1]
        )
        if is_repeat:
            segments.pop(); seps and seps.pop()
        else:
            break

    result = segments[0]
    for i, sep in enumerate(seps):
        if i + 1 < len(segments):
            result += f"{sep}{segments[i + 1]}"
    return result.strip()


def _clean_heading(text: str) -> str:
    """Collapse whitespace and remove exact string/word-level repetition."""
    text = re.sub(r'\s+', ' ', text).strip()
    prev = None
    while text != prev:
        prev = text
        n = len(text)
        # Character-level repetition (e.g. "abab" → "ab")
        for i in range(1, n // 2 + 1):
            if n % i == 0 and text[:i] * (n // i) == text:
                text = text[:i].strip()
                break
        # Word-level repetition (e.g. "foo bar foo bar" → "foo bar")
        words = text.split()
        half = len(words) // 2
        if len(words) >= 2 and len(words) % 2 == 0 and words[:half] == words[half:]:
            text = " ".join(words[:half])
    return text


def _clean_social_url(href: str) -> str:
    """Strip anchors, query params, trailing slashes, and normalise @ handles."""
    href = href.split("#")[0].split("?")[0].rstrip("/")
    return href.replace("/@", "/")


# Extraction Functions

def _extract_title(soup: BeautifulSoup, brand_hint: str | None) -> str:
    tag = soup.find("title")
    og  = soup.find("meta", property="og:title")
    raw = tag.get_text(strip=True) if tag else (og.get("content", "") if og else "")
    return _clean_title(raw, brand_hint=brand_hint)


def _extract_meta_description(soup: BeautifulSoup) -> str | None:
    meta = soup.find("meta", attrs={"name": "description"})
    og   = soup.find("meta", property="og:description")
    if meta:
        return meta.get("content", "").strip() or None
    return og.get("content", "") if og else None


def _extract_headings(soup: BeautifulSoup) -> list[str]:
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        if tag.find_parent(["nav", "header", "footer", "aside"]):
            continue
        clone = copy.copy(tag)
        for hidden in clone.find_all(attrs={"aria-hidden": "true"}): hidden.decompose()
        for hidden in clone.find_all(attrs={"hidden": True}):        hidden.decompose()
        text = _clean_heading(clone.get_text(" ", strip=True).replace("¶", ""))
        if text:
            headings.append(f"{tag.name}: {text}")
    return headings


def _score_image(img, src: str) -> int:
    """Heuristic score: higher = more likely to be a meaningful image."""
    tag_id    = (img.get("id")    or "").lower()
    tag_class = " ".join(img.get("class") or []).lower()
    src_lower = src.lower()
    if "logo"   in (tag_id + tag_class + src_lower): return 10
    if any(k in (tag_id + tag_class + src_lower) for k in ("hero", "banner")): return 8
    return 0


def _extract_images(soup: BeautifulSoup, url: str) -> list[str]:
    candidates: list[tuple[int, str]] = []

    # High-priority meta tags
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        candidates.append((15, urljoin(url, og["content"])))

    tw = soup.find("meta", attrs={"name": "twitter:image"})
    if tw and tw.get("content"):
        candidates.append((12, urljoin(url, tw["content"])))

    # Inline <img> tags
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src.startswith("data:"):
            continue
        try:
            if int(img.get("width", _IMG_MIN_SIZE)) < _IMG_MIN_SIZE: continue
            if int(img.get("height", _IMG_MIN_SIZE)) < _IMG_MIN_SIZE: continue
        except ValueError:
            pass
        candidates.append((_score_image(img, src), urljoin(url, src)))

    # Sort, deduplicate, and cap
    candidates.sort(key=lambda x: x[0], reverse=True)
    seen, images = set(), []
    for _, img_url in candidates:
        if img_url not in seen:
            images.append(img_url)
            seen.add(img_url)
        if len(images) == _IMG_MAX:
            break
    return images


def _extract_social_links(soup: BeautifulSoup) -> list[str]:
    found: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        href = _clean_social_url(a["href"]).lower()
        for platform, patterns in _SOCIAL_PATTERNS.items():
            if platform not in found and any(p in href for p in patterns):
                found[platform] = _clean_social_url(a["href"])
                break
    return list(found.values())


def _check_metadata_presence(soup: BeautifulSoup) -> tuple[bool, bool]:
    """Return (author_found, date_found)."""
    author = bool(
        soup.find("meta", attrs={"name": "author"}) or
        soup.find("meta", property="article:author") or
        soup.find("a", rel="author") or
        soup.find(class_=re.compile(r"author|byline", re.I)) or
        soup.find(id=re.compile(r"author|byline", re.I))
    )
    date = bool(
        soup.find("meta", property="article:published_time") or
        soup.find("meta", attrs={"name": "publish-date"}) or
        soup.find("time", datetime=True) or
        soup.find(class_=re.compile(r"date|published|time", re.I))
    )
    return author, date

# Public API 

async def scrape_page(url: str) -> PageData:
    brand_hint = _brand_from_url(url)

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            r = await client.get(url, headers=_HEADERS)
            r.raise_for_status()
            if str(r.url).rstrip("/") != url.rstrip("/"):
                logger.info(f"Redirected to: {r.url}")
    except httpx.HTTPStatusError as e:
        raise ScrapingError(f"HTTP {e.response.status_code}: {e.response.reason_phrase}")
    except httpx.RequestError as e:
        raise ScrapingError(f"Request failed: {e}")

    try:
        soup = BeautifulSoup(r.text, "html.parser")
        canonical = soup.find("link", rel="canonical")
        author_found, date_found = _check_metadata_presence(soup)

        return PageData(
            title=_extract_title(soup, brand_hint),
            meta_description=_extract_meta_description(soup),
            headings=_extract_headings(soup),
            image_urls=_extract_images(soup, url),
            canonical_url=canonical.get("href") if canonical else None,
            author_found=author_found,
            date_found=date_found,
            social_links=_extract_social_links(soup),
        )
    except Exception as e:
        raise ScrapingError(f"Parse error: {e}")
