
import hashlib
import json
import uuid
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangChainDocument


def stable_chunk_id(
    doc_id: str, chunk_index: int, content: str, metadata: dict | None
) -> str:
    payload = {
        "doc_id": doc_id,
        "chunk_index": chunk_index,
        "content": content,
        "metadata": metadata or {},
    }
    payload_json = json.dumps(payload, sort_keys=True, default=str)
    content_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()[:16]
    base = f"chunk::{doc_id}::{chunk_index}::{content_hash}"
    
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))



class Chunker:

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )


    def chunk_document(self, document: LangChainDocument) -> List[LangChainDocument]:
        chunks = self.text_splitter.split_text(document.page_content)
        chunked_documents = []
        for i, chunk in enumerate(chunks):
            chunk_id = stable_chunk_id(
                document.metadata.get("doc_id", "unknown_doc"),
                i,
                chunk,
                document.metadata,
            )
            chunk_metadata = document.metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_id": chunk_id,
            })
            chunked_documents.append(
                LangChainDocument(
                    page_content=chunk,
                    metadata=chunk_metadata
                )
            )
        return chunked_documents
