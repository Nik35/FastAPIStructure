from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from models import DnsRequest
from app.schemas.request import DnsRequestCreate
from app.schemas.response import DnsRequestStatus, ResponseContext, LogMessage
from app.core.logging import get_logger
from app.tasks import provision_dns_record

logger = get_logger(__name__)

router = APIRouter()

@router.post("/create", response_model=DnsRequestStatus, summary="Create a new DNS record request")
def create_dns_request(
    request: DnsRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submits a new DNS record request. The process is handled asynchronously
    by a Celery task.
    """
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
        raise HTTPException(status_code=500, detail=str(e))

