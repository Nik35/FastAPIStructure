from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import DnsRequest
from app.schemas.request import DnsRequestCreate
from app.schemas.response import DnsRequestStatus, ResponseContext, LogMessage
from app.core.logging import get_logger
from app.celery.tasks import provision_dns_record
import uuid

logger = get_logger(__name__)

def create_dns_request_logic(
    request: DnsRequestCreate,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received DNS request for domain {request.resource.domain} from source {request.context.source}")
        db_request = DnsRequest(
            record_type=request.resource.record_type,
            domain=request.resource.domain,
            target=request.resource.target,
            comment=request.resource.comment,
            status="PENDING",
            source=request.context.source,
            config=request.resource.config.model_dump() if request.resource.config else None,
            log_messages=[LogMessage(status="INFO", message="Received new DNS request.").model_dump()]
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        provision_dns_record.apply_async(args=[str(db_request.id)], queue='dns_tasks')

        logger.info(f"DNS request {db_request.id} submitted to Celery")

        return DnsRequestStatus(
            context=ResponseContext(
                request_id=db_request.id,
                partition=request.context.partition,
                service=request.context.service,
                region=request.context.region,
                account_id=request.context.account_id
            ),
            status="PENDING",
            message="DNS request submitted and is being processed."
        )
    except Exception as e:
        logger.error(f"Error creating DNS request: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_dns_request_status_logic(
    request_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    db_request = db.query(DnsRequest).filter(DnsRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DNS Request not found")

    return DnsRequestStatus(
        context=ResponseContext(
            request_id=db_request.id,
            partition="default",
            service="dns",
            region="us-east-1",
            account_id="123456789012"
        ),
        status=db_request.status,
        message=f"DNS request status: {db_request.status}"
    )

def update_dns_request_status_logic(
    request_id: uuid.UUID,
    new_status: str,
    db: Session = Depends(get_db)
):
    db_request = db.query(DnsRequest).filter(DnsRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DNS Request not found")

    db_request.status = new_status
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return DnsRequestStatus(
        context=ResponseContext(
            request_id=db_request.id,
            partition="default",
            service="dns",
            region="us-east-1",
            account_id="123456789012"
        ),
        status=db_request.status,
        message=f"DNS request status updated to: {db_request.status}"
    )
