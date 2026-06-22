"""
LabhArth AI — Database Models (SQLAlchemy ORM)
================================================
SQLAlchemy models mapping to PostgreSQL tables.
Uses async-compatible declarative base.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Scheme(Base):
    """Government welfare scheme."""

    __tablename__ = "schemes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    ministry = Column(String(255))
    category = Column(String(100))
    level = Column(String(50))
    state = Column(String(100))
    eligibility_criteria = Column(JSONB)
    benefits = Column(Text)
    required_documents = Column(JSONB)
    application_process = Column(Text)
    official_url = Column(String(1000))
    status = Column(String(50), default="active")
    launched_date = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    eligibility_checks = relationship("EligibilityCheck", back_populates="scheme")

    def __repr__(self) -> str:
        return f"<Scheme(id={self.id}, name='{self.name}')>"


class UserProfile(Base):
    """Citizen profile for eligibility matching."""

    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(255), unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    state = Column(String(100))
    district = Column(String(100))
    category = Column(String(50))
    income_annual = Column(Float)
    occupation = Column(String(100))
    education = Column(String(100))
    is_bpl = Column(Boolean, default=False)
    is_disabled = Column(Boolean, default=False)
    is_farmer = Column(Boolean, default=False)
    is_student = Column(Boolean, default=False)
    additional_info = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, session='{self.session_id}')>"


class ChatSession(Base):
    """Chat message in a conversation."""

    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    agent_name = Column(String(100))
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, role='{self.role}')>"


class EligibilityCheck(Base):
    """Record of an eligibility check."""

    __tablename__ = "eligibility_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(String(255), nullable=False)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"))
    is_eligible = Column(Boolean)
    confidence = Column(Float)
    reasoning = Column(Text)
    missing_criteria = Column(JSONB)
    checked_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scheme = relationship("Scheme", back_populates="eligibility_checks")

    def __repr__(self) -> str:
        return f"<EligibilityCheck(id={self.id}, eligible={self.is_eligible})>"
