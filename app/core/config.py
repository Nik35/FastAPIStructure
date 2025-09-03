import os

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dns_orchestrator")
    KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
    KAFKA_DNS_TOPIC = os.getenv("KAFKA_DNS_TOPIC", "dns_requests")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    API_URL = os.getenv("API_URL", "http://app:8000/api/v1/dns/create")

settings = Settings()
