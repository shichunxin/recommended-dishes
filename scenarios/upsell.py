from agent.core_agent import RecommendationAgent
from services.dish_service import DishService
from services.llm_service import LLMService
from utils.logger import setup_logger
import json
from typing import Dict, Any, List

logger = setup_logger(__name__)

class UpsellScenario:
    def __init__(self):
        self.agent = RecommendationAgent()
        self.llm = LLMService()
        logger.info("Upsell scenario initialized")
    
    def recommend_complements(self, main_dish_id: str, session_id: str = None) -> Dict[str, Any]:
        main_dish = DishService.get_dish(main_dish_id)
        if not main_dish:
            return {"success": False, "error": "菜品不存在"}
        
        complements = DishService.get_dish_compatibility(main_dish_id)
        
        if not complements:
            return {"success": False, "error": "暂无搭配推荐"}
        
        ranked_complements = self.rank_complements(main_dish, complements)
        
        recommendation = self.llm.generate_upsell_prompt(main_dish, ranked_complements[:3])
        
        return {
            "success": True,
            "main_dish": main_dish,
            "complements": ranked_complements,
            "recommendation": recommendation
        }
    
    def rank_complements(self, main_dish: Dict[str, Any], complements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for comp in complements:
            score = comp.get('compatibility_score', 0.0)
            
            if comp.get('is_hot'):
                score += 0.2
            
            if main_dish.get('category') != comp.get('category'):
                score += 0.15
            
            if comp.get('price') and main_dish.get('price'):
                price_ratio = comp['price'] / main_dish['price']
                if 0.2 <= price_ratio <= 0.8:
                    score += 0.1
            
            scored.append({**comp, 'upsell_score': score})
        
        return sorted(scored, key=lambda x: x.get('upsell_score', 0), reverse=True)
    
    def handle_add_to_cart(self, dish_id: str, session_id: str) -> Dict[str, Any]:
        self.agent.add_to_cart(session_id, dish_id)
        
        result = self.recommend_complements(dish_id, session_id)
        
        if result.get("success"):
            return {
                "status": "success",
                "message": result["recommendation"]
            }
        
        return {
            "status": "success",
            "message": "已添加到购物车"
        }