
from atexit import register
from config.settings import settings
import psycopg
from pgvector.psycopg import register_vector
from typing import Sequence,List
from langchain_core.documents import Document as LangChainDocument

class PGVectorStore:
    def __init__(self) -> None:
        self.dsn = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


    def _connect(self,ensure_extensions: bool = False, register: bool = True):

        conn = psycopg.connect(self.dsn)
        if ensure_extensions:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        if register:
            register_vector(conn)
        return conn
    
    def ensure_schema(self,embedding_dim: int):
        with self._connect(ensure_extensions=True) as conn:
            conn.execute(f"""
            CREATE TABLE IF NOT EXISTS embeddings (
                id BIGSERIAL PRIMARY KEY,
                doc_id TEXT,
                chunk_id UUID,
                chunk_index INTEGER,
                source TEXT,
                filename TEXT,
                content TEXT,
                metadata JSONB,
                embedding VECTOR({embedding_dim}),
                content TEXT
            );
            """)

    def create_index(self,lists: int | None = None) -> None:
        with self._connect() as conn:
            if lists is None:
                conn.execute("""
                CREATE INDEX rag_chunks_embeddings_ivfflat ON rag_chunks USING ivfflat (embedding vector_cosine_ops);
                """)
            else:
                conn.execute(f"""
                CREATE INDEX rag_chunks_embeddings_ivfflat ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = {lists});
                """)

            conn.execute("""
            ANALYZE rag_chunks;
            """)

    


    def insert_embedding(self, chunks: Sequence[LangChainDocument], embeddings : Sequence[List[float]]) -> None:

        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must be the same.")
        
        
        rows = []        
        for chunk, embedding in zip(chunks, embeddings):

                metadata = chunk.metadata or {}

                rows.append((
                    chunk.metadata.get("doc_id"),
                    chunk.metadata.get("chunk_id"),
                    chunk.metadata.get("chunk_index"),
                    chunk.metadata.get("source"),
                    chunk.metadata.get("filename"),
                    chunk.page_content,
                    psycopg.Json({k: v for k, v in chunk.metadata.items() if k != "doc_id" and k != "chunk_id" and k != "chunk_index" and k != "source" and k != "filename"}),
                    embedding
                ))
                sql = """ 
                        INSERT INTO rag_chunks (
                        doc_id, 
                        chunk_id, 
                        chunk_index, 
                        source, 
                        filename, 
                        content, 
                        metadata, 
                        embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.executemany(sql, rows)



    def search(self, query_embedding: List[float], top_k: int = 5) -> List[LangChainDocument]:
        
        sql = """
        SELECT doc_id, 
        chunk_id, 
        chunk_index, 
        source, 
        filename, 
        content, 
        metadata, 
        embedding <==> %s::vector AS distance
        FROM rag_chunks
        ORDER BY embedding <==> %s::vector
        LIMIT %s;
        """

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (query_embedding, top_k))
                results = cur.fetchall()
                
                print(f"Search returned {len(results)} results.")
                print(f"Results: {results}")

                documents = []
                for row in results:
                    documents.append(
                        {   
                            "doc_id": row[0],
                            "chunk_id": row[1],
                            "chunk_index": row[2],
                            "source": row[3],
                            "filename": row[4],
                            "page_content": row[5],
                            "metadata": row[6],
                            "distance": row[7]
                        }
                    )
                return documents



