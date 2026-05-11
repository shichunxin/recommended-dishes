import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, Embeddings, Metadatas
from config import config
from utils.logger import setup_logger
from typing import List, Dict, Any, Optional

logger = setup_logger(__name__)

class ChromaStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        self.collection = self.client.get_or_create_collection(config.CHROMA_COLLECTION_NAME)
        logger.info("Chroma vector store initialized")
    
    def add_documents(self, documents: Documents, metadatas: Optional[Metadatas] = None, ids: Optional[List[str]] = None):
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.debug(f"Added {len(documents)} documents to vector store")
    
    def query(self, query_texts: List[str], n_results: int = 5, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )
        return results
    
    def update(self, ids: List[str], documents: Optional[Documents] = None, metadatas: Optional[Metadatas] = None):
        self.collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.debug(f"Updated {len(ids)} documents in vector store")
    
    def delete(self, ids: List[str]):
        self.collection.delete(ids=ids)
        logger.debug(f"Deleted {len(ids)} documents from vector store")
    
    def get(self, ids: List[str]) -> Dict[str, Any]:
        return self.collection.get(ids=ids)
    
    def count(self) -> int:
        return self.collection.count()
    
    def reset_collection(self):
        self.client.delete_collection(config.CHROMA_COLLECTION_NAME)
        self.collection = self.client.create_collection(config.CHROMA_COLLECTION_NAME)
        logger.info("Vector store collection reset")

chroma_store = ChromaStore()