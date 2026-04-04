import pytest
from unittest.mock import patch, AsyncMock
from app.core.audit import run_audit
from app.services.llm import generate_json_ld
from app.models.response import PageData

@pytest.mark.asyncio
async def test_run_audit_logic():
    mock_page_data = PageData(
        title="Test Page",
        meta_description="Test Description",
        headings=["h1: Welcome"],
        image_urls=[],
        social_links=[]
    )
    mock_json_ld = {"@context": "https://schema.org", "@type": "Article", "headline": "Test Page"}

    with patch("app.core.audit.scrape_page", new_callable=AsyncMock) as mock_scrape:
        with patch("app.core.audit.generate_json_ld", new_callable=AsyncMock) as mock_llm:
            mock_scrape.return_value = mock_page_data
            mock_llm.return_value = mock_json_ld
            response = await run_audit("https://test.com")
            
            assert response.url == "https://test.com"
            assert response.page_data.title == "Test Page"
            assert response.json_ld == mock_json_ld
            assert len(response.geo_notes) > 0

@pytest.mark.asyncio
async def test_llm_fallback_mechanism():
    url = "https://fail.com"
    schema_type = "Article"
    title = "Failure"
    meta = None
    headings = []

    with patch("app.services.llm.genai.Client") as mock_client:
        mock_client.side_effect = Exception("API Error")
        result = await generate_json_ld(url, schema_type, title, meta, headings)
        
        assert result["@type"] == "Article"
        assert "@context" in result
        assert result["headline"] == "Untitled Article"
