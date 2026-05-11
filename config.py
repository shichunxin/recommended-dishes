import os
from typing import Dict, Any

class Config:
    # 数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DB = os.getenv('MYSQL_DB', 'catering')
    
    # Chroma向量数据库配置
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIR', './chroma_db')
    CHROMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION', 'catering_recommendations')
    
    # LLM配置
    LLM_MODEL = os.getenv('LLM_MODEL', 'qwen-7b-chat')
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:8000/v1')
    
    # 应用配置
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', 8001))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 推荐策略配置
    RECOMMENDATION_MAX_ITEMS = int(os.getenv('RECOMMENDATION_MAX_ITEMS', 6))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.7))
    
    # 多目标排序权重
    SORTING_WEIGHTS: Dict[str, float] = {
        'customer_preference': 0.35,
        'profit_margin': 0.25,
        'popularity': 0.20,
        'compatibility': 0.15,
        'novelty': 0.05
    }

config = Config()