from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class Conversation(Base):
    __tablename__ = "interaction_conversation"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(String(255), nullable=False)
    message_text = Column(Text, nullable=True)
    encrypted_message_text = Column(LargeBinary, nullable=True)
    sender = Column(String(50), nullable=False)
    source = Column(String(255), nullable=False)
    date_time = Column(DateTime, nullable=True)
    business_phone_number_id = Column(String(255), nullable=True)
    mapped = Column(Boolean, default=False)
    tenant_id = Column(String(50), ForeignKey("tenant_tenant.id"), nullable=True)

    tenant = relationship("Tenant", back_populates="conversations")
