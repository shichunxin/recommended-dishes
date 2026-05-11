from services.llm_service import LLMService
from utils.logger import setup_logger
import json
from typing import Dict, Any, List

logger = setup_logger(__name__)

class ReflectionModule:
    def __init__(self):
        self.llm = LLMService()
        logger.info("Reflection module initialized")
    
    def evaluate_recommendation(self, recommendation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        evaluation = self.llm.evaluate_recommendation(recommendation, context)
        
        overall_score = sum([
            evaluation.get('relevance', 3),
            evaluation.get('diversity', 3),
            evaluation.get('attractiveness', 3),
            evaluation.get('practicality', 3)
        ]) / 4
        
        return {
            **evaluation,
            'overall_score': overall_score,
            'confidence': self.calculate_confidence(evaluation)
        }
    
    def calculate_confidence(self, evaluation: Dict[str, Any]) -> float:
        scores = [
            evaluation.get('relevance', 3),
            evaluation.get('diversity', 3),
            evaluation.get('attractiveness', 3),
            evaluation.get('practicality', 3)
        ]
        
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        
        confidence = min(1.0, max(0.0, (avg_score / 5) * (1 - variance / 4)))
        return confidence
    
    def analyze_feedback(self, feedback: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""分析以下推荐反馈：

反馈内容：
{json.dumps(feedback, ensure_ascii=False)}

推荐上下文：
{json.dumps(context, ensure_ascii=False)}

请分析：
1. 用户接受了哪些推荐？
2. 用户拒绝了哪些推荐？
3. 用户有什么新的偏好或需求？
4. 下次推荐应该如何调整？

请以JSON格式返回分析结果。"""
        
        result = self.llm.generate(prompt, max_tokens=512, temperature=0.3)
        try:
            return json.loads(result)
        except:
            logger.warning("Failed to parse feedback analysis")
            return {
                "accepted": [],
                "rejected": [],
                "new_preferences": {},
                "suggestions": ""
            }
    
    def learn_from_feedback(self, feedback: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        analysis = self.analyze_feedback(feedback, {"user_profile": user_profile})
        
        updated_profile = user_profile.copy()
        preferences = updated_profile.get('preferences', {})
        
        new_prefs = analysis.get('new_preferences', {})
        preferences.update(new_prefs)
        
        suggestions = analysis.get('suggestions', "")
        if suggestions:
            preferences['last_feedback_suggestion'] = suggestions
        
        updated_profile['preferences'] = preferences
        return updated_profile
    
    def generate_improvement_suggestion(self, evaluations: List[Dict[str, Any]]) -> str:
        if not evaluations:
            return "暂无足够数据进行分析"
        
        avg_relevance = sum(e.get('relevance', 3) for e in evaluations) / len(evaluations)
        avg_diversity = sum(e.get('diversity', 3) for e in evaluations) / len(evaluations)
        avg_attractiveness = sum(e.get('attractiveness', 3) for e in evaluations) / len(evaluations)
        avg_practicality = sum(e.get('practicality', 3) for e in evaluations) / len(evaluations)
        
        suggestions = []
        
        if avg_relevance < 3.5:
            suggestions.append("提高推荐与用户需求的相关性")
        if avg_diversity < 3.5:
            suggestions.append("增加推荐菜品的多样性")
        if avg_attractiveness < 3.5:
            suggestions.append("优化推荐话术的吸引力")
        if avg_practicality < 3.5:
            suggestions.append("提升推荐的实用性")
        
        if suggestions:
            return "、".join(suggestions)
        return "推荐质量良好，继续保持"