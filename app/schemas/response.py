from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class ResponseContext(BaseModel):
    """
    Provides context for the response.
    """
    request_id: uuid.UUID
    partition: str
    service: str
    region: str
    account_id: str

class DnsRequestStatus(BaseModel):
    """
    The response body after a DNS request is submitted.
    """
    context: ResponseContext
    status: str
    message: str

class LogMessage(BaseModel):
    """
    Schema for a single log entry.
    """
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str
    message: str