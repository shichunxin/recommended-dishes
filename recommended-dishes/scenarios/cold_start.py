from agent.core_agent import RecommendationAgent
from services.dish_service import DishService
from services.user_service import UserService
from services.llm_service import LLMService
from utils.logger import setup_logger
import json
from typing import Dict, Any, List

logger = setup_logger(__name__)

class ColdStartScenario:
    def __init__(self):
        self.agent = RecommendationAgent()
        self.llm = LLMService()
        self.dialog_steps = [
            {
                "question": "初次见面，告诉我您今天的心情，我帮您量身定制一桌好菜。",
                "extract": "mood"
            },
            {
                "question": "好的，喜欢川味麻辣还是湘味香辣呢？",
                "extract": "flavor_preference"
            },
            {
                "question": "明白了！为您推荐今日精选...",
                "extract": None
            }
        ]
        logger.info("Cold start scenario initialized")
    
    def start_dialog(self, session_id: str) -> Dict[str, Any]:
        result = self.agent.run("冷启动引导", session_id=session_id)
        return {
            "success": True,
            "response": result["response"],
            "session_id": session_id,
            "step": 0
        }
    
    def continue_dialog(self, session_id: str, user_input: str, step: int) -> Dict[str, Any]:
        if step >= len(self.dialog_steps) - 1:
            return self.generate_recommendation(session_id, user_input)
        
        result = self.agent.run(user_input, session_id=session_id)
        
        _, session = self.agent.get_or_create_session(session_id)
        extract_field = self.dialog_steps[step]["extract"]
        
        if extract_field:
            session["temporary_profile"][extract_field] = user_input
        
        next_step = step + 1
        if next_step < len(self.dialog_steps):
            next_question = self.dialog_steps[next_step]["question"]
            session["history"].append({
                "role": "assistant",
                "content": next_question,
                "timestamp": result["context"]["timestamp"]
            })
            return {
                "success": True,
                "response": next_question,
                "session_id": session_id,
                "step": next_step,
                "temporary_profile": session["temporary_profile"]
            }
        
        return self.generate_recommendation(session_id, user_input)
    
    def generate_recommendation(self, session_id: str, last_input: str) -> Dict[str, Any]:
        _, session = self.agent.get_or_create_session(session_id)
        temp_profile = session.get("temporary_profile", {})
        
        all_dishes = DishService.get_all_dishes()
        filtered_dishes = self.filter_by_temp_profile(all_dishes, temp_profile)
        
        ranked_dishes = self.rank_for_cold_start(filtered_dishes, temp_profile)[:6]
        
        context = {
            "temporary_profile": temp_profile,
            "last_input": last_input
        }
        
        recommendation = self.llm.generate_recommendation(context, ranked_dishes)
        
        return {
            "success": True,
            "response": recommendation,
            "session_id": session_id,
            "step": len(self.dialog_steps),
            "temporary_profile": temp_profile,
            "recommendations": ranked_dishes
        }
    
    def filter_by_temp_profile(self, dishes: List[Dict[str, Any]], temp_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not temp_profile:
            return dishes
        
        flavor_pref = temp_profile.get("flavor_preference", "").lower()
        mood = temp_profile.get("mood", "").lower()
        
        filtered = []
        for dish in dishes:
            tags = [t.lower() for t in dish.get('tags', [])]
            category = dish.get('category', "").lower()
            
            matches = 0
            if flavor_pref:
                if flavor_pref in tags or flavor_pref in category:
                    matches += 1
            
            if mood:
                mood_keywords = {
                    "happy": ["happy", "joy", "celebrate", "festive"],
                    "sad": ["comfort", "warm", "nourishing"],
                    "tired": ["quick", "light", "easy"],
                    "hungry": ["filling", "generous", "hearty"]
                }
                
                for keyword in mood_keywords.get(mood, []):
                    if keyword in tags:
                        matches += 1
            
            if matches > 0:
                filtered.append(dish)
        
        return filtered or dishes
    
    def rank_for_cold_start(self, dishes: List[Dict[str, Any]], temp_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        flavor_pref = temp_profile.get("flavor_preference", "").lower()
        
        scored = []
        for dish in dishes:
            score = dish.get('popularity', 0.5) * 0.4
            
            tags = [t.lower() for t in dish.get('tags', [])]
            if flavor_pref and flavor_pref in tags:
                score += 0.3
            
            if dish.get('is_hot'):
                score += 0.2
            
            if dish.get('is_new'):
                score += 0.1
            
            scored.append({**dish, 'cold_start_score': score})
        
        return sorted(scored, key=lambda x: x.get('cold_start_score', 0), reverse=True)