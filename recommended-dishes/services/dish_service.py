from sqlalchemy.orm import Session
from models.dish import Dish
from data.database import db
from utils.logger import setup_logger
import json
from typing import List, Dict, Any

logger = setup_logger(__name__)

class DishService:
    @staticmethod
    def get_dish(dish_id: str) -> Dict[str, Any]:
        session = db.get_session()
        try:
            dish = session.query(Dish).filter_by(dish_id=dish_id).first()
            return dish.to_dict() if dish else None
        finally:
            session.close()
    
    @staticmethod
    def get_all_dishes(available_only: bool = True) -> List[Dict[str, Any]]:
        session = db.get_session()
        try:
            query = session.query(Dish)
            if available_only:
                query = query.filter_by(is_available=True)
            dishes = query.all()
            return [dish.to_dict() for dish in dishes]
        finally:
            session.close()
    
    @staticmethod
    def get_dishes_by_category(category: str) -> List[Dict[str, Any]]:
        session = db.get_session()
        try:
            dishes = session.query(Dish).filter_by(category=category, is_available=True).all()
            return [dish.to_dict() for dish in dishes]
        finally:
            session.close()
    
    @staticmethod
    def search_dishes(query: str) -> List[Dict[str, Any]]:
        all_dishes = DishService.get_all_dishes()
        query_lower = query.lower()
        return [dish for dish in all_dishes 
                if query_lower in dish['name'].lower() or 
                   (dish['description'] and query_lower in dish['description'].lower())]
    
    @staticmethod
    def get_dish_compatibility(dish_id: str) -> List[Dict[str, Any]]:
        dish = DishService.get_dish(dish_id)
        if not dish:
            return []
        
        compatibility = dish.get('compatibility', {})
        compatible_ids = list(compatibility.keys())
        
        session = db.get_session()
        try:
            dishes = session.query(Dish).filter(Dish.dish_id.in_(compatible_ids), Dish.is_available == True).all()
            result = [d.to_dict() for d in dishes]
            for d in result:
                d['compatibility_score'] = compatibility.get(d['dish_id'], 0.0)
            return sorted(result, key=lambda x: x.get('compatibility_score', 0), reverse=True)
        finally:
            session.close()
    
    @staticmethod
    def get_hot_dishes(limit: int = 10) -> List[Dict[str, Any]]:
        session = db.get_session()
        try:
            dishes = session.query(Dish).filter_by(is_available=True, is_hot=True).limit(limit).all()
            return [dish.to_dict() for dish in dishes]
        finally:
            session.close()
    
    @staticmethod
    def get_new_dishes(limit: int = 10) -> List[Dict[str, Any]]:
        session = db.get_session()
        try:
            dishes = session.query(Dish).filter_by(is_available=True, is_new=True).limit(limit).all()
            return [dish.to_dict() for dish in dishes]
        finally:
            session.close()
    
    @staticmethod
    def create_dish(dish_data: Dict[str, Any]) -> Dict[str, Any]:
        session = db.get_session()
        try:
            dish = Dish(
                dish_id=dish_data['dish_id'],
                name=dish_data['name'],
                description=dish_data.get('description'),
                price=dish_data['price'],
                category=dish_data.get('category'),
                tags=json.dumps(dish_data.get('tags', [])),
                image_url=dish_data.get('image_url'),
                is_available=dish_data.get('is_available', True),
                is_hot=dish_data.get('is_hot', False),
                is_new=dish_data.get('is_new', False),
                cost=dish_data.get('cost'),
                popularity=dish_data.get('popularity', 0.0),
                compatibility=json.dumps(dish_data.get('compatibility', {}))
            )
            session.add(dish)
            session.commit()
            logger.info(f"Created dish: {dish_data['name']}")
            return dish.to_dict()
        finally:
            session.close()
    
    @staticmethod
    def update_dish(dish_id: str, dish_data: Dict[str, Any]) -> Dict[str, Any]:
        session = db.get_session()
        try:
            dish = session.query(Dish).filter_by(dish_id=dish_id).first()
            if dish:
                for key, value in dish_data.items():
                    if hasattr(dish, key):
                        if key in ['tags', 'compatibility']:
                            setattr(dish, key, json.dumps(value))
                        else:
                            setattr(dish, key, value)
                session.commit()
                logger.info(f"Updated dish: {dish_id}")
                return dish.to_dict()
            return None
        finally:
            session.close()