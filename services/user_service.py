from sqlalchemy.orm import Session
from models.user import User
from data.database import db
from utils.logger import setup_logger
import json
from typing import Dict, Any

logger = setup_logger(__name__)

class UserService:
    @staticmethod
    def get_user(user_id: str) -> Dict[str, Any]:
        session = db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            return user.to_dict() if user else None
        finally:
            session.close()
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        session = db.get_session()
        try:
            user = User(
                user_id=user_data['user_id'],
                name=user_data.get('name'),
                phone=user_data.get('phone'),
                email=user_data.get('email'),
                preferences=json.dumps(user_data.get('preferences', {})),
                allergens=json.dumps(user_data.get('allergens', []))
            )
            session.add(user)
            session.commit()
            logger.info(f"Created user: {user_data['user_id']}")
            return user.to_dict()
        finally:
            session.close()
    
    @staticmethod
    def update_user(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        session = db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                if 'name' in user_data:
                    user.name = user_data['name']
                if 'phone' in user_data:
                    user.phone = user_data['phone']
                if 'email' in user_data:
                    user.email = user_data['email']
                if 'preferences' in user_data:
                    user.preferences = json.dumps(user_data['preferences'])
                if 'allergens' in user_data:
                    user.allergens = json.dumps(user_data['allergens'])
                session.commit()
                logger.info(f"Updated user: {user_id}")
                return user.to_dict()
            return None
        finally:
            session.close()
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        session = db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                session.delete(user)
                session.commit()
                logger.info(f"Deleted user: {user_id}")
                return True
            return False
        finally:
            session.close()
    
    @staticmethod
    def update_preferences(user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        session = db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                existing_prefs = user.preferences if isinstance(user.preferences, dict) else json.loads(user.preferences) if user.preferences else {}
                existing_prefs.update(preferences)
                user.preferences = json.dumps(existing_prefs)
                session.commit()
                logger.info(f"Updated preferences for user: {user_id}")
                return user.to_dict()
            return None
        finally:
            session.close()