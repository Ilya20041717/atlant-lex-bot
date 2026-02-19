from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization")
    clients = relationship("Client", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, index=True, nullable=False)
    role = Column(String(32), nullable=False, default="unknown")
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization", back_populates="users")
    lead_profile = relationship("LeadProfile", back_populates="user", uselist=False)
    client = relationship("Client", back_populates="user", uselist=False)


class LeadProfile(Base):
    __tablename__ = "lead_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    debt_amount = Column(Numeric(12, 2))
    creditors_count = Column(Integer)
    overdue_months = Column(Integer)
    income = Column(Numeric(12, 2))
    assets = Column(Text)
    region = Column(String(120))
    contact_name = Column(String(255))
    contact_phone = Column(String(32))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="lead_profile")


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True)
    code = Column(String(64), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    client_actions = Column(Text, nullable=False)
    eta_text = Column(String(120), nullable=False)

    clients = relationship("Client", back_populates="stage")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    contract_number = Column(String(64), nullable=True)
    current_stage_id = Column(Integer, ForeignKey("stages.id"))
    next_step = Column(Text)
    total_cost = Column(Numeric(12, 2))
    paid_amount = Column(Numeric(12, 2))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="client")
    organization = relationship("Organization", back_populates="clients")
    stage = relationship("Stage", back_populates="clients")
    documents = relationship("ClientDocument", back_populates="client")
    tasks = relationship("ClientTask", back_populates="client")
    payments = relationship("ClientPayment", back_populates="client")
    notifications = relationship("Notification", back_populates="client")


class ClientTask(Base):
    __tablename__ = "client_tasks"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    due_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="tasks")


class ClientDocument(Base):
    __tablename__ = "client_documents"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="not_provided")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", back_populates="documents")


class ClientPayment(Base):
    __tablename__ = "client_payments"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    paid_at = Column(Date)
    status = Column(String(32), nullable=False, default="planned")

    client = relationship("Client", back_populates="payments")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    type = Column(String(32), nullable=False)
    text = Column(Text, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    status = Column(String(32), nullable=False, default="planned")

    client = relationship("Client", back_populates="notifications")
