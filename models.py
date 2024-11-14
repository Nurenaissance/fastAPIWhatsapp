from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, JSON, Date, Time
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class Contact(Base):
    __tablename__ = "contacts_contact"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    createdOn = Column(DateTime, default=datetime.utcnow, nullable=True)
    isActive = Column(Boolean, default=False, nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenant_tenant.id"), nullable=True)
    tenant = relationship("Tenant", back_populates="contacts")  # Corrected back_populates
    bg_id = Column(String(50), nullable=True)
    bg_name = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Contact(name={self.name})>"

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

    def __repr__(self):
        return f"<Tenant(id={self.id}, organization={self.organization})>"

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

class Product(Base):
    __tablename__ = "shop_products"

    id = Column(Integer, primary_key=True)
    product_id = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    link = Column(String, nullable=False)
    image_link = Column(String, unique=True, nullable=False)
    
    # Enums as String, or you can define Enum types in SQLAlchemy (optional)
    condition = Column(String(255), default="new", nullable=False)
    availability = Column(String(255), default="in_stock", nullable=False)
    
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    brand = Column(String(255), nullable=False)
    
    catalog_id = Column(BigInteger, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    
    tenant_id = Column(String(50), ForeignKey("tenant_tenant.id"), nullable=True)  # Adjusted ForeignKey reference
    
    tenant = relationship("Tenant", back_populates="products")

    def __repr__(self):
        return f"<Product(title={self.title}, product_id={self.product_id})>"

class NodeTemplate(Base):
    __tablename__ = "node_temps_nodetemplate"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    category = Column(String(100), nullable=False)
    createdBy_id = Column(Integer, ForeignKey("auth_user.id"), nullable=True)
    node_data = Column(JSON, nullable=False)
    fallback_msg = Column(Text, nullable=True)
    fallback_count = Column(Integer, nullable=True)
    tenant_id = Column(Integer, ForeignKey("tenant_tenant.id"), nullable=True)

    tenant = relationship("Tenant", back_populates="node_templates")

    def __repr__(self):
        return f"<NodeTemplate(name={self.name})>"
    
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


class ScheduledEvent(Base):
    __tablename__ = "scheduled_events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    value = Column(JSON, nullable=False)
    date = Column(Date, nullable=True)  # Stores the date of the event
    time = Column(Time, nullable=True)  # Stores the time of the event