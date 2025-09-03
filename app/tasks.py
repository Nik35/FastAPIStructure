from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from models import DnsRequest, DnsRecord
from app.schemas.response import LogMessage
from app.core.logging import get_logger
import time

logger = get_logger(__name__)

@celery_app.task(queue='dns_tasks')
def provision_dns_record(request_id: str):
    db = SessionLocal()
    db_request = db.query(DnsRequest).filter(DnsRequest.id == request_id).first()

    if db_request:
        try:
            logger.info(f"[Celery Task] Processing DNS request: {request_id}")
            if db_request.config:
                logger.info(f"[Celery Task] DNS config for request {request_id}: {db_request.config}")

            # Simulate running an Ansible playbook
            logger.info(f"[Celery Task] Triggering Ansible job for request: {request_id}")
            time.sleep(10)  # Simulate long-running Ansible job
            logger.info(f"[Celery Task] Ansible job completed for request: {request_id}")

            db_request.status = "COMPLETED"
            db_request.log_messages = db_request.log_messages + [LogMessage(status="SUCCESS", message="DNS record provisioned successfully by Ansible.").model_dump()]
            db.add(db_request)

            db_record = DnsRecord(
                request_id=db_request.id,
                record_type=db_request.record_type,
                domain=db_request.domain,
                target=db_request.target,
                comment=db_request.comment
            )
            db.add(db_record)
            db.commit()
            logger.info(f"[Celery Task] Successfully processed DNS request: {request_id}")

        except Exception as e:
            db.rollback()
            db_request.status = "FAILED"
            db_request.log_messages = db_request.log_messages + [LogMessage(status="ERROR", message=str(e)).model_dump()]
            db.add(db_request)
            db.commit()
            logger.error(f"[Celery Task] Failed to process DNS request: {request_id}, error: {e}")
        finally:
            db.close()
