from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from typing import List
import numpy as np

import sys


sys.path.insert(0, str(Path(__file__).parent.parent))


from config.settings import EMBEDDING_MODEL


# print(sys.path)


class OllamaEmbedder:
    def __init__(self):
        self.model = EMBEDDING_MODEL or "nomic-embed-text:latest"
        self.embedder = OllamaEmbeddings(model=self.model)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embedder.embed_query(text)
    

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        np_dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np_dot / (norm1 * norm2)
    

    def similarity_search(self, query: str, documents: List[str], k: int = 4) -> List[str]:
        query_embedding = self.embed_query(query)
        doc_embeddings = self.embed_documents(documents)

        # Calculate cosine similarities
        similarities = []
        for doc, emb in zip(documents, doc_embeddings):
            sim = self.cosine_similarity(query_embedding, emb)
            similarities.append((sim, doc))

        # Sort by similarity and return top k documents
        similarities.sort(reverse=True, key=lambda x: x[0])
        top_k_docs = [doc for _, doc in similarities[:k]]
        return top_k_docs
    


if __name__ == "__main__":
    embedder = OllamaEmbedder()
    docs = ["Prevents unwanted execution", "Ensures code runs only when intended"]
    embeddings = embedder.embed_documents(docs)
    # for i, emb in enumerate(embeddings):
    #     print(f"Document {i} embedding: {emb}")

    similarity = embedder.similarity_search("code execution prevention", docs, k=1)
    print(f"Most similar document: {similarity}")