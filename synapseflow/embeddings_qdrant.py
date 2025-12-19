from .openai_integration import get_embedding
from .qdrant_adapter import QdrantAdapter
from typing import List

class EmbeddingMemory:
    def __init__(self, qdrant_url: str = None):
        # Initialize adapter; will raise if qdrant-client not installed
        self.adapter = QdrantAdapter(url=qdrant_url) if (qdrant_url or True) else None

    def upsert_text(self, user_id: str, text: str, meta: dict = None):
        emb = None
        try:
            emb = get_embedding(text)
        except Exception as e:
            print('Embedding failed, upserting without vector:', e)
        self.adapter.upsert(user_id, text, meta or {}, vector=emb)

    def query(self, user_id: str, query_text: str, top_k: int = 5):
        try:
            qemb = get_embedding(query_text)
            return self.adapter.query(user_id, query_text, top_k=top_k, vector=qemb)
        except Exception as e:
            print('Embedding query failed, falling back to payload search:', e)
            return self.adapter.query(user_id, query_text, top_k=top_k, vector=None)
