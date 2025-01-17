from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from config.database import Base

class Retailer(Base):
    __tablename__ = 'orders_retailer'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    tenant_id = Column(String(50), ForeignKey("tenant_tenant.id"), nullable=True)

    tenant = relationship("Tenant", back_populates="retailer")
