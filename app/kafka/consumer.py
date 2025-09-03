from kafka import KafkaConsumer
from app.core.config import settings
from app.core.logging import get_logger
import json
import requests

logger = get_logger(__name__)

def consume_dns_requests():
    consumer = KafkaConsumer(
        settings.KAFKA_DNS_TOPIC,
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest'
    )

    for message in consumer:
        payload = message.value
        logger.info(f"Received message from Kafka: {payload}")

        # Construct the API request payload
        api_payload = {
            "context": {
                "account_id": payload.get("account_id", "default_account"),
                "source": "kafka"
            },
            "resource": {
                "record_type": payload.get("record_type"),
                "domain": payload.get("domain"),
                "target": payload.get("target"),
                "comment": payload.get("comment"),
                "config": payload.get("config") # Include config from Kafka payload.
            }
        }

        try:
            # Call the API endpoint
            response = requests.post(settings.API_URL, json=api_payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            logger.info(f"Successfully called API for request: {api_payload}")
            logger.info(f"API response: {response.json()}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling API for request {api_payload}: {e}")
