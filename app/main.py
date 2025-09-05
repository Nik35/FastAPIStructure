from fastapi import FastAPI
import importlib
import pkgutil
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


# Dynamically register routers for all versions in app/routes
from pathlib import Path
routes_path = Path(__file__).parent / "routes"
for version_pkg in routes_path.iterdir():
    if version_pkg.is_dir() and not version_pkg.name.startswith("__"):
        version = version_pkg.name
        router_file_path = version_pkg / "routes.py" # Specifically look for routes.py
        if router_file_path.exists():
            try:
                module = importlib.import_module(f"app.routes.{version}.routes") # Import routes module
                app.include_router(
                    module.router,
                    prefix=f"/api/{version}", # Prefix will be /api/v1, /api/v2
                    tags=[f"api_{version}"] # Tag will be api_v1, api_v2
                )
            except Exception as e:
                logger.warning(f"Could not import router for {version}/routes.py: {e}")
        else:
            logger.info(f"No routes.py found for version {version}") # Logger message if not found

@app.get("/")
def read_root():
    return {"message": "Welcome to the DNS Orchestrator API"}
