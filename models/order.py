from sqlalchemy import Column, String, Float, JSON, DateTime, Enum
from models.base import Base
from datetime import datetime

class Order(Base):
    __tablename__ = 'orders'
    
    ORDER_STATUS = ['pending', 'confirmed', 'preparing', 'served', 'completed', 'cancelled']
    
    order_id = Column(String(36), primary_key=True)
    user_id = Column(String(36))
    table_id = Column(String(36))
    items = Column(JSON)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(*ORDER_STATUS), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'table_id': self.table_id,
            'items': self.items if isinstance(self.items, list) else [],
            'total_amount': self.total_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }