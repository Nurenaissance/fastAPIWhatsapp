from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, JSON, Date, Time
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class WhatsappTenantData(Base):
    __tablename__ = "whatsapp_chat_whatsapptenantdata"

    business_phone_number_id = Column(BigInteger, primary_key=True)
    flow_data = Column(JSON, nullable=True)
    adj_list = Column(JSON, nullable=True)
    access_token = Column(String(300), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    business_account_id = Column(BigInteger, nullable=False)
    start = Column(Integer, nullable=True)
    fallback_count = Column(Integer, nullable=True)
    fallback_message = Column(String(1000), nullable=True)
    flow_name = Column(String(200), nullable=True)
    tenant_id = Column(String(50), ForeignKey("tenant_tenant.id"), nullable=False)
    spreadsheet_link = Column(String, nullable=True)  # Use String for URL

    tenant = relationship("Tenant", back_populates="whatsapp_chat_whatsapp_data")

    def __repr__(self):
        return f"<WhatsappTenantData(business_phone_number_id={self.business_phone_number_id})>"

class MessageStatus(Base):
    __tablename__ = "whatsapp_message_id"

    business_phone_number_id = Column(BigInteger, nullable=False, index=True)  # Index added
    sent = Column(Boolean, default=False, nullable=False)                       # Default value set
    delivered = Column(Boolean, default=False, nullable=False)                  # Default value set
    read = Column(Boolean, default=False, nullable=False)                       # Default value set
    user_phone_number = Column(BigInteger, nullable=False, index=True)          # Index added
    message_id = Column(String(300), primary_key=True)                          # Primary key retained
    broadcast_group = Column(String(50), nullable=True)
    broadcast_group_name = Column(String(100), nullable=True)
    replied = Column(Boolean, default=False, nullable=False)                    # Default value set
    failed = Column(Boolean, default=False, nullable=False)                     # Default value set

    def __repr__(self):
        return f"<MessageStatus(message_id={self.message_id}, user_phone_number={self.user_phone_number})>"

