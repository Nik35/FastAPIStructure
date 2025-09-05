from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.request import DnsRequestCreate
from app.schemas.response import DnsRequestStatus
import uuid
from app.api.v1.endpoints.dns import (
	create_dns_request_logic,
	get_dns_request_status_logic,
	update_dns_request_status_logic
)

router = APIRouter()

@router.post("/create", response_model=DnsRequestStatus, summary="Create a new DNS record request")
def create_dns_request(
	request: DnsRequestCreate,
	db: Session = Depends(get_db)
):
	return create_dns_request_logic(request=request, db=db)

@router.get("/{request_id}", response_model=DnsRequestStatus, summary="Get DNS request status by ID")
def get_dns_request_status(
	request_id: uuid.UUID,
	db: Session = Depends(get_db)
):
	return get_dns_request_status_logic(request_id=request_id, db=db)

@router.post("/update_status/{request_id}", response_model=DnsRequestStatus, summary="Update DNS request status")
def update_dns_request_status(
	request_id: uuid.UUID,
	new_status: str,
	db: Session = Depends(get_db)
):
	return update_dns_request_status_logic(request_id=request_id, new_status=new_status, db=db)