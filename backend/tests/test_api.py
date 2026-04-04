import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.models.response import AuditResponse, PageData

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_perform_audit_endpoint(async_client):
    mock_response = AuditResponse(
        url="https://example.com",
        page_data=PageData(
            title="Example Title",
            headings=["H1: Example"],
            image_urls=[],
            social_links=[]
        ),
        detected_schema_type="Organization",
        json_ld={"@context": "https://schema.org", "@type": "Organization", "name": "Example"},
        geo_notes=[],
        audit_timestamp=datetime.now(timezone.utc)
    )

    with patch("main.run_audit", return_value=mock_response) as mock_run:
        response = await async_client.post(
            "/audit",
            json={"url": "https://example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == "https://example.com"
        assert data["detected_schema_type"] == "Organization"
        mock_run.assert_called_once()
