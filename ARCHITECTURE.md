
## 4. Dynamic API Versioning

This project implements a dynamic API versioning strategy that allows for easy management and scaling of different API versions (e.g., `v1`, `v2`). This is achieved by leveraging FastAPI's `APIRouter` and Python's dynamic import capabilities.

**How it Works:**

1.  **Versioned Directories:** API logic and routing definitions are organized into version-specific directories:
    *   `app/api/v1/` and `app/routes/v1/` for Version 1.
    *   `app/api/v2/` and `app/routes/v2/` for Version 2.
    *   New versions (e.g., `v3`) can be added by simply creating `app/api/v3/` and `app/routes/v3/` directories.

2.  **Centralized Router Registration (`app/main.py`):**
    The `app/main.py` file dynamically discovers and registers routers for each API version. It iterates through the `app/routes/` directory, identifies version folders (e.g., `v1`, `v2`), and then looks for a `routes.py` file within each version.

    ```python
    # Snippet from app/main.py
    from pathlib import Path
    import importlib

    routes_path = Path(__file__).parent / "routes"
    for version_pkg in routes_path.iterdir():
        if version_pkg.is_dir() and not version_pkg.name.startswith("__"):
            version = version_pkg.name
            router_file_path = version_pkg / "routes.py"
            if router_file_path.exists():
                try:
                    module = importlib.import_module(f"app.routes.{version}.routes")
                    app.include_router(
                        module.router,
                        prefix=f"/api/{version}", # Dynamic prefix based on folder name
                        tags=[f"api_{version}"]
                    )
                except Exception as e:
                    logger.warning(f"Could not import router for {version}/routes.py: {e}")
            else:
                logger.info(f"No routes.py found for version {version}")
    ```

3.  **URL Structure:**
    The `prefix=f"/api/{version}"` in `app.main.py` ensures that API endpoints are automatically prefixed with their version number in the URL.
    *   For Version 1 endpoints: `http://your-api.com/api/v1/your-endpoint`
    *   For Version 2 endpoints: `http://your-api.com/api/v2/your-endpoint`

**Benefits:**

*   **Scalability:** Easily add new API versions without modifying existing code paths.
*   **Maintainability:** Each version's logic and routing are self-contained, reducing complexity.
*   **Clear Separation:** Enforces a clear distinction between different API versions.
*   **Backward Compatibility:** Allows you to maintain older API versions while developing and deploying newer ones.

