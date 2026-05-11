from sqlalchemy import Column, String, JSON, DateTime, Float
from models.base import Base
from datetime import datetime

class Recommendation(Base):
    __tablename__ = 'recommendations'
    
    recommendation_id = Column(String(36), primary_key=True)
    session_id = Column(String(36), nullable=False)
    user_id = Column(String(36))
    context = Column(JSON)
    recommended_dishes = Column(JSON)
    confidence = Column(Float, default=0.0)
    feedback = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'recommendation_id': self.recommendation_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'context': self.context if isinstance(self.context, dict) else {},
            'recommended_dishes': self.recommended_dishes if isinstance(self.recommended_dishes, list) else [],
            'confidence': self.confidence,
            'feedback': self.feedback if isinstance(self.feedback, dict) else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }