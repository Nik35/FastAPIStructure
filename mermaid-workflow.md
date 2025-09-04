# Workflow Diagrams

This document contains the workflow diagrams for the project.

## Updated Workflow Diagram
```mermaid
flowchart TD
    A[Kafka Message Received] --> B[API Adapter Processes Request]
    B --> C[Call Actual API]
    C --> D[Trigger Celery Task]
    D --> E[Process Completed]
```

## Sequence Diagram
```mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Send Kafka Message
    System->>API Adapter: Process Message
    API Adapter->>Actual API: Make API Call
    Actual API-->>API Adapter: Response
    API Adapter->>Celery: Trigger Task
    Celery-->>System: Task Completed
```
