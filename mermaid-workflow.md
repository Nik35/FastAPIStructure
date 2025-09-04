# DNS Orchestrator Workflow Diagrams

This document provides comprehensive workflow diagrams for the DNS Request Orchestrator project using Mermaid syntax. These diagrams illustrate the various components, data flows, and processes within the system.

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [API Request Flow](#api-request-flow)
3. [Kafka Message Flow](#kafka-message-flow)
4. [Celery Task Processing](#celery-task-processing)
5. [Database Interactions](#database-interactions)
6. [CI/CD Workflow](#cicd-workflow)
7. [Container Orchestration](#container-orchestration)

---

## System Architecture Overview

This diagram shows the high-level architecture of the DNS orchestration service and how all components interact with each other.

```mermaid
graph TB
    subgraph "External Sources"
        CLIENT[HTTP Client]
        KAFKA_PRODUCER[Kafka Producer]
    end

    subgraph "Load Balancer/Gateway"
        LB[Load Balancer]
    end

    subgraph "Application Layer"
        API[FastAPI Application<br/>:8000]
        CONSUMER[Kafka Consumer]
        WORKER[Celery Worker]
    end

    subgraph "Message Queue"
        KAFKA[Apache Kafka<br/>Topic: dns_requests]
        REDIS[Redis<br/>Celery Broker]
    end

    subgraph "Database Layer"
        POSTGRES[(PostgreSQL<br/>Database)]
    end

    subgraph "External Services"
        ANSIBLE[Ansible<br/>DNS Provisioning<br/>(Simulated)]
    end

    %% External connections
    CLIENT --> LB
    KAFKA_PRODUCER --> KAFKA
    
    %% Load balancer to API
    LB --> API
    
    %% API interactions
    API --> POSTGRES
    API --> REDIS
    
    %% Kafka flow
    KAFKA --> CONSUMER
    CONSUMER --> API
    
    %% Celery flow
    REDIS --> WORKER
    WORKER --> POSTGRES
    WORKER --> ANSIBLE
    
    %% Styling
    classDef external fill:#e1f5fe
    classDef application fill:#f3e5f5
    classDef database fill:#e8f5e8
    classDef queue fill:#fff3e0
    
    class CLIENT,KAFKA_PRODUCER,ANSIBLE external
    class API,CONSUMER,WORKER application
    class POSTGRES database
    class KAFKA,REDIS queue
```

---

## API Request Flow

This diagram illustrates the complete flow when a DNS request is made through the HTTP API.

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant PostgreSQL
    participant Redis
    participant CeleryWorker
    participant Ansible

    Client->>+FastAPI: POST /api/v1/dns/create
    Note over Client,FastAPI: Request payload with context & resource
    
    FastAPI->>FastAPI: Validate request schema
    FastAPI->>+PostgreSQL: Create DNS request record
    PostgreSQL-->>-FastAPI: Return request ID
    
    FastAPI->>FastAPI: Set status to PENDING
    FastAPI->>+Redis: Queue Celery task
    Redis-->>-FastAPI: Task queued
    
    FastAPI-->>-Client: Return response with request_id & status
    
    Redis->>+CeleryWorker: Trigger provision_dns_record task
    CeleryWorker->>+PostgreSQL: Fetch request details
    PostgreSQL-->>-CeleryWorker: Return request data
    
    CeleryWorker->>+Ansible: Execute DNS provisioning
    Note over CeleryWorker,Ansible: Simulate 10s Ansible playbook
    Ansible-->>-CeleryWorker: Provisioning complete
    
    CeleryWorker->>+PostgreSQL: Update request status to COMPLETED
    CeleryWorker->>PostgreSQL: Create DNS record entry
    CeleryWorker->>PostgreSQL: Add success log message
    PostgreSQL-->>-CeleryWorker: Confirm updates
    
    Note over Client: Client can query status separately
```

---

## Kafka Message Flow

This diagram shows how DNS requests are processed when they arrive via Kafka messages.

```mermaid
sequenceDiagram
    participant Producer as Kafka Producer
    participant Kafka as Kafka Topic<br/>(dns_requests)
    participant Consumer as Kafka Consumer
    participant FastAPI
    participant PostgreSQL
    participant Redis
    participant CeleryWorker

    Producer->>+Kafka: Publish DNS request message
    Kafka-->>-Producer: Message acknowledged
    
    loop Message Processing
        Consumer->>+Kafka: Poll for messages
        Kafka-->>-Consumer: Return DNS request payload
        
        Consumer->>Consumer: Transform to API format
        Note over Consumer: Add source: "kafka" to context
        
        Consumer->>+FastAPI: POST /api/v1/dns/create
        FastAPI->>FastAPI: Validate request
        FastAPI->>+PostgreSQL: Create DNS request (source=kafka)
        PostgreSQL-->>-FastAPI: Return request ID
        
        FastAPI->>+Redis: Queue Celery task
        Redis-->>-FastAPI: Task queued
        FastAPI-->>-Consumer: Return success response
        
        Consumer->>Consumer: Log successful API call
    end
    
    Note over Redis,CeleryWorker: Same async processing as API flow
    Redis->>CeleryWorker: Process DNS provisioning task
```

---

## Celery Task Processing

This flowchart details the asynchronous task processing workflow for DNS provisioning.

```mermaid
flowchart TD
    START([Task Triggered]) --> FETCH[Fetch DNS Request<br/>from Database]
    
    FETCH --> CHECK{Request<br/>Exists?}
    CHECK -->|No| ERROR_NOT_FOUND[Log Error:<br/>Request Not Found]
    CHECK -->|Yes| LOG_START[Log: Processing Started]
    
    LOG_START --> CONFIG_CHECK{Has<br/>Config?}
    CONFIG_CHECK -->|Yes| LOG_CONFIG[Log DNS Config Details]
    CONFIG_CHECK -->|No| ANSIBLE_START
    LOG_CONFIG --> ANSIBLE_START
    
    ANSIBLE_START[Trigger Ansible Job] --> SIMULATE[Simulate 10s<br/>Ansible Execution]
    
    SIMULATE --> ANSIBLE_CHECK{Ansible<br/>Success?}
    
    ANSIBLE_CHECK -->|Success| UPDATE_SUCCESS[Update Status: COMPLETED]
    ANSIBLE_CHECK -->|Failure| UPDATE_FAILURE[Update Status: FAILED]
    
    UPDATE_SUCCESS --> LOG_SUCCESS[Add Success Log Message]
    UPDATE_FAILURE --> LOG_ERROR[Add Error Log Message]
    
    LOG_SUCCESS --> CREATE_RECORD[Create DNS Record Entry]
    LOG_ERROR --> COMMIT_FAILURE
    
    CREATE_RECORD --> COMMIT_SUCCESS[Commit Transaction]
    COMMIT_FAILURE[Commit Transaction] --> END_FAILURE
    COMMIT_SUCCESS --> END_SUCCESS[Task Complete - Success]
    
    ERROR_NOT_FOUND --> END_ERROR[Task Complete - Error]
    END_FAILURE[Task Complete - Failure]
    
    %% Styling
    classDef startEnd fill:#e8f5e8
    classDef process fill:#e3f2fd
    classDef decision fill:#fff3e0
    classDef error fill:#ffebee
    classDef success fill:#e8f5e8
    
    class START,END_SUCCESS,END_FAILURE,END_ERROR startEnd
    class FETCH,LOG_START,LOG_CONFIG,ANSIBLE_START,SIMULATE,UPDATE_SUCCESS,UPDATE_FAILURE,LOG_SUCCESS,LOG_ERROR,CREATE_RECORD,COMMIT_SUCCESS,COMMIT_FAILURE process
    class CHECK,CONFIG_CHECK,ANSIBLE_CHECK decision
    class ERROR_NOT_FOUND error
```

---

## Database Interactions

This diagram shows the database schema and relationships between tables.

```mermaid
erDiagram
    DNS_REQUESTS {
        UUID id PK
        string record_type
        string domain
        string target
        string comment
        string status
        string source
        jsonb config
        jsonb log_messages
        timestamp created_at
        timestamp updated_at
    }
    
    DNS_RECORDS {
        UUID id PK
        UUID request_id UK
        string record_type
        string domain
        string target
        string comment
        timestamp provisioned_at
    }
    
    DNS_REQUESTS ||--o| DNS_RECORDS : "creates"
```

### Database Operation Flow

```mermaid
flowchart LR
    subgraph "Request Creation"
        A1[API/Kafka Input] --> A2[Validate Schema]
        A2 --> A3[Insert DNS_REQUESTS<br/>Status: PENDING]
    end
    
    subgraph "Task Processing"
        B1[Celery Task] --> B2[Query DNS_REQUESTS]
        B2 --> B3[Update Status & Logs]
        B3 --> B4[Insert DNS_RECORDS<br/>on Success]
    end
    
    A3 --> B1
    
    classDef input fill:#e3f2fd
    classDef process fill:#f3e5f5
    classDef output fill:#e8f5e8
    
    class A1 input
    class A2,A3,B1,B2,B3 process
    class B4 output
```

---

## CI/CD Workflow

This diagram shows the GitHub Actions workflow for building and deploying the application.

```mermaid
flowchart TD
    PUSH[Push to develop branch] --> TRIGGER[Trigger GitHub Actions]
    PR[Pull Request to develop] --> TRIGGER
    
    TRIGGER --> CHECKOUT[Checkout Repository]
    CHECKOUT --> LOGIN[Login to Container Registry<br/>ghcr.io]
    
    LOGIN --> METADATA[Extract Metadata<br/>Tags & Labels]
    METADATA --> BUILD[Build Docker Image]
    
    BUILD --> TEST{Tests Pass?}
    TEST -->|No| FAIL[❌ Build Failed]
    TEST -->|Yes| PUSH_IMAGE[Push to ghcr.io]
    
    PUSH_IMAGE --> TAG[Tag as latest/version]
    TAG --> DEPLOY[🚀 Ready for Deployment]
    
    classDef trigger fill:#e3f2fd
    classDef process fill:#f3e5f5
    classDef success fill:#e8f5e8
    classDef failure fill:#ffebee
    
    class PUSH,PR trigger
    class CHECKOUT,LOGIN,METADATA,BUILD,PUSH_IMAGE,TAG process
    class DEPLOY success
    class FAIL failure
```

---

## Container Orchestration

This diagram shows how Docker Compose orchestrates all the services.

```mermaid
graph TB
    subgraph "Docker Compose Services"
        subgraph "Database Services"
            POSTGRES_C[postgres:13<br/>Port: 5432]
            REDIS_C[redis:6.2-alpine<br/>Port: 6379]
        end
        
        subgraph "Message Queue Services"
            ZOOKEEPER_C[cp-zookeeper:7.0.1<br/>Port: 2181]
            KAFKA_C[cp-kafka:7.0.1<br/>Port: 9092]
        end
        
        subgraph "Application Services"
            APP_C[FastAPI App<br/>Port: 8000<br/>Command: uvicorn]
            CONSUMER_C[Kafka Consumer<br/>Command: python run_consumer.py]
            WORKER_C[Celery Worker<br/>Command: celery worker]
        end
    end
    
    subgraph "Dependencies"
        ZOOKEEPER_C --> KAFKA_C
        POSTGRES_C --> APP_C
        POSTGRES_C --> CONSUMER_C
        POSTGRES_C --> WORKER_C
        REDIS_C --> APP_C
        REDIS_C --> WORKER_C
        KAFKA_C --> APP_C
        KAFKA_C --> CONSUMER_C
    end
    
    subgraph "Environment Configuration"
        ENV[Environment Files<br/>.env.dev / .env.uta / .env.prod]
        ENV --> APP_C
        ENV --> CONSUMER_C
        ENV --> WORKER_C
    end
    
    subgraph "Initialization"
        ENTRYPOINT[entrypoint.sh<br/>- Wait for DB<br/>- Init Alembic<br/>- Run Migrations<br/>- Start Service]
        ENTRYPOINT --> APP_C
        ENTRYPOINT --> CONSUMER_C
        ENTRYPOINT --> WORKER_C
    end
    
    classDef database fill:#e8f5e8
    classDef queue fill:#fff3e0
    classDef application fill:#f3e5f5
    classDef config fill:#e1f5fe
    
    class POSTGRES_C,REDIS_C database
    class ZOOKEEPER_C,KAFKA_C queue
    class APP_C,CONSUMER_C,WORKER_C application
    class ENV,ENTRYPOINT config
```

---

## Data Flow Summary

This high-level diagram summarizes the complete data flow through the system.

```mermaid
flowchart LR
    subgraph "Input Sources"
        HTTP[HTTP API Clients]
        KAFKA_IN[Kafka Messages]
    end
    
    subgraph "Processing Layer"
        API[FastAPI<br/>DNS Endpoints]
        TASKS[Celery Tasks<br/>Async Processing]
    end
    
    subgraph "Storage Layer"
        DB[(PostgreSQL<br/>DNS Requests & Records)]
        QUEUE[Redis<br/>Task Queue]
    end
    
    subgraph "External Integration"
        ANSIBLE[Ansible Playbooks<br/>DNS Provisioning]
    end
    
    HTTP --> API
    KAFKA_IN --> API
    API --> DB
    API --> QUEUE
    QUEUE --> TASKS
    TASKS --> DB
    TASKS --> ANSIBLE
    
    classDef input fill:#e3f2fd
    classDef process fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef external fill:#fff3e0
    
    class HTTP,KAFKA_IN input
    class API,TASKS process
    class DB,QUEUE storage
    class ANSIBLE external
```

---

## Notes

- All diagrams use Mermaid syntax and can be rendered in GitHub, GitLab, or any Mermaid-compatible viewer
- The system supports multiple environment configurations (dev, uta, prod)
- Database migrations are handled automatically via Alembic during container startup
- Celery tasks are queued with a specific queue name: `dns_tasks`
- The Kafka consumer transforms messages to match the API schema before forwarding
- All services include structured JSON logging for observability
- The system is designed to be horizontally scalable with multiple worker instances
