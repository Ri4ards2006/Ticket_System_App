from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    status = Column(String(50), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
