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

    def __repr__(self):
        return f"<Tenant(id={self.id}, organization={self.organization})>"


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
