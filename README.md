# DNS Request Orchestrator (PostgreSQL + Kafka + Celery + Ansible Backend)

This project provides a robust and scalable backend API for a DNS request orchestration service, built with FastAPI and PostgreSQL. It uses Kafka for receiving payloads, Celery for asynchronous task processing, and simulates Ansible for job execution.

## Project Structure

- `app/main.py`: The core FastAPI application that defines the API router.
- `app/core/config.py`: Centralized configuration management.
- `app/core/database.py`: Handles PostgreSQL database connection, session management, and table creation using SQLAlchemy.
- `app/core/celery_app.py`: Configures the Celery application, defining the broker and task includes.
- `app/core/logging.py`: Sets up structured JSON logging for the entire application.
- `app/kafka/consumer.py`: Contains the Kafka consumer logic that listens to a Kafka topic, processes messages, and calls the FastAPI endpoint.
- `app/schemas/request.py`: Contains Pydantic models for request validation.
- `app/schemas/response.py`: Contains Pydantic models for response serialization.
- `app/api/v1/endpoints/dns.py`: Defines the `/v1/dns` API endpoints.
- `app/tasks.py`: Defines Celery tasks, including the Ansible job simulation.
- `app/models/models.py`: Defines the SQLAlchemy ORM models (moved from schemas/models.py).
- `requirements.txt`: Lists all Python dependencies.
- `scripts/run_consumer.py`: Script to start the Kafka consumer (moved from root).
# Database Migrations (Alembic)

Alembic is used for handling database migrations. Basic commands:

1. **Initialize Alembic**
    ```bash
    alembic init migrations
    ```
2. **Configure Alembic**
    - Edit `migrations/env.py` to set your SQLAlchemy `Base` and database URL.
    - Example:
      ```python
      from app.core.database import Base
      target_metadata = Base.metadata
      ```
3. **Create a Migration**
    ```bash
    alembic revision --autogenerate -m "Initial migration"
    ```
4. **Apply Migrations**
    ```bash
    alembic upgrade head
    ```

See `ALEMBIC_SETUP.md` for more details.

## Development Setup


### Running with Docker Compose (Recommended)

This is the recommended way to run the application for development. It will start the FastAPI application, PostgreSQL, Kafka, Redis, and the Celery worker with a single command.

**Automatic Database Migrations:**

The Docker setup now automatically initializes Alembic (if not already present) and applies all database migrations before starting the app, worker, or consumer. This is handled by the `entrypoint.sh` script, so you do not need to run Alembic commands manually.


**Steps:**

1.  **Install Docker and Docker Compose**

    Ensure you have Docker and Docker Compose installed on your system.

2.  **Run Docker Compose with Environment Selection**

    By default, the app uses `.env.dev`. To use a different environment (e.g., UTA or prod), set the ENV variable:

    **Windows PowerShell:**
    ```powershell
    $env:ENV="uta"; docker-compose up --build
    $env:ENV="prod"; docker-compose up --build
    ```

    **Linux/macOS Bash:**
    ```bash
    ENV=uta docker-compose up --build
    ENV=prod docker-compose up --build
    ```

    The API will be available at `http://127.0.0.1:8000`.

---

**Note:**

- The `entrypoint.sh` script will:
    - Wait for the database to be ready
    - Initialize Alembic migrations if the `migrations/` folder does not exist
    - Always run `alembic upgrade head` to apply migrations
    - Start the main service (app, worker, or consumer)

You can find and customize this logic in `entrypoint.sh`.

### Running Individual Components with Docker

If you want to run each component as a separate Docker container, you can follow these steps:

1.  **Create a Docker Network**

    ```bash
    docker network create my-network
    ```

2.  **Run PostgreSQL**

    ```bash
    docker run -d --name postgres --network my-network -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dns_orchestrator -p 5432:5432 postgres
    ```

3.  **Run Redis**

    ```bash
    docker run -d --name redis --network my-network -p 6379:6379 redis:6.2-alpine
    ```

4.  **Run Kafka and Zookeeper**

    ```bash
    docker run -d --name zookeeper --network my-network -p 2181:2181 confluentinc/cp-zookeeper
    docker run -d --name kafka --network my-network -p 9092:9092 -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092 -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT -e KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 confluentinc/cp-kafka
    ```

5.  **Build the Application Image**

    ```bash
    docker build -t fastapi-app .
    ```

6.  **Run the FastAPI Application**

    ```bash
    docker run -d --name app --network my-network -p 8000:8000 -e DATABASE_URL="postgresql://user:password@postgres/dns_orchestrator" -e KAFKA_BROKER_URL="kafka:29092" -e CELERY_BROKER_URL="redis://redis:6379/0" fastapi-app
    ```

7.  **Run the Kafka Consumer**

    ```bash
    docker run -d --name consumer --network my-network -e DATABASE_URL="postgresql://user:password@postgres/dns_orchestrator" -e KAFKA_BROKER_URL="kafka:29092" fastapi-app python run_consumer.py
    ```

8.  **Run the Celery Worker**

    ```bash
    docker run -d --name worker --network my-network -e DATABASE_URL="postgresql://user:password@postgres/dns_orchestrator" -e CELERY_BROKER_URL="redis://redis:6379/0" fastapi-app celery -A app.tasks worker --loglevel=info -Q dns_tasks
    ```

### Manual Setup


If you prefer to run the services manually, you can follow these steps:

#### 1. Install PostgreSQL, Redis, and Kafka

Ensure you have PostgreSQL, Redis, and Kafka instances running. Docker is a great way to get started.

```bash
# PostgreSQL container
docker run --name my-postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dns_orchestrator -p 5432:5432 -d postgres

# Redis container
docker run --name my-redis -p 6379:6379 -d redis:6.2-alpine

# Kafka and Zookeeper containers
docker run -p 2181:2181 -d --name zookeeper confluentinc/cp-zookeeper
docker run -p 9092:9092 -d --name kafka -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 --link zookeeper confluentinc/cp-kafka
```

#### 2. Install Dependencies

It is highly recommended to use a Python virtual environment.

```bash
pip install -r requirements.txt
```


#### 3. Set Environment Variables (Recommended: .env files)

This project supports environment-specific configuration using `.env` files. Three example files are provided:

- `.env.dev` — for development
- `.env.uta` — for User Testing Acceptance
- `.env.prod` — for production

Copy the appropriate file to `.env` before running the application. For example:

```bash
cp .env.dev .env
```

The application will automatically load environment variables from `.env` using `python-dotenv`.

If you prefer, you can still set environment variables manually as shown below:

```bash
export DATABASE_URL="postgresql://user:password@localhost/dns_orchestrator"
export KAFKA_BROKER_URL="localhost:9092"
export KAFKA_DNS_TOPIC="dns_requests"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export API_URL="http://localhost:8000/api/v1/dns/create"
```

#### 4. Run the Backend Server


Start the FastAPI server using uvicorn, specifying the environment (dev, uta, prod):

**Windows PowerShell:**
```powershell
$env:ENV="dev"; uvicorn app.main:app --reload
$env:ENV="uta"; uvicorn app.main:app --reload
$env:ENV="prod"; uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Linux/macOS Bash:**
```bash
ENV=dev uvicorn app.main:app --reload
ENV=uta uvicorn app.main:app --reload
ENV=prod uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

#### 5. Run the Kafka Consumer

In a separate terminal, start the Kafka consumer to process the tasks.

```bash
python run_consumer.py
```

#### 6. Run the Celery Worker

In a separate terminal, start the Celery worker to process the tasks.

```bash
celery -A app.tasks worker --loglevel=info -Q dns_tasks
```

## API Endpoint

The API provides the following endpoint:

- **POST `/api/v1/dns/create`**: Submits a new DNS record request.

**Request Body**: A JSON object with the following fields:

- `context` (object): Contextual information about the request.
  - `account_id` (string): The account ID of the requester.
  - `source` (string, optional): The source of the request (e.g., 'api', 'kafka'). Defaults to 'api'.
- `resource` (object): The DNS resource payload.
  - `record_type` (string): The type of DNS record.
  - `domain` (string): The domain name.
  - `target` (string): The target value.
  - `comment` (string, optional): A comment.
  - `config` (object, optional): Configuration parameters for the DNS record.
    - `ttl` (integer, optional): Time-to-live for the DNS record (default: 300).
    - `priority` (integer, optional): Priority for MX or SRV records.
    - `extra_config` (object, optional): Additional configuration parameters (key-value pairs).

## Database Schema

- `dns_requests`: Tracks request status and logs, including the `source` of the request.
- `dns_records`: Stores successfully provisioned records.
