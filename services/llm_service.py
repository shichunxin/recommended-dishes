from openai import OpenAI
from config import config
from utils.logger import setup_logger
import json
from typing import Dict, Any, List

logger = setup_logger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=config.LLM_API_KEY if config.LLM_API_KEY else "empty",
            base_url=config.LLM_BASE_URL
        )
        logger.info("LLM Service initialized")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的餐饮智能推荐助手，擅长理解顾客需求并提供个性化的菜品推荐。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            return f"Error: {str(e)}"
    
    def extract_intent(self, user_input: str) -> str:
        prompt = f"""分析用户意图，识别以下输入的意图类型：
输入：{user_input}

意图类型包括：
1. recommend - 请求菜品推荐
2. add_to_cart - 添加菜品到购物车
3. inquire - 询问菜品信息
4. greet - 问候语
5. goodbye - 告别
6. clarify - 需要追问澄清
7. cold_start - 新客冷启动
8. upsell - 搭售推荐
9. scene_based - 情景感知推荐

请只返回意图类型名称。"""
        
        result = self.generate(prompt, max_tokens=32, temperature=0.1)
        return result.strip()
    
    def generate_recommendation(self, context: Dict[str, Any], dishes: List[Dict[str, Any]]) -> str:
        prompt = f"""根据以下上下文信息，为顾客生成个性化推荐：

用户上下文：
{json.dumps(context, ensure_ascii=False)}

可用菜品：
{json.dumps(dishes, ensure_ascii=False)}

请以自然、友好的语言给出推荐建议，包括推荐理由，不超过300字。"""
        
        result = self.generate(prompt, max_tokens=512, temperature=0.7)
        return result
    
    def generate_dialog_response(self, history: List[Dict[str, str]], user_input: str) -> str:
        history_str = "\n".join([f"{item['role']}: {item['content']}" for item in history])
        prompt = f"""对话历史：
{history_str}

用户当前输入：{user_input}

请以友好、自然的方式回应，保持对话流畅。"""
        
        result = self.generate(prompt, max_tokens=512, temperature=0.7)
        return result
    
    def analyze_preferences(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""分析以下用户数据，提取口味偏好：

用户数据：
{json.dumps(user_data, ensure_ascii=False)}

请以JSON格式返回用户的口味偏好，包括：
- favorite_flavors: 喜欢的口味列表
- favorite_categories: 喜欢的菜品类别
- dietary_restrictions: 饮食限制
- price_range: 价格偏好（low/medium/high）"""
        
        result = self.generate(prompt, max_tokens=256, temperature=0.3)
        try:
            return json.loads(result)
        except:
            logger.warning("Failed to parse preference analysis result")
            return {"favorite_flavors": [], "favorite_categories": [], "dietary_restrictions": [], "price_range": "medium"}
    
    def evaluate_recommendation(self, recommendation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""评估以下推荐的质量：

推荐内容：{recommendation}

上下文信息：
{json.dumps(context, ensure_ascii=False)}

请从以下维度评估（每项1-5分）：
1. 相关性：推荐是否与用户需求相关
2. 多样性：推荐菜品是否多样化
3. 吸引力：推荐话术是否有吸引力
4. 实用性：推荐是否实用可行

请以JSON格式返回评估结果，格式：{{"relevance": 分数, "diversity": 分数, "attractiveness": 分数, "practicality": 分数}}"""
        
        result = self.generate(prompt, max_tokens=128, temperature=0.2)
        try:
            return json.loads(result)
        except:
            logger.warning("Failed to parse evaluation result")
            return {"relevance": 3, "diversity": 3, "attractiveness": 3, "practicality": 3}
    
    def generate_clarification_question(self, history: List[Dict[str, str]], user_input: str) -> str:
        prompt = f"""对话历史：
{history_str}

用户当前输入：{user_input}

用户意图不明确，请生成一个追问问题以澄清用户需求。问题要简洁、友好。"""
        
        result = self.generate(prompt, max_tokens=128, temperature=0.7)
        return result
    
    def generate_upsell_prompt(self, main_dish: Dict[str, Any], side_dishes: List[Dict[str, Any]]) -> str:
        prompt = f"""主菜品：{json.dumps(main_dish, ensure_ascii=False)}

搭配菜品：{json.dumps(side_dishes, ensure_ascii=False)}

请生成一句自然、有吸引力的搭售推荐话术，突出搭配优势。"""
        
        result = self.generate(prompt, max_tokens=128, temperature=0.8)
        return result