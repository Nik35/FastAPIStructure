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

def create_dns_request_logic_v2(
    request: DnsRequestCreate,
    db: Session = Depends(get_db)
):
    logger.info(f"V2: Received DNS request for domain {request.resource.domain}")
    return DnsRequestStatus(
        context=ResponseContext(
            request_id=uuid.uuid4(),
            partition=request.context.partition,
            service=request.context.service,
            region=request.context.region,
            account_id=request.context.account_id
        ),
        status="V2_PENDING",
        message="V2: DNS request submitted and is being processed with V2 logic."
    )

def get_dns_request_status_logic_v2(
    request_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    logger.info(f"V2: Retrieving status for request ID {request_id}")
    return DnsRequestStatus(
        context=ResponseContext(
            request_id=request_id,
            partition="default",
            service="dns_v2",
            region="us-east-1",
            account_id="123456789012"
        ),
        status="V2_COMPLETED",
        message=f"V2: DNS request status for {request_id} is completed."
    )

def update_dns_request_status_logic_v2(
    request_id: uuid.UUID,
    new_status: str,
    db: Session = Depends(get_db)
):
    logger.info(f"V2: Updating status for request ID {request_id} to {new_status}")
    return DnsRequestStatus(
        context=ResponseContext(
            request_id=request_id,
            partition="default",
            service="dns_v2",
            region="us-east-1",
            account_id="123456789012"
        ),
        status=f"V2_{new_status}",
        message=f"V2: DNS request status for {request_id} updated to: {new_status}"
    )
