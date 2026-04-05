from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from qdrant_client.http import models as qmodels
import os
import uuid

# ── Lazy init — nothing runs at import time ──────────────────────
_qdrant_client = None
_embedding_model = None

COLLECTION_NAME = "roadmaps"
USER_COLLECTION = "user_roadmaps"
VECTOR_SIZE = 384


def get_client():
    global _qdrant_client
    if _qdrant_client is None:
        url = os.getenv("QDRANT_URL", "http://localhost:6333")
        api_key = os.getenv("QDRANT_API_KEY", None)
        _qdrant_client = QdrantClient(url=url, api_key=api_key)
    return _qdrant_client


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def init_qdrant_collection():
    try:
        client = get_client()
        if not client.collection_exists(COLLECTION_NAME):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )
            print(f"✅ Qdrant collection '{COLLECTION_NAME}' created.")
        else:
            print(f"ℹ️ Qdrant collection '{COLLECTION_NAME}' already exists.")
    except Exception as e:
        print(f"⚠️ Qdrant initialization failed: {e}")


def init_user_roadmaps_collection():
    try:
        client = get_client()
        if not client.collection_exists(USER_COLLECTION):
            client.create_collection(
                collection_name=USER_COLLECTION,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
            )
            print(f"✅ Created '{USER_COLLECTION}' collection.")
        else:
            print(f"ℹ️ Qdrant collection '{USER_COLLECTION}' already exists.")
    except Exception as e:
        print(f"⚠️ Failed to init '{USER_COLLECTION}': {e}")


def insert_roadmap(user_id: str, vector: list, roadmap_data: dict):
    try:
        get_client().upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"user_id": user_id, "roadmap": roadmap_data}
            )]
        )
    except Exception as e:
        print(f"⚠️ Failed to insert roadmap in Qdrant: {e}")


def insert_user_roadmap(user_id: str, roadmap_id: str, prompt: str):
    try:
        vector = get_embedding_model().encode(prompt).tolist()
        get_client().upsert(
            collection_name=USER_COLLECTION,
            points=[PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"user_id": user_id, "roadmap_id": roadmap_id, "prompt": prompt}
            )]
        )
    except Exception as e:
        print(f"⚠️ Failed to insert user_roadmap in Qdrant: {e}")


def search_roadmaps(query: str, top_k: int = 3):
    try:
        query_vector = get_embedding_model().encode(query).tolist()
        results = get_client().search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k
        )
        return [{"score": r.score, "payload": r.payload} for r in results]
    except Exception as e:
        print(f"⚠️ Qdrant search failed: {e}")
        return []


def search_user_roadmaps(user_id: str, query: str, top_k: int = 5):
    try:
        query_vector = get_embedding_model().encode(query).tolist()
        results = get_client().search(
            collection_name=USER_COLLECTION,
            query_vector=query_vector,
            query_filter=qmodels.Filter(
                must=[qmodels.FieldCondition(
                    key="user_id",
                    match=qmodels.MatchValue(value=user_id)
                )]
            ),
            limit=top_k
        )
        return [{"score": r.score, "payload": r.payload} for r in results]
    except Exception as e:
        print(f"⚠️ Qdrant user roadmap search failed: {e}")
        return []