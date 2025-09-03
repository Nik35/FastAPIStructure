from app.kafka.consumer import consume_dns_requests
from app.core.logging import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Starting Kafka consumer...")
    consume_dns_requests()
