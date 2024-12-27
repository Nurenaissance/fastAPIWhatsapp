from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, JSON, Date, Time
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime



class Product(Base):
    __tablename__ = "shop_products"

    id = Column(String(255), unique=True, nullable=False, primary_key=True)
    title = Column(String(255) ,nullable=False)
    description = Column(Text, nullable=False)
    link = Column(String, nullable=False)
    image_link = Column(String ,nullable=False)
    
    condition = Column(String(255), default="new", nullable=False)
    availability = Column(String(255), default="in_stock", nullable=False)
    
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    brand = Column(String(255), nullable=False)
    
    catalog_id = Column(BigInteger, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    
    tenant_id = Column(String(50), ForeignKey("tenant_tenant.id"), nullable=True) 
    
    tenant = relationship("Tenant", back_populates="products")

    def __repr__(self):
        return f"<Product(title={self.title})>"
