from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class PageData(BaseModel):
    title: str
    meta_description: Optional[str] = None
    headings: List[str]
    image_urls: List[str]
    canonical_url: Optional[str] = None
    author_found: bool = False
    date_found: bool = False
    social_links: List[str] = []

class GeoNote(BaseModel):
    message: str
    severity: Literal["critical", "warning", "info"]

class AuditResponse(BaseModel):
    """
    Serialized response for a GEO audit.
    """
    url: str
    page_data: PageData
    detected_schema_type: str
    json_ld: Dict[str, Any]
    geo_notes: List[GeoNote]
    audit_timestamp: datetime
