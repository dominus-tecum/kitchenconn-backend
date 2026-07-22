from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    items = Column(JSON)
    item_names = Column(JSON)
    waiter = Column(String)
    timestamp = Column(String)
    status = Column(String, default="pending")
    confirmed_at = Column(String, nullable=True)
    ready_at = Column(String, nullable=True)
    served_at = Column(String, nullable=True)