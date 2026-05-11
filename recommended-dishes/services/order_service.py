from sqlalchemy.orm import Session
from models.order import Order
from data.database import db
from utils.logger import setup_logger
import uuid
from typing import Dict, Any, List

logger = setup_logger(__name__)

class OrderService:
    @staticmethod
    def get_order(order_id: str) -> Dict[str, Any]:
        session = db.get_session()
        try:
            order = session.query(Order).filter_by(order_id=order_id).first()
            return order.to_dict() if order else None
        finally:
            session.close()
    
    @staticmethod
    def create_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
        session = db.get_session()
        try:
            order = Order(
                order_id=str(uuid.uuid4()),
                user_id=order_data.get('user_id'),
                table_id=order_data.get('table_id'),
                items=order_data.get('items', []),
                total_amount=order_data.get('total_amount', 0.0),
                status='pending'
            )
            session.add(order)
            session.commit()
            logger.info(f"Created order: {order.order_id}")
            return order.to_dict()
        finally:
            session.close()
    
    @staticmethod
    def update_order(order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        session = db.get_session()
        try:
            order = session.query(Order).filter_by(order_id=order_id).first()
            if order:
                if 'items' in order_data:
                    order.items = order_data['items']
                if 'total_amount' in order_data:
                    order.total_amount = order_data['total_amount']
                if 'status' in order_data:
                    order.status = order_data['status']
                session.commit()
                logger.info(f"Updated order: {order_id}")
                return order.to_dict()
            return None
        finally:
            session.close()
    
    @staticmethod
    def get_orders_by_user(user_id: str) -> List[Dict[str, Any]]:
        session = db.get_session()
        try:
            orders = session.query(Order).filter_by(user_id=user_id).all()
            return [order.to_dict() for order in orders]
        finally:
            session.close()
    
    @staticmethod
    def get_orders_by_table(table_id: str) -> List[Dict[str, Any]]:
        session = db.get_session()
        try:
            orders = session.query(Order).filter_by(table_id=table_id).all()
            return [order.to_dict() for order in orders]
        finally:
            session.close()