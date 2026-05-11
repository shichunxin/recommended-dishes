from services.user_service import UserService
from services.dish_service import DishService
from services.order_service import OrderService
from utils.logger import setup_logger
import json
from typing import Dict, Any, List

logger = setup_logger(__name__)

class RecommendationTools:
    @staticmethod
    def get_user_profile(user_id: str) -> Dict[str, Any]:
        logger.debug(f"Getting user profile: {user_id}")
        return UserService.get_user(user_id)
    
    @staticmethod
    def get_dish_info(dish_id: str) -> Dict[str, Any]:
        logger.debug(f"Getting dish info: {dish_id}")
        return DishService.get_dish(dish_id)
    
    @staticmethod
    def get_all_dishes() -> List[Dict[str, Any]]:
        logger.debug("Getting all dishes")
        return DishService.get_all_dishes()
    
    @staticmethod
    def get_dishes_by_category(category: str) -> List[Dict[str, Any]]:
        logger.debug(f"Getting dishes by category: {category}")
        return DishService.get_dishes_by_category(category)
    
    @staticmethod
    def get_user_orders(user_id: str) -> List[Dict[str, Any]]:
        logger.debug(f"Getting user orders: {user_id}")
        return OrderService.get_orders_by_user(user_id)
    
    @staticmethod
    def search_dishes(query: str) -> List[Dict[str, Any]]:
        logger.debug(f"Searching dishes: {query}")
        return DishService.search_dishes(query)
    
    @staticmethod
    def get_dish_compatibility(dish_id: str) -> List[Dict[str, Any]]:
        logger.debug(f"Getting dish compatibility: {dish_id}")
        return DishService.get_dish_compatibility(dish_id)
    
    @staticmethod
    def get_hot_dishes(limit: int = 10) -> List[Dict[str, Any]]:
        logger.debug(f"Getting hot dishes, limit: {limit}")
        return DishService.get_hot_dishes(limit)
    
    @staticmethod
    def get_new_dishes(limit: int = 10) -> List[Dict[str, Any]]:
        logger.debug(f"Getting new dishes, limit: {limit}")
        return DishService.get_new_dishes(limit)
    
    TOOLS = [
        {
            "name": "get_user_profile",
            "description": "获取用户画像信息，包括偏好、过敏信息等",
            "parameters": {
                "user_id": {"type": "string", "description": "用户ID", "required": True}
            }
        },
        {
            "name": "get_dish_info",
            "description": "获取菜品详情信息",
            "parameters": {
                "dish_id": {"type": "string", "description": "菜品ID", "required": True}
            }
        },
        {
            "name": "get_all_dishes",
            "description": "获取所有可用菜品列表",
            "parameters": {}
        },
        {
            "name": "get_dishes_by_category",
            "description": "按类别获取菜品列表",
            "parameters": {
                "category": {"type": "string", "description": "菜品类别", "required": True}
            }
        },
        {
            "name": "get_user_orders",
            "description": "获取用户历史订单",
            "parameters": {
                "user_id": {"type": "string", "description": "用户ID", "required": True}
            }
        },
        {
            "name": "search_dishes",
            "description": "根据关键词搜索菜品",
            "parameters": {
                "query": {"type": "string", "description": "搜索关键词", "required": True}
            }
        },
        {
            "name": "get_dish_compatibility",
            "description": "获取菜品的搭配推荐",
            "parameters": {
                "dish_id": {"type": "string", "description": "菜品ID", "required": True}
            }
        },
        {
            "name": "get_hot_dishes",
            "description": "获取热门菜品",
            "parameters": {
                "limit": {"type": "integer", "description": "返回数量限制", "required": False}
            }
        },
        {
            "name": "get_new_dishes",
            "description": "获取新品菜品",
            "parameters": {
                "limit": {"type": "integer", "description": "返回数量限制", "required": False}
            }
        }
    ]
    
    @classmethod
    def call_tool(cls, tool_name: str, **kwargs) -> Dict[str, Any]:
        try:
            method = getattr(cls, tool_name)
            result = method(**kwargs)
            return {"success": True, "data": result}
        except AttributeError:
            logger.error(f"Tool {tool_name} not found")
            return {"success": False, "error": f"Tool {tool_name} not found"}
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {"success": False, "error": str(e)}