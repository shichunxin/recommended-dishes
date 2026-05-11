from agent.core_agent import RecommendationAgent
from services.dish_service import DishService
from services.user_service import UserService
from services.llm_service import LLMService
from utils.logger import setup_logger
import json
from datetime import datetime
from typing import Dict, Any, List

logger = setup_logger(__name__)

class SceneBasedScenario:
    def __init__(self):
        self.agent = RecommendationAgent()
        self.llm = LLMService()
        logger.info("Scene-based scenario initialized")
    
    def detect_scene(self, context: Dict[str, Any]) -> str:
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        is_weekend = day_of_week >= 5
        is_dinner = 17 <= hour <= 22
        is_lunch = 11 <= hour <= 14
        is_breakfast = 6 <= hour <= 10
        
        if is_weekend and is_dinner:
            return "weekend_dinner"
        elif is_weekend and is_lunch:
            return "weekend_lunch"
        elif is_dinner:
            return "weekday_dinner"
        elif is_lunch:
            return "weekday_lunch"
        elif is_breakfast:
            return "breakfast"
        else:
            return "general"
    
    def get_scene_features(self, scene: str) -> Dict[str, Any]:
        features = {
            "weekend_dinner": {
                "name": "周末约会",
                "priorities": ["appearance", "romantic", "premium"],
                "max_items": 4
            },
            "weekend_lunch": {
                "name": "周末聚餐",
                "priorities": ["variety", "sharing", "value"],
                "max_items": 6
            },
            "weekday_dinner": {
                "name": "工作日晚餐",
                "priorities": ["quick", "healthy", "affordable"],
                "max_items": 3
            },
            "weekday_lunch": {
                "name": "工作日午餐",
                "priorities": ["quick", "filling", "value"],
                "max_items": 2
            },
            "breakfast": {
                "name": "早餐",
                "priorities": ["quick", "light", "traditional"],
                "max_items": 2
            },
            "general": {
                "name": "日常用餐",
                "priorities": ["popular", "balanced"],
                "max_items": 5
            }
        }
        return features.get(scene, features["general"])
    
    def recommend_for_scene(self, user_id: str = None, table_info: Dict[str, Any] = None) -> Dict[str, Any]:
        context = {
            "user_id": user_id,
            "table_info": table_info,
            "timestamp": datetime.now().isoformat()
        }
        
        scene = self.detect_scene(context)
        scene_features = self.get_scene_features(scene)
        
        user_profile = UserService.get_user(user_id) if user_id else None
        
        all_dishes = DishService.get_all_dishes()
        filtered_dishes = self.filter_by_scene(all_dishes, scene_features)
        
        if user_profile:
            filtered_dishes = self.filter_by_preferences(filtered_dishes, user_profile)
        
        ranked_dishes = self.rank_by_scene(filtered_dishes, scene_features)[:scene_features["max_items"]]
        
        banner_text = self.generate_banner(scene_features, user_profile)
        
        return {
            "success": True,
            "scene": scene,
            "scene_name": scene_features["name"],
            "recommendations": ranked_dishes,
            "banner": banner_text,
            "context": context
        }
    
    def filter_by_scene(self, dishes: List[Dict[str, Any]], scene_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        priorities = scene_features.get("priorities", [])
        filtered = []
        
        for dish in dishes:
            tags = dish.get('tags', [])
            match_count = sum(1 for p in priorities if p.lower() in [t.lower() for t in tags])
            if match_count > 0 or "general" in priorities:
                filtered.append(dish)
        
        return filtered or dishes
    
    def filter_by_preferences(self, dishes: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        preferences = user_profile.get("preferences", {})
        if not preferences:
            return dishes
        
        favorite_flavors = preferences.get("favorite_flavors", [])
        favorite_categories = preferences.get("favorite_categories", [])
        allergens = user_profile.get("allergens", [])
        
        filtered = []
        for dish in dishes:
            tags = dish.get('tags', [])
            category = dish.get('category', "")
            
            if allergens and any(a in tags for a in allergens):
                continue
            
            flavor_match = len(set(tags) & set(favorite_flavors)) > 0
            category_match = category in favorite_categories
            
            if flavor_match or category_match or not (favorite_flavors or favorite_categories):
                filtered.append(dish)
        
        return filtered or dishes
    
    def rank_by_scene(self, dishes: List[Dict[str, Any]], scene_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        priorities = scene_features.get("priorities", [])
        
        scored = []
        for dish in dishes:
            score = dish.get('popularity', 0.0) * 0.3
            tags = dish.get('tags', [])
            
            for priority in priorities:
                if priority.lower() in [t.lower() for t in tags]:
                    score += 0.2
            
            if dish.get('is_hot'):
                score += 0.15
            
            if dish.get('is_new'):
                score += 0.1
            
            scored.append({**dish, 'scene_score': score})
        
        return sorted(scored, key=lambda x: x.get('scene_score', 0), reverse=True)
    
    def generate_banner(self, scene_features: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        user_name = user_profile.get('name', '') if user_profile else ''
        
        prompt = f"""场景：{scene_features['name']}
用户姓名：{user_name}
优先推荐：{', '.join(scene_features['priorities'])}

请生成一句吸引顾客的Banner文案，用于菜品推荐展示。"""
        
        return self.llm.generate(prompt, max_tokens=64, temperature=0.8)