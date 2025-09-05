# DNS Request Orchestrator (FastAPI, PostgreSQL, Kafka, Celery)

This project provides a robust and scalable backend API for a DNS request orchestration service. It's built with FastAPI, uses PostgreSQL for data persistence, Kafka for messaging, and Celery for asynchronous task processing.

## Project Overview and Architecture

For a detailed understanding of the application's architecture, component interactions, and the purpose of each directory, please refer to:

*   [**ARCHITECTURE.md**](ARCHITECTURE.md)

## Development Setup

This project uses [Poetry](https://python-poetry.org/) for dependency management.

### 1. Poetry Setup

If you haven't set up Poetry for this project yet, please follow the instructions in:

*   [**POETRY_GUIDE.md**](POETRY_GUIDE.md)

### 2. Running with Docker Compose (Recommended)

This is the recommended way to run the entire application stack for development. It will start the FastAPI application, PostgreSQL, Kafka, Redis, and the Celery worker(s) with a single command.

**Automatic Database Migrations:**

The Docker setup now automatically initializes Alembic (if not already present) and applies all database migrations before starting the app, worker, or consumer. Alembic migrations are now located in `app/models/migrations/` for consistency. This is handled by the `deployment/entrypoint.sh` script, so you do not need to run Alembic commands manually.

## Database Migrations (Alembic)

This project uses Alembic for database migrations. The migration scripts are located in `app/models/migrations/`.

**Basic Alembic Commands (run with `poetry run`):**

1.  **Initialize Alembic (already done for this project):**
    ```bash
    # This command was used to set up alembic.ini and the migrations folder structure.
    # You typically only run this once per project.
    poetry run alembic init app/models/migrations
    ```
    *(Note: This command was simulated, as Alembic was not installed. The files have been manually created.)*

2.  **Configure Alembic (`app/models/migrations/env.py`):**
    - Ensure `app/models/migrations/env.py` correctly imports your SQLAlchemy `Base` and models.
    - Example snippet from `env.py`:
      ```python
      from app.core.database import Base
      from app.models.models import DnsRequest, DnsRecord # Import all your models
      target_metadata = Base.metadata
      ```

3.  **Create a new migration script:**
    ```bash
    poetry run alembic revision --autogenerate -m "Description of your changes"
    ```
    This will create a new Python file in `app/models/migrations/versions/` with `upgrade()` and `downgrade()` functions.

4.  **Apply migrations to the database:**
    ```bash
    poetry run alembic upgrade head
    ```
    This applies all pending migrations to your database.

5.  **Revert migrations:**
    ```bash
    poetry run alembic downgrade -1 # Revert the last migration
    poetry run alembic downgrade base # Revert all migrations
    ```

**Steps:**

1.  **Install Docker and Docker Compose**

    Ensure you have Docker and Docker Compose installed on your system.

2.  **Run Docker Compose with Environment Selection**

    By default, the app uses `.env.dev`. To use a different environment (e.g., UTA or prod), set the ENV variable:

    **Windows PowerShell:**
    ```powershell
    $env:ENV="uta"; docker compose -f deployment/docker-compose.yml up --build
    $env:ENV="prod"; docker compose -f deployment/docker-compose.yml up --build
    ```

    **Linux/macOS Bash:**
    ```bash
    ENV=uta docker compose -f deployment/docker-compose.yml up --build
    ENV=prod docker compose -f deployment/docker-compose.yml up --build
    ```

    The API will be available at `http://127.0.0.1:8000`.

---

**Note:**

- The `deployment/entrypoint.sh` script will:
    - Wait for the database to be ready
    - Initialize Alembic migrations if the `app/models/migrations/` folder does not exist
    - Always run `alembic -c alembic.ini upgrade head` to apply migrations
    - Start the main service (app, worker, or consumer)

You can find and customize this logic in `deployment/entrypoint.sh`.

### 3. Running Individual Components with Docker

If you want to run each component as a separate Docker container, you can follow these steps:

1.  **Create a Docker Network**

    ```bash
    docker network create my-network
    ```

2.  **Run Infrastructure Services (PostgreSQL, Redis, Kafka, Zookeeper)**

    ```bash
    # PostgreSQL container
    docker run -d --name postgres --network my-network -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dns_orchestrator -p 5432:5432 postgres

    # Redis container
    docker run -d --name redis --network my-network -p 6379:6379 redis:6.2-alpine

    # Kafka and Zookeeper containers
    docker run -d --name zookeeper --network my-network -p 2181:2181 confluentinc/cp-zookeeper
    docker run -d --name kafka --network my-network -p 9092:9092 -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092 -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT -e KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 confluentinc/cp-kafka
    ```

3.  **Build Application and Worker Images**

    ```bash
    docker build -t fastapi-app -f deployment/Dockerfile.app .
    docker build -t celery-worker -f deployment/Dockerfile.worker .
    ```

4.  **Run the FastAPI Application**

    ```bash
    docker run -d --name app --network my-network -p 8000:8000 \
      -e DATABASE_URL="postgresql://user:password@postgres/dns_orchestrator" \
      -e KAFKA_BROKER_URL="kafka:29092" \
      -e CELERY_BROKER_URL="redis://redis:6379/0" \
      fastapi-app
    ```

5.  **Run the Kafka Consumer**

    ```bash
    docker run -d --name consumer --network my-network \
      -e DATABASE_URL="postgresql://user:password@postgres/dns_orchestrator" \
      -e KAFKA_BROKER_URL="kafka:29092" \
      fastapi-app python scripts/run_consumer.py
    ```

6.  **Run the Celery Worker**

    ```bash
    docker run -d --name worker --network my-network \
      -e DATABASE_URL="postgresql://user:password@postgres/dns_orchestrator" \
      -e CELERY_BROKER_URL="redis://redis:6379/0" \
      -e CELERY_WORKER_CONCURRENCY=2 \
      -e CELERY_QUEUE=dns_tasks \
      -e CELERY_WORKER_LOG_LEVEL=INFO \
      celery-worker
    ```

### 4. Manual Setup

If you prefer to run the services manually (without Docker), you can follow these steps:

#### 1. Install Infrastructure Services

Ensure you have PostgreSQL, Redis, and Kafka instances running. Docker is a great way to get started with these.

```bash
# Example: PostgreSQL container
docker run --name my-postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dns_orchestrator -p 5432:5432 -d postgres

# Example: Redis container
docker run --name my-redis -p 6379:6379 -d redis:6.2-alpine

# Example: Kafka and Zookeeper containers
docker run -p 2181:2181 -d --name zookeeper confluentinc/cp-zookeeper
docker run -p 9092:9092 -d --name kafka -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT -e KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 --link zookeeper confluentinc/cp-kafka
```

#### 2. Install Python Dependencies with Poetry

It is highly recommended to use a Python virtual environment managed by Poetry.

```bash
# Navigate to your project root
cd /path/to/your/project

# Install dependencies
poetry install
```

#### 3. Set Environment Variables

This project supports environment-specific configuration using `.env` files located in the `env/` directory.

Copy the appropriate file to `.env` in your project root before running the application. For example:

```bash
cp env/.env.dev .env
```

The application will automatically load environment variables from `.env` using `python-dotenv`.

#### 4. Run the Backend Server

Start the FastAPI server using uvicorn, specifying the environment (dev, uta, prod):

**Windows PowerShell:**
```powershell
$env:ENV="dev"; poetry run uvicorn app.main:app --reload
$env:ENV="uta"; poetry run uvicorn app.main:app --reload
$env:ENV="prod"; poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Linux/macOS Bash:**
```bash
ENV=dev poetry run uvicorn app.main:app --reload
ENV=uta poetry run uvicorn app.main:app --reload
ENV=prod poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

#### 5. Run the Kafka Consumer

In a separate terminal, start the Kafka consumer to process the tasks.

```bash
poetry run python scripts/run_consumer.py
```

#### 6. Run the Celery Worker

In a separate terminal, start the Celery worker to process the tasks.

```bash
poetry run celery -A app.core.celery_app worker --loglevel=info -Q dns_tasks
```

## API Endpoints

The API provides the following endpoints, with dynamic versioning:

*   **`/api/v1/dns/create` (POST)**: Submits a new DNS record request using v1 logic.
*   **`/api/v1/dns/{request_id}` (GET)**: Retrieves the status of a specific DNS request using v1 logic.
*   **`/api/v1/dns/update_status/{request_id}` (POST)**: Updates the status of a specific DNS record request using v1 logic.
*   **`/api/v2/dns/create` (POST)**: Submits a new DNS record request using v2 logic.
*   **`/api/v2/dns/{request_id}` (GET)**: Retrieves the status of a specific DNS request using v2 logic.
*   **`/api/v2/dns/update_status/{request_id}` (POST)**: Updates the status of a specific DNS record request using v2 logic.

**Request Body for `/create` endpoints**: A JSON object with the following fields:

-   `context` (object): Contextual information about the request.
    -   `account_id` (string): The account ID of the requester.
    -   `source` (string, optional): The source of the request (e.g., 'api', 'kafka'). Defaults to 'api'.
-   `resource` (object): The DNS resource payload.
    -   `record_type` (string): The type of DNS record.
    -   `domain` (string): The domain name.
    -   `target` (string): The target value.
    -   `comment` (string, optional): A comment.
    -   `config` (object, optional): Configuration parameters for the DNS record.
        -   `ttl` (integer, optional): Time-to-live for the DNS record (default: 300).
        -   `priority` (integer, optional): Priority for MX or SRV records.
        -   `extra_config` (object, optional): Additional configuration parameters (key-value pairs).

## Database Schema

-   `dns_requests`: Tracks request status and logs, including the `source` of the request.
-   `dns_records`: Stores successfully provisioned records.