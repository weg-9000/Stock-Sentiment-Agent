"""
Milvus 혹은 Pinecone – 유사 텍스트 검색 (RAG)
"""
import pymilvus, numpy as np
from config import settings

class VectorSearch:
    DIM = 768
    INDEX = "tweet_embeddings"

    def __init__(self):
        self._client = pymilvus.Collection(self.INDEX)  # pragma: no cover
        # TODO: collection & index 생성 로직

    def insert(self, vec: np.ndarray, meta: dict):
        self._client.insert([vec.tolist(), meta])

    def similar(self, vec: np.ndarray, k=10) -> list[dict]:
        res = self._client.search([vec.tolist()], "vector", k=k)
        # TODO: 결과 파싱
        return res
