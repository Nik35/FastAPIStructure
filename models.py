import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base

class DnsRequest(Base):
    """
    Represents an ongoing DNS request in the database.
    The logs are stored as a JSONB column, which is perfect for dynamic data.
    """
    __tablename__ = "dns_requests"

    # Use UUID for a unique, unguessable primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_type = Column(String(10), nullable=False)
    domain = Column(String, nullable=False)
    target = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    status = Column(String(50), default="PENDING", nullable=False)
    source = Column(String(50), default="api", nullable=False)
    config = Column(JSONB, nullable=True)
    
    # JSONB is a highly efficient way to store semi-structured log data
    log_messages = Column(JSONB, default=[])

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<DnsRequest(id='{self.id}', status='{self.status}')>"

class DnsRecord(Base):
    """
    Represents a successfully provisioned DNS record.
    """
    __tablename__ = "dns_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    record_type = Column(String(10), nullable=False)
    domain = Column(String, nullable=False)
    target = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    provisioned_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DnsRecord(id='{self.id}', domain='{self.domain}')>"
