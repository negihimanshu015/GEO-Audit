import httpx
import logging
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.models.response import PageData

logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _clean_title(title: str) -> str:
    """
    Cleans page titles by removing redundant branding artifacts.
    Logic:
    1. Splits on common separators: | / - · —
    2. If the last segment is a case-insensitive repeat of an earlier segment, strip it.
    3. Handles multiple repetitions (e.g., Brand / Brand / Brand).
    """
    if not title:
        return ""

    # Normalize backslashes to forward slashes first
    title = title.replace("\\", "/").strip()

    # Pattern for splitting while keeping the separators
    # Separators: | / - · —
    separators = r"[|/\-·—]"
    parts = re.split(f"(\s*{separators}\s*)", title)
    
    if len(parts) <= 1:
        return title

    segments = []
    seps = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            segments.append(part.strip())
        else:
            seps.append(part)

    # Deduplicate from the end
    while len(segments) > 1:
        last_segment = segments[-1].lower()
        if not last_segment:
            segments.pop()
            if seps: seps.pop()
            continue
            
        is_repeat = False
        for i in range(len(segments) - 1):
            prev_segment = segments[i].lower()
            if not prev_segment: continue
            # Check for exact match or if the brand is already in the main title
            if last_segment == prev_segment or last_segment in prev_segment:
                is_repeat = True
                break
        
        if is_repeat:
            segments.pop()
            if seps: seps.pop()
        else:
            break

    # Reconstruct with original separators
    res = segments[0]
    for i in range(len(seps)):
        if i + 1 < len(segments):
            res += f"{seps[i]}{segments[i+1]}"
            
    return res.strip()


async def scrape_page(url: str) -> PageData:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0, verify=False) as client:
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

        # Title extraction and cleaning
        title_tag = soup.find("title")
        og_title = soup.find("meta", property="og:title")
        title = (title_tag.get_text(strip=True) if title_tag
                 else (og_title.get("content", "") if og_title else ""))
        title = _clean_title(title)

        # Meta description
        desc = soup.find("meta", attrs={"name": "description"})
        og_desc = soup.find("meta", property="og:description")
        meta_description = (desc.get("content", "").strip() if desc
                            else (og_desc.get("content", "") if og_desc else None))

        # Headings (H1–H3)
        headings = [
            f"{tag.name}: {tag.get_text(strip=True).replace('¶', '').strip()}"
            for tag in soup.find_all(["h1", "h2", "h3"])
            if tag.get_text(strip=True) and not tag.find_parent(["nav", "header", "footer", "aside"])
        ]

        # Image extraction
        meta_images = []
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            meta_images.append(urljoin(url, og_img["content"]))
            
        twitter_img = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_img and twitter_img.get("content"):
            meta_images.append(urljoin(url, twitter_img["content"]))

        scored_images = []
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue
                
            try:
                if int(img.get("width", 10)) < 10 or int(img.get("height", 10)) < 10:
                    continue
            except ValueError:
                pass
                
            full_src = urljoin(url, src)
            
            # Priority scoring based on IDs, classes, and src
            score = 0
            tag_id = (img.get("id") or "").lower()
            tag_class = " ".join(img.get("class") or []).lower()
            src_lower = src.lower()
            
            if "logo" in tag_id or "logo" in tag_class or "logo" in src_lower:
                score += 10
            elif "hero" in tag_id or "hero" in tag_class or "hero" in src_lower or "banner" in src_lower:
                score += 8
                
            scored_images.append((score, full_src))

        scored_images.sort(key=lambda x: x[0], reverse=True)
        
        images = []
        seen = set()
        for img_url in meta_images + [img[1] for img in scored_images]:
            if img_url not in seen:
                images.append(img_url)
                seen.add(img_url)
            if len(images) == 5:
                break

        canonical_tag = soup.find("link", rel="canonical")
        canonical_url = canonical_tag.get("href") if canonical_tag else None

        author_found = any([
            soup.find("meta", attrs={"name": "author"}),
            soup.find("meta", property="article:author"),
            soup.find("a", rel="author"),
            soup.find(class_=re.compile("author|byline", re.I)),
            soup.find(id=re.compile("author|byline", re.I))
        ])

        date_found = any([
            soup.find("meta", property="article:published_time"),
            soup.find("meta", attrs={"name": "publish-date"}),
            soup.find("time", datetime=True),
            soup.find(class_=re.compile("date|published|time", re.I)),
        ])

        # Extract LinkedIn, X, Wikipedia, or Wikidata links
        social_links = []
        social_patterns = [
            "linkedin.com/in/", "linkedin.com/company/",
            "twitter.com/", "x.com/",
            "wikipedia.org/wiki/", "wikidata.org/wiki/"
        ]
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(p in href.lower() for p in social_patterns):
                social_links.append(href)
        
        social_links = list(dict.fromkeys(social_links))[:10]

        return PageData(
            title=title or "No Title Found",
            meta_description=meta_description,
            headings=headings,
            image_urls=images,
            canonical_url=canonical_url,
            author_found=bool(author_found),
            date_found=bool(date_found),
            social_links=social_links
        )

    except Exception as e:
        raise ScrapingError(f"Parse error: {e}")
