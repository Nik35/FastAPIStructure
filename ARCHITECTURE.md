# Application Architecture and Structure

This document provides an overview of the application's architecture, its key components, and the purpose of each directory.

## 1. High-Level Architecture Flow

The application is designed as a microservice that orchestrates DNS record creation, leveraging FastAPI for the API, Celery for asynchronous tasks, Kafka for messaging, and PostgreSQL for data persistence.

```mermaid
graph TD
    A[Client] --> B(FastAPI App);
    B --> C{API Endpoints};
    C --> D[API Logic];
    D --> E(Database);
    D --> F(Kafka Producer);
    F --> G[Kafka Broker];
    G --> H(Kafka Consumer);
    H --> I(Celery Task Queue);
    I --> J[Celery Worker];
    J --> K(External DNS Service);
    J --> E;
    J --> L(Logging);
    B --> L;
    H --> L;
    J --> L;
```

**Explanation of Flow:**
1.  **Client Interaction:** Clients (e.g., web UI, other services) send requests to the FastAPI App.
2.  **FastAPI App:** Receives requests and routes them to appropriate API Endpoints.
3.  **API Endpoints:** Defined in `app/routes/vX/routes.py`, these handle request parsing and delegate business logic to API Logic.
4.  **API Logic:** Located in `app/api/vX/api.py`, this contains the core business logic, interacting with the Database and potentially producing messages to Kafka.
5.  **Database (PostgreSQL):** Stores DNS request and record data.
6.  **Kafka Producer:** API Logic can produce messages to Kafka for asynchronous processing.
7.  **Kafka Broker:** Acts as a central message bus.
8.  **Kafka Consumer:** A separate service (`scripts/run_consumer.py`) consumes messages from Kafka.
9.  **Celery Task Queue:** Messages from Kafka (or direct calls from API Logic) can trigger Celery tasks.
10. **Celery Worker:** Processes asynchronous tasks, such as interacting with an External DNS Service or updating the Database.
11. **External DNS Service:** The actual service responsible for provisioning DNS records (e.g., AWS Route 53, Cloudflare).
12. **Logging:** All components log their activities, providing observability.

## 2. Directory Structure and Purpose

```
.
├── app/                  # Main application source code
│   ├── api/              # API Logic (Business Logic for Endpoints)
│   │   ├── common/       # Common API utilities shared across versions
│   │   ├── v1/           # Version 1 API logic
│   │   │   └── api.py    # Logic for v1 endpoints
│   │   └── v2/           # Version 2 API logic
│   │       └── api.py    # Logic for v2 endpoints
│   ├── celery/           # Celery-related files
│   │   ├── tasks.py      # Celery task definitions
│   │   └── celery_app.py # Celery application instance
│   ├── core/             # Core application components
│   │   ├── config.py     # Application settings and configuration
│   │   ├── database.py   # Database connection and session management
│   │   ├── logging.py    # Logging configuration
│   │   └── secrets.py    # Centralized Secrets Management (CSM) integration
│   ├── kafka/            # Kafka-related components
│   │   └── consumer.py   # Kafka consumer logic
│   ├── routes/           # API Routing Definitions
│   │   ├── v1/           # Version 1 API routes
│   │   │   └── routes.py # Route definitions for v1
│   │   └── v2/           # Version 2 API routes
│   │       └── routes.py # Route definitions for v2
│   ├── schemas/          # Pydantic models for request/response validation and database models
│   │   ├── request.py    # Request models
│   │   ├── response.py   # Response models
│   │   └── models.py     # SQLAlchemy database models
│   └── utils/            # General-purpose utility functions/modules (e.g., helpers, common functions)
├── deployment/           # Deployment-related files (Docker, Kubernetes/OpenShift manifests)
│   ├── Dockerfile.app    # Dockerfile for the FastAPI application image
│   ├── Dockerfile.worker # Dockerfile for the Celery worker image
│   ├── docker-compose.yml # Docker Compose for local development setup
│   ├── entrypoint.sh     # Main application entrypoint script for Docker
│   └── celery_worker_entrypoint.sh # Celery worker entrypoint script for Docker
├── env/                  # Environment-specific configuration files (.env files)
│   ├── .env.dev          # Development environment variables
│   ├── .env.prod         # Production environment variables
│   └── .env.uta          # User Testing Acceptance environment variables
├── scripts/              # Standalone executable scripts (e.g., run_consumer.py)
├── tests/                # Unit and integration tests
├── alembic/              # Alembic migration scripts (if initialized)
├── alembic.ini           # Alembic configuration file (if initialized)
├── pyproject.toml        # Poetry project definition and dependencies
├── poetry.lock           # Poetry lock file (exact dependency versions)
├── POETRY_GUIDE.md       # Guide for Poetry setup and usage
└── README.md             # Project overview and main entry point
```

## 3. What to Write Where

*   **`app/api/vX/api.py`**:
    *   **Purpose:** Contains the actual business logic for your API endpoints. This is where you'll write the code that interacts with the database, calls external services, or dispatches tasks.
    *   **Content:** Functions that perform operations like creating, reading, updating, or deleting resources. These functions should be pure Python functions that take necessary arguments and return data. They should *not* contain FastAPI decorators (`@router.get`, `@router.post`, etc.).
    *   **Example:** A function `create_dns_record_logic(data: DnsRequestCreate, db: Session)`

*   **`app/routes/vX/routes.py`**:
    *   **Purpose:** Defines the API endpoints and maps them to the corresponding business logic functions. This is the "routing" layer.
    *   **Content:** FastAPI `APIRouter` instances, and functions decorated with `@router.get`, `@router.post`, etc. These functions should primarily call the logic functions from `app/api/vX/api.py` and handle request/response serialization.
    *   **Example:**
        ```python
        from fastapi import APIRouter, Depends
        from app.api.v1.api import create_dns_record_logic

        router = APIRouter()

        @router.post("/create")
        def create_dns_record(request: DnsRequestCreate, db: Session = Depends(get_db)):
            return create_dns_record_logic(request, db)
        ```

*   **`app/schemas/`**:
    *   **Purpose:** Defines the data structures for your application.
    *   **Content:**
        *   `request.py`: Pydantic models for incoming request bodies.
        *   `response.py`: Pydantic models for outgoing response bodies.
        *   `models.py`: SQLAlchemy models (or other ORM models) that define your database tables.

*   **`app/core/`**:
    *   **Purpose:** Contains fundamental, cross-cutting concerns of your application.
    *   **Content:** Configuration loading, database connection setup, logging configuration, secrets management integration.

*   **`app/celery/`**:
    *   **Purpose:** Houses all Celery-related code.
    *   **Content:**
        *   `tasks.py`: Definitions of your Celery tasks (functions decorated with `@celery_app.task`).
        *   `celery_app.py`: The Celery application instance itself.

*   **`app/kafka/`**:
    *   **Purpose:** Contains Kafka-specific consumer and producer logic.
    *   **Content:** Functions or classes that interact with Kafka brokers to consume or produce messages.

*   **`app/utils/`**:
    *   **Purpose:** For general-purpose utility functions or modules that are reusable across different parts of the `app/` package and are not specific to API, database, or messaging.
    *   **Content:** Helper functions for data manipulation, common validators, custom exceptions, etc.

*   **`app/api/common/`**:
    *   **Purpose:** For utility functions or modules that are specific to the API layer but are shared across different API versions (e.g., `v1`, `v2`).
    *   **Content:** Common authentication helpers, response transformers, request pre-processors that apply to multiple API versions.

*   **`deployment/`**:
    *   **Purpose:** Contains all files related to deploying your application.
    *   **Content:** Dockerfiles, Docker Compose files, Kubernetes/OpenShift manifests (e.g., YAML files for Deployments, Services, Routes, ConfigMaps, Secrets), shell scripts for container entrypoints.

*   **`env/`**:
    *   **Purpose:** Stores environment-specific configuration variables.
    *   **Content:** `.env` files for development, production, testing, etc. (e.g., database URLs, API keys, external service endpoints). These files should NOT be committed to version control if they contain sensitive information.

*   **`scripts/`**:
    *   **Purpose:** For standalone executable Python scripts that perform specific tasks (e.g., data migration scripts, one-off administrative tasks, consumer runners).
    *   **Content:** `run_consumer.py` or similar.
