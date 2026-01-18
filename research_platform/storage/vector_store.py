from typing import List, Dict, Any, Optional
from functools import lru_cache
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger


class VectorStore:
    def __init__(self, db_type: str = "chroma", persist_directory: str = "./data/chroma"):
        self.db_type = db_type
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        if db_type == "chroma":
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name="research_papers",
                metadata={"description": "Research paper embeddings"}
            )
            logger.info("ChromaDB vector store initialized")
        else:
            raise ValueError(f"Unsupported vector DB type: {db_type}")
    
    def add_paper(self, paper_id: str, title: str, abstract: str, metadata: Dict[str, Any]) -> None:
        try:
            text = f"{title}\n\n{abstract}"
            embedding = self.embedder.encode(text).tolist()
            
            self.collection.upsert(
                ids=[paper_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[text]
            )
            logger.debug(f"Added paper to vector store: {paper_id}")
        except Exception as e:
            logger.error(f"Error adding paper to vector store: {e}")
            raise
    
    def search_similar_papers(
        self, 
        query: str, 
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.embedder.encode(query).tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata if filter_metadata else None
            )
            
            papers = []
            if results['ids'] and len(results['ids']) > 0:
                for i, paper_id in enumerate(results['ids'][0]):
                    papers.append({
                        "paper_id": paper_id,
                        "distance": results['distances'][0][i] if results['distances'] else 0,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "document": results['documents'][0][i] if results['documents'] else ""
                    })
            
            return papers
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def delete_paper(self, paper_id: str) -> None:
        try:
            self.collection.delete(ids=[paper_id])
            logger.debug(f"Deleted paper from vector store: {paper_id}")
        except Exception as e:
            logger.error(f"Error deleting paper from vector store: {e}")


@lru_cache()
def get_vector_store(db_type: str = "chroma") -> VectorStore:
    return VectorStore(db_type=db_type)
