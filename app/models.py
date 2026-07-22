from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
from sqlalchemy import Column, String, Integer, DateTime, JSON, Index, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Crear Base para ORM
Base = declarative_base()


class Audit(Base):
    __tablename__ = "audits"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    domain = Column(String(255), nullable=False)
    score_overall = Column(Integer, nullable=True)
    results = Column(JSON, nullable=False)
    screenshot_url = Column(String(500), nullable=True)
    customer_email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('idx_domain', 'domain'),
        Index('idx_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Audit(id={self.id}, domain={self.domain}, score={self.score_overall})>"


class UserError(Base):
    __tablename__ = "user_errors"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    domain = Column(String(255), nullable=True)
    error_type = Column(String(50), nullable=False, index=True)
    error_message = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<UserError(id={self.id}, type={self.error_type})>"


class AuditRequest(BaseModel):
    domain: str = Field(..., min_length=3, max_length=255)

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, v: str) -> str:
        v = v.replace("https://", "").replace("http://", "")
        return v.rstrip("/")


class SendEmailRequest(BaseModel):
    """Request para enviar email de auditoría."""
    email: str = Field(..., min_length=5, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validación básica de email."""
        if "@" not in v or "." not in v:
            raise ValueError("Email inválido")
        return v.lower()


class AuditResponse(BaseModel):
    audit_id: str
    domain: str
    score_overall: int = Field(..., ge=0, le=100)
    indicators: Dict[str, Any]
    screenshot_url: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    error: str