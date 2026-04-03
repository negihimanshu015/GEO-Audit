import logging
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware

from utils.logging_config import setup_logging
from app.core.audit import run_audit
from app.models.request import AuditRequest
from app.models.response import AuditResponse
from app.services.scraper import ScrapingError
from app.config import get_settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Initialize centralized logging
setup_logging("audit.log")
logger = logging.getLogger(__name__)

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="GEO Audit API",
    description="Structured Data Recommendation Demo for AI Search visibility",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    """Returns the API health status."""
    return {"status": "ok"}

@app.post("/audit", response_model=AuditResponse, tags=["Audit"])
@limiter.limit(settings.RATE_LIMIT)
async def perform_audit(request: Request, audit_request: AuditRequest):
    """
    Executes a GEO audit for a given public webpage URL.
    Returns extracted metadata, detected schema, and AI-driven recommendations.
    """
    try:
        url_str = str(audit_request.url)
        logger.info(f"Received audit request for URL: {url_str}")
        
        response = await run_audit(url_str)
        return response

    except ScrapingError as e:
        logger.warning(f"Audit failed due to scraping error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Scraping failed: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during audit: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during the audit process."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)
