from fastapi import FastAPI
from app.api.v1.endpoints import dns
from app.core.database import engine, Base
from app.core.logging import get_logger

logger = get_logger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DNS Orchestrator API",
    description="API for orchestrating DNS records",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")

app.include_router(dns.router, prefix="/api/v1/dns", tags=["dns"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the DNS Orchestrator API"}
