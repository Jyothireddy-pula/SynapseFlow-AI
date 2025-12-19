import os, time, json
from typing import Optional, Dict, Any, List
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest
except Exception:
    QdrantClient = None
    rest = None

class QdrantAdapter:
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, collection: str = 'synapseflow_memory'):
        if QdrantClient is None:
            raise RuntimeError('qdrant-client not installed. pip install qdrant-client')
        self.url = url or os.getenv('QDRANT_URL') or 'http://localhost:6333'
        self.api_key = api_key or os.getenv('QDRANT_API_KEY') or None
        self.client = QdrantClient(url=self.url, api_key=self.api_key)
        self.collection = collection
        # create collection if not exists
        try:
            self.client.recreate_collection(collection_name=self.collection, vector_size=384, distance=rest.Distance.COSINE)
        except Exception:
            try:
                self.client.create_collection(collection_name=self.collection, vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE))
            except Exception:
                pass

    def upsert(self, user_id: str, text: str, meta: Optional[Dict[str,Any]] = None, vector: Optional[List[float]] = None):
        vec = vector or [0.0]*384
        payload = {'user_id': user_id, 'text': text, 'meta': meta or {}}
        point_id = f"{user_id}-{int(time.time()*1000)}"
        try:
            self.client.upsert(collection_name=self.collection, points=[rest.PointStruct(id=point_id, vector=vec, payload=payload)])
        except Exception as e:
            print('Qdrant upsert failed:', e)


def search_by_vector(self, vector: List[float], top_k: int = 5):
    """Search the collection using a vector and return top_k results."""
    try:
        resp = self.client.search(collection_name=self.collection, query_vector=vector, limit=top_k, with_payload=True)
        results = []
        for r in resp:
            payload = r.payload or {}
            results.append({'id': r.id, 'score': getattr(r, 'score', None), 'text': payload.get('text',''), 'payload': payload})
        return results
    except Exception as e:
        print('Qdrant search_by_vector failed:', e)
        return []

    def query(self, user_id: str, query: str, top_k: int = 5, vector: Optional[List[float]] = None):
        # stub: use scroll filter by user_id to show demo results
        try:
            if vector is not None:
                return self.search_by_vector(vector, top_k)
            resp = self.client.scroll(collection_name=self.collection, limit=top_k, with_payload=True, with_vector=False, filter=rest.Filter(must=[rest.FieldCondition(key='user_id', match=rest.MatchValue(value=user_id))]))
            results = []
            for p in resp:
                payload = p.payload or {}
                results.append({'id': p.id, 'text': payload.get('text',''), 'payload': payload})
            return results
        except Exception as e:
            print('Qdrant query failed:', e)
            return []
