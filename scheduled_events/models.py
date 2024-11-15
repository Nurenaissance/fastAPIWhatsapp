from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, JSON, Date, Time
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime

class ScheduledEvent(Base):
    __tablename__ = "scheduled_events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    value = Column(JSON, nullable=False)
    date = Column(Date, nullable=True)  # Stores the date of the event
    time = Column(Time, nullable=True)  # Stores the time of the event