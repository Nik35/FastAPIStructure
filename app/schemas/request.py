from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class RequestContext(BaseModel):
    """
    Provides context for the request, similar to an AWS ARN.
    """
    partition: str = Field(default="dns", description="The partition the resource is in.")
    service: str = Field(default="orchestrator", description="The service namespace.")
    region: str = Field(default="global", description="The region the resource resides in.")
    account_id: str = Field(..., description="The account ID of the requester.")
    source: str = Field(default="api", description="The source of the request (e.g., 'api', 'kafka').")

class DnsConfig(BaseModel):
    """
    Configuration parameters for the DNS record.
    """
    ttl: Optional[int] = Field(default=300, description="Time-to-live for the DNS record.")
    priority: Optional[int] = Field(None, description="Priority for MX or SRV records.")
    # Add other relevant DNS configuration parameters here
    # e.g., routing_policy: Optional[str] = "simple"
    # e.g., health_check_id: Optional[str] = None
    # Allow arbitrary extra fields for flexibility
    extra_config: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration parameters.")

class DnsResource(BaseModel):
    """
    The DNS resource payload.
    """
    record_type: str = Field(..., max_length=10)
    domain: str = Field(...)
    target: str = Field(...)
    comment: Optional[str] = None
    config: Optional[DnsConfig] = None

class DnsRequestCreate(BaseModel):
    """
    The full request body for creating a DNS record.
    """
    context: RequestContext
    resource: DnsResource
