import os
from dotenv import load_dotenv
from app.core.secrets import get_secrets_from_csm # Import CSM secrets function

# Determine the environment and load .env file
env = os.getenv("ENV", "dev")
# Adjust path to look inside the new 'env' folder
dotenv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'env', f'.env.{env}')

if os.path.exists(dotenv_file_path):
    load_dotenv(dotenv_file_path)
else:
    # Fallback to loading from root if specific env file not found
    load_dotenv()

# Fetch secrets from CSM (simulated)
csm_secrets = get_secrets_from_csm(env) # Pass the environment to the CSM function

class Settings:
    # Prioritize environment variables, then CSM secrets, then defaults
    DATABASE_URL = os.getenv("DATABASE_URL", csm_secrets.get("DATABASE_URL", "postgresql://user:password@localhost/dns_orchestrator"))
    KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", csm_secrets.get("KAFKA_BROKER_URL", "localhost:9092"))
    KAFKA_DNS_TOPIC = os.getenv("KAFKA_DNS_TOPIC", csm_secrets.get("KAFKA_DNS_TOPIC", "dns_requests"))
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", csm_secrets.get("CELERY_BROKER_URL", "redis://localhost:6379/0"))
    API_URL = os.getenv("API_URL", csm_secrets.get("API_URL", "http://app:8000/api/v1/dns/create"))
    API_KEY = os.getenv("API_KEY", csm_secrets.get("API_KEY", "default_api_key")) # Example of a new secret

settings = Settings()
