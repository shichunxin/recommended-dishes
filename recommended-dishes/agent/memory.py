from data.chroma_store import chroma_store
from utils.logger import setup_logger
import json
import uuid
from typing import Dict, Any, List

logger = setup_logger(__name__)

class MemorySystem:
    def __init__(self):
        self.chroma_store = chroma_store
        logger.info("Memory system initialized")
    
    def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        document = json.dumps({
            "user_id": user_id,
            "type": "preferences",
            "data": preferences
        }, ensure_ascii=False)
        
        self.chroma_store.add_documents(
            documents=[document],
            metadatas=[{"user_id": user_id, "type": "preferences"}],
            ids=[f"pref_{user_id}"]
        )
        logger.debug(f"Stored preferences for user: {user_id}")
    
    def retrieve_user_preferences(self, user_id: str) -> Dict[str, Any]:
        results = self.chroma_store.query(
            query_texts=[f"user preferences for {user_id}"],
            n_results=1,
            where={"user_id": user_id, "type": "preferences"}
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            try:
                data = json.loads(results['documents'][0][0])
                return data.get('data', {})
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode preferences for user: {user_id}")
                return {}
        return {}
    
    def store_conversation(self, session_id: str, conversation: List[Dict[str, str]]):
        document = json.dumps({
            "session_id": session_id,
            "type": "conversation",
            "data": conversation
        }, ensure_ascii=False)
        
        self.chroma_store.add_documents(
            documents=[document],
            metadatas=[{"session_id": session_id, "type": "conversation"}],
            ids=[f"conv_{session_id}_{uuid.uuid4().hex[:8]}"]
        )
        logger.debug(f"Stored conversation for session: {session_id}")
    
    def retrieve_conversation(self, session_id: str) -> List[Dict[str, str]]:
        results = self.chroma_store.query(
            query_texts=[f"conversation history for session {session_id}"],
            n_results=5,
            where={"session_id": session_id, "type": "conversation"}
        )
        
        conversations = []
        for doc in results['documents'][0]:
            try:
                data = json.loads(doc)
                conversations.extend(data.get('data', []))
            except json.JSONDecodeError:
                continue
        
        return sorted(conversations, key=lambda x: x.get('timestamp', 0))
    
    def store_recommendation(self, session_id: str, recommendation: Dict[str, Any]):
        document = json.dumps({
            "session_id": session_id,
            "type": "recommendation",
            "data": recommendation
        }, ensure_ascii=False)
        
        self.chroma_store.add_documents(
            documents=[document],
            metadatas=[{"session_id": session_id, "type": "recommendation"}],
            ids=[f"rec_{session_id}_{uuid.uuid4().hex[:8]}"]
        )
        logger.debug(f"Stored recommendation for session: {session_id}")
    
    def retrieve_recommendations(self, session_id: str) -> List[Dict[str, Any]]:
        results = self.chroma_store.query(
            query_texts=[f"recommendations for session {session_id}"],
            n_results=10,
            where={"session_id": session_id, "type": "recommendation"}
        )
        
        recommendations = []
        for doc in results['documents'][0]:
            try:
                data = json.loads(doc)
                recommendations.append(data.get('data', {}))
            except json.JSONDecodeError:
                continue
        
        return sorted(recommendations, key=lambda x: x.get('timestamp', 0), reverse=True)
    
    def clear_session_memory(self, session_id: str):
        results = self.chroma_store.query(
            query_texts=[""],
            n_results=100,
            where={"session_id": session_id}
        )
        
        ids_to_delete = results['ids'][0] if results['ids'] else []
        if ids_to_delete:
            self.chroma_store.delete(ids_to_delete)
            logger.debug(f"Cleared memory for session: {session_id}")