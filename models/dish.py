from sqlalchemy import Column, String, Float, Boolean, Text, JSON
from models.base import Base
import json

class Dish(Base):
    __tablename__ = 'dishes'
    
    dish_id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    tags = Column(JSON)
    image_url = Column(String(255))
    is_available = Column(Boolean, default=True)
    is_hot = Column(Boolean, default=False)
    is_new = Column(Boolean, default=False)
    cost = Column(Float)
    popularity = Column(Float, default=0.0)
    compatibility = Column(JSON)
    
    def to_dict(self):
        return {
            'dish_id': self.dish_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'tags': self.tags if isinstance(self.tags, list) else json.loads(self.tags) if self.tags else [],
            'image_url': self.image_url,
            'is_available': self.is_available,
            'is_hot': self.is_hot,
            'is_new': self.is_new,
            'cost': self.cost,
            'popularity': self.popularity,
            'compatibility': self.compatibility if isinstance(self.compatibility, dict) else json.loads(self.compatibility) if self.compatibility else {}
        }