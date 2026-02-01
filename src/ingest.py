

from src.document_loader import DocumentLoader, DoclingLoadConfig
from src.chunker import Chunker
from src.embedder import OllamaEmbedder
from src.vector_store import PGVectorStore
from config.settings import settings


def ingest_documents(folder_path: str) -> None:
    # Load documents
    load_config = DoclingLoadConfig()
    loader = DocumentLoader(load_config)
    documents = loader.load_folder(folder_path)

    # Chunk documents
    chunker = Chunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    chunked_documents = chunker.chunk_documents(documents)
    print(f"Total chunks created: {len(chunked_documents)}")

    # Embed chunks
    embedder = OllamaEmbedder(model_name=settings.EMBEDDING_MODEL)
    embeddings = embedder.embed_documents(chunked_documents)
    print(f"Total embeddings created: {len(embeddings)}")

    # Store in vector database
    vector_store = PGVectorStore()
    vector_store.ensure_schema(embedding_dim=embedder.embedding_dimension)
    vector_store.insert_embedding(chunked_documents, embeddings)
    vector_store.create_index(lists=100)

if __name__ == "__main__":
    ingest_documents(settings.DATA_FOLDER)
