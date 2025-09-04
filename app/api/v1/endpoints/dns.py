"""Updated endpoint to use dynamic API versioning from config.py"""

from fastapi import APIRouter
from config import API_VERSION  # Import the API_VERSION variable

router = APIRouter(prefix=f"/api/{API_VERSION}")  # Use dynamic versioning

@router.get("/dns")
async def get_dns():
    return {"message": "This is the DNS endpoint."}

# Add other endpoint definitions here, removing hardcoded versioning.