from services.llm_service import LLMService
from agent.tools import RecommendationTools
from agent.memory import MemorySystem
from agent.reflection import ReflectionModule
from config import config
from utils.logger import setup_logger
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

logger = setup_logger(__name__)

class RecommendationAgent:
    def __init__(self):
        self.llm = LLMService()
        self.memory = MemorySystem()
        self.reflection = ReflectionModule()
        self.conversations = {}
        logger.info("Recommendation Agent initialized")
    
    def get_or_create_session(self, session_id: str = None) -> tuple:
        if not session_id:
            session_id = str(uuid.uuid4())
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                "history": [],
                "user_profile": None,
                "current_order": [],
                "temporary_profile": {},
                "clarification_count": 0
            }
        return session_id, self.conversations[session_id]
    
    def analyze_intent(self, user_input: str) -> str:
        return self.llm.extract_intent(user_input)
    
    def decide_tool_call(self, intent: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        tool_calls = []
        
        if intent == "recommend":
            tool_calls.append({"name": "get_all_dishes", "parameters": {}})
            if context.get("user_id"):
                tool_calls.append({"name": "get_user_profile", "parameters": {"user_id": context["user_id"]}})
        
        elif intent == "inquire":
            tool_calls.append({"name": "search_dishes", "parameters": {"query": context.get("user_input", "")}})
        
        elif intent == "add_to_cart":
            if context.get("user_id"):
                tool_calls.append({"name": "get_user_profile", "parameters": {"user_id": context["user_id"]}})
        
        elif intent == "upsell":
            last_item = context.get("current_order", [])[-1] if context.get("current_order") else None
            if last_item:
                tool_calls.append({"name": "get_dish_compatibility", "parameters": {"dish_id": last_item}})
        
        elif intent == "scene_based":
            tool_calls.append({"name": "get_hot_dishes", "parameters": {"limit": 20}})
            if context.get("user_id"):
                tool_calls.append({"name": "get_user_profile", "parameters": {"user_id": context["user_id"]}})
        
        return tool_calls
    
    def call_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for tool_call in tool_calls:
            result = RecommendationTools.call_tool(
                tool_call["name"],
                **tool_call["parameters"]
            )
            results.append({
                "tool": tool_call["name"],
                "result": result
            })
        return results
    
    def multi_objective_ranking(self, dishes: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        user_profile = context.get("user_profile", {})
        preferences = user_profile.get("preferences", {})
        
        scored_dishes = []
        for dish in dishes:
            score = 0.0
            
            if preferences:
                flavor_match = len(set(dish.get('tags', [])) & set(preferences.get('favorite_flavors', [])))
                category_match = 1 if dish.get('category') in preferences.get('favorite_categories', []) else 0
                score += (flavor_match * 0.1 + category_match * 0.15) * config.SORTING_WEIGHTS['customer_preference']
            
            if dish.get('cost') and dish.get('price'):
                profit_margin = (dish['price'] - dish['cost']) / dish['price']
                score += profit_margin * config.SORTING_WEIGHTS['profit_margin']
            
            score += dish.get('popularity', 0.0) * config.SORTING_WEIGHTS['popularity']
            
            if dish.get('compatibility_score'):
                score += dish['compatibility_score'] * config.SORTING_WEIGHTS['compatibility']
            
            if dish.get('is_new', False):
                score += 0.5 * config.SORTING_WEIGHTS['novelty']
            
            scored_dishes.append({**dish, 'score': score})
        
        return sorted(scored_dishes, key=lambda x: x.get('score', 0), reverse=True)
    
    def generate_response(self, intent: str, context: Dict[str, Any], tool_results: List[Dict[str, Any]]) -> str:
        dishes = []
        user_profile = context.get("user_profile", {})
        
        for result in tool_results:
            if result["result"].get("success"):
                data = result["result"]["data"]
                if result["tool"] in ["get_all_dishes", "search_dishes", "get_hot_dishes", "get_dish_compatibility"]:
                    dishes.extend(data if isinstance(data, list) else [data])
                elif result["tool"] == "get_user_profile":
                    user_profile = data
        
        if intent == "recommend":
            ranked_dishes = self.multi_objective_ranking(dishes, context)[:config.RECOMMENDATION_MAX_ITEMS]
            return self.llm.generate_recommendation(context, ranked_dishes)
        
        elif intent == "upsell":
            if dishes:
                ranked_dishes = self.multi_objective_ranking(dishes, context)[:3]
                main_dish = context.get("current_order", [])[-1] if context.get("current_order") else {}
                return self.llm.generate_upsell_prompt(main_dish, ranked_dishes)
            return "暂时没有合适的搭配推荐"
        
        elif intent == "scene_based":
            ranked_dishes = self.multi_objective_ranking(dishes, context)[:config.RECOMMENDATION_MAX_ITEMS]
            return self.llm.generate_recommendation(context, ranked_dishes)
        
        elif intent == "inquire":
            if dishes:
                return f"我为您找到了以下菜品：\n" + "\n".join([f"- {d['name']}: {d['description']} ￥{d['price']}" for d in dishes[:5]])
            return "抱歉，没有找到相关菜品。"
        
        elif intent == "clarify":
            history = context.get("history", [])
            user_input = context.get("user_input", "")
            return self.generate_clarification_question(history, user_input)
        
        elif intent == "cold_start":
            return self.handle_cold_start(context)
        
        elif intent == "greet":
            return "您好！欢迎来到我们餐厅，请问今天想吃点什么？我可以为您推荐一些美味的菜品。"
        
        elif intent == "goodbye":
            return "感谢您的光临，期待下次再见！"
        
        else:
            return self.llm.generate_dialog_response(context.get("history", []), context.get("user_input", ""))
    
    def generate_clarification_question(self, history: List[Dict[str, str]], user_input: str) -> str:
        history_str = "\n".join([f"{item['role']}: {item['content']}" for item in history])
        prompt = f"""对话历史：
{history_str}

用户当前输入：{user_input}

用户意图不明确，请生成一个简洁、友好的追问问题以澄清用户需求。"""
        
        return self.llm.generate(prompt, max_tokens=128, temperature=0.7)
    
    def handle_cold_start(self, context: Dict[str, Any]) -> str:
        session = self.conversations.get(context.get("session_id"), {})
        temp_profile = session.get("temporary_profile", {})
        
        questions = [
            "初次见面，告诉我您今天的心情，我帮您量身定制一桌好菜。",
            "好的，喜欢川味麻辣还是湘味香辣呢？",
            "明白了！为您推荐今日精选..."
        ]
        
        step = session.get("clarification_count", 0)
        if step < len(questions):
            return questions[step]
        
        return "为您推荐今日精选菜品..."
    
    def run(self, user_input: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
        session_id, session = self.get_or_create_session(session_id)
        
        if user_id and not session["user_profile"]:
            user_data = RecommendationTools.call_tool("get_user_profile", user_id=user_id)
            if user_data.get("success"):
                session["user_profile"] = user_data["data"]
        
        context = {
            "user_input": user_input,
            "user_id": user_id,
            "history": session["history"],
            "user_profile": session["user_profile"],
            "current_order": session["current_order"],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        intent = self.analyze_intent(user_input)
        
        if intent == "cold_start" and session["clarification_count"] < 3:
            response = self.handle_cold_start(context)
            session["clarification_count"] += 1
            
            if session["clarification_count"] == 2:
                session["temporary_profile"]["flavor_preference"] = user_input
        else:
            tool_calls = self.decide_tool_call(intent, context)
            tool_results = self.call_tools(tool_calls)
            response = self.generate_response(intent, context, tool_results)
            
            evaluation = self.reflection.evaluate_recommendation(response, context)
            self.memory.store_recommendation(session_id, {
                "response": response,
                "context": context,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            })
        
        session["history"].append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        session["history"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        self.memory.store_conversation(session_id, session["history"])
        
        return {
            "session_id": session_id,
            "intent": intent,
            "response": response,
            "context": context
        }
    
    def add_to_cart(self, session_id: str, dish_id: str) -> List[str]:
        _, session = self.get_or_create_session(session_id)
        session["current_order"].append(dish_id)
        return session["current_order"]
    
    def get_current_order(self, session_id: str) -> List[str]:
        _, session = self.get_or_create_session(session_id)
        return session["current_order"]
    
    def clear_order(self, session_id: str) -> List[str]:
        _, session = self.get_or_create_session(session_id)
        session["current_order"] = []
        return session["current_order"]
    
    def update_user_profile(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        _, session = self.get_or_create_session(session_id)
        if session["user_profile"]:
            session["user_profile"].update(updates)
            if session["user_profile"].get("user_id"):
                self.memory.store_user_preferences(session["user_profile"]["user_id"], session["user_profile"].get("preferences", {}))
        return session["user_profile"]
    
    def submit_feedback(self, session_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        _, session = self.get_or_create_session(session_id)
        
        if session["user_profile"] and session["user_profile"].get("user_id"):
            updated_profile = self.reflection.learn_from_feedback(feedback, session["user_profile"])
            session["user_profile"] = updated_profile
            
            from services.user_service import UserService
            UserService.update_user(session["user_profile"]["user_id"], {"preferences": updated_profile.get("preferences", {})})
            
            self.memory.store_user_preferences(session["user_profile"]["user_id"], updated_profile.get("preferences", {}))
        
        return {"status": "success", "message": "反馈已接收"}