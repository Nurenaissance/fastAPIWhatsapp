from sqlalchemy import Column, Integer, String, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from config.database import Base

class Tenant(Base):
    __tablename__ = "tenant_tenant"

    id = Column(String(50), primary_key=True)
    organization = Column(String(100), nullable=False)
    db_user = Column(String(100), nullable=False)
    db_user_password = Column(String(100), nullable=False)
    spreadsheet_link = Column(String, nullable=True)  # Use String as URL
    catalog_id = Column(BigInteger, nullable=True)

    # Corrected relationship names to match back_populates in Contact and Product models
    contacts = relationship("Contact", back_populates="tenant")
    whatsapp_chat_whatsapp_data = relationship("WhatsappTenantData", back_populates="tenant")
    products = relationship("Product", back_populates="tenant")
    node_templates = relationship("NodeTemplate", back_populates="tenant")
    dynamic_models = relationship("DynamicModel", back_populates="tenant")
    message_status = relationship("MessageStatus", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, organization={self.organization})>"
