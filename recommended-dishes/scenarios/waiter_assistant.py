from agent.core_agent import RecommendationAgent
from services.user_service import UserService
from services.dish_service import DishService
from services.llm_service import LLMService
from utils.logger import setup_logger
import json
from typing import Dict, Any, List

logger = setup_logger(__name__)

class WaiterAssistantScenario:
    def __init__(self):
        self.agent = RecommendationAgent()
        self.llm = LLMService()
        logger.info("Waiter assistant scenario initialized")
    
    def get_customer_info(self, user_id: str) -> Dict[str, Any]:
        user_profile = UserService.get_user(user_id)
        
        if not user_profile:
            return {"success": False, "error": "用户不存在"}
        
        preferences = user_profile.get("preferences", {})
        allergens = user_profile.get("allergens", [])
        
        return {
            "success": True,
            "user_id": user_id,
            "name": user_profile.get("name", ""),
            "preferences": preferences,
            "allergens": allergens,
            "favorite_flavors": preferences.get("favorite_flavors", []),
            "favorite_categories": preferences.get("favorite_categories", []),
            "price_range": preferences.get("price_range", "medium")
        }
    
    def recommend_for_table(self, table_id: str, user_ids: List[str] = None) -> Dict[str, Any]:
        customer_profiles = []
        all_preferences = set()
        all_allergens = set()
        
        if user_ids:
            for user_id in user_ids:
                info = self.get_customer_info(user_id)
                if info.get("success"):
                    customer_profiles.append(info)
                    all_preferences.update(info.get("favorite_flavors", []))
                    all_preferences.update(info.get("favorite_categories", []))
                    all_allergens.update(info.get("allergens", []))
        
        today_specials = DishService.get_hot_dishes(10)
        
        filtered_dishes = []
        for dish in today_specials:
            tags = dish.get('tags', [])
            
            if all_allergens and any(a in tags for a in all_allergens):
                continue
            
            filtered_dishes.append(dish)
        
        ranked_dishes = self.rank_for_group(filtered_dishes, all_preferences, len(customer_profiles))[:6]
        
        recommendation_text = self.generate_waiter_prompt(ranked_dishes, customer_profiles)
        
        return {
            "success": True,
            "table_id": table_id,
            "customer_count": len(customer_profiles),
            "profiles": customer_profiles,
            "recommendations": ranked_dishes,
            "recommendation_text": recommendation_text
        }
    
    def rank_for_group(self, dishes: List[Dict[str, Any]], preferences: set, group_size: int) -> List[Dict[str, Any]]:
        scored = []
        for dish in dishes:
            score = dish.get('popularity', 0.0) * 0.3
            
            tags = dish.get('tags', [])
            pref_match = len(set(tags) & preferences)
            score += pref_match * 0.2
            
            if dish.get('is_hot'):
                score += 0.2
            
            if group_size >= 3:
                if "sharing" in tags or "family" in tags:
                    score += 0.15
            else:
                if "individual" in tags or "single" in tags:
                    score += 0.1
            
            if dish.get('is_new'):
                score += 0.15
            
            scored.append({**dish, 'group_score': score})
        
        return sorted(scored, key=lambda x: x.get('group_score', 0), reverse=True)
    
    def generate_waiter_prompt(self, dishes: List[Dict[str, Any]], profiles: List[Dict[str, Any]]) -> str:
        if profiles:
            names = ", ".join([p.get("name", "") for p in profiles if p.get("name")])
            flavor_prefs = ", ".join(set([f for p in profiles for f in p.get("favorite_flavors", [])]))
            
            prompt = f"""服务员推荐场景：
                        顾客信息：{names}
                        口味偏好：{flavor_prefs}

                        推荐菜品：{json.dumps(dishes, ensure_ascii=False)}

                        请生成一段适合服务员口头推荐的话术，友好、简洁。"""
        else:
            prompt = f"""服务员推荐场景：
                        未知顾客

                        推荐菜品：{json.dumps(dishes, ensure_ascii=False)}

                        请生成一段适合服务员口头推荐的话术，友好、简洁。"""
        
        return self.llm.generate(prompt, max_tokens=128, temperature=0.7)
    
    def notify_waiter(self, table_id: str, message: str) -> Dict[str, Any]:
        logger.info(f"Notification sent to waiter for table {table_id}: {message}")
        return {
            "success": True,
            "table_id": table_id,
            "message": message,
            "timestamp": "2026-05-09T18:00:00Z"
        }