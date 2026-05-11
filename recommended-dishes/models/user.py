from sqlalchemy import Column, String, JSON, DateTime
from models.base import Base
from datetime import datetime
import json

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String(36), primary_key=True)
    name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    preferences = Column(JSON)
    allergens = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'preferences': self.preferences if isinstance(self.preferences, dict) else json.loads(self.preferences) if self.preferences else {},
            'allergens': self.allergens if isinstance(self.allergens, list) else json.loads(self.allergens) if self.allergens else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }