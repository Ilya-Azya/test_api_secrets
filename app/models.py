from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Secret(Base):
    __tablename__ = "secrets"

    id = Column(String, primary_key=True, default=generate_uuid)
    secret_data = Column(Text, nullable=False)
    passphrase_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class SecretLog(Base):
    __tablename__ = "secret_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    secret_id = Column(String)
    action = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
