from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, JSON, Date, Time
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class DynamicModel(Base):
    __tablename__ = "dynamic_entities_dynamicmodel"

    model_name = Column(String(255))
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenant_tenant.id"), nullable=True)
    tenant = relationship("Tenant", back_populates="dynamic_models")


class DynamicField(Base):
    __tablename__ = "dynamic_entities_dynamicfield"

    id = Column(Integer, primary_key=True)
    field_name = Column(String(255))
    field_type = Column(String(50))
    dynamic_model_id = Column(Integer, ForeignKey("tenant_tenant.id"), nullable=True)
    # dynamic_model = relationship("DynamicModel", back_populates="")