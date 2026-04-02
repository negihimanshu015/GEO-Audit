from pydantic import BaseModel, HttpUrl

class AuditRequest(BaseModel):
    """
    Model for the initial GEO audit request.
    Validates that the input is a properly formatted public webpage URL.
    """
    url: HttpUrl
