
from typing import List,Optional
from pathlib import Path
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType

from langchain_core.documents import Document as LangChainDocument

from docling.document_converter import DocumentConverter
from dataclasses import dataclass

import uuid


@dataclass
class DoclingLoadConfig:
    export_type: ExportType = ExportType.DOC_CHUNKS
    chunker: Optional[object] = None
    meta_extractor: Optional[object] = None
    allow_external_plugins: bool = False


class DocumentLoader:
    """given a source path creates citation ready documents"""

    def __init__(self, config: Optional[DoclingLoadConfig] = None):
        self.config = config or DoclingLoadConfig()


    def stable_doc_id(self,file_path: str) -> str:
        base = f"doc::{file_path}"
        return str(uuid.uuid5(uuid.NAMESPACE_URL,base))



    def build_loader(self,file_paths:List[str]) -> DoclingLoader :

        converter = None
        if self.config.allow_external_plugins:
            converter = DocumentConverter()
            for option in converter.format_to_options.values():
                if option.pipeline_options is not None:
                    option.pipeline_options.allow_external_plugins = True

        kwargs = {"file_path": file_paths,
                  "export_type": self.config.export_type,
                  }
        if converter is not None:
            kwargs["converter"] = converter
        if self.config.chunker is not None:
            kwargs["chunker"] = self.config.chunker

        if self.config.meta_extractor is not None:
            kwargs["meta_extractor"] = self.config.meta_extractor

        return DoclingLoader(**kwargs)
    

    def load_folder(self,folder_path: str) -> List[LangChainDocument]:

        folder = Path(folder_path)

        if not folder.exists():
            raise FileNotFoundError(f"Folder not found at {folder_path}")
        
        file_paths = [str(path) for path in folder.rglob("*") if path.is_file()]

        # filepaths= ["data/Example1.pdf", "data/Example2.docx"]

        if not file_paths:
            print("issue with filepaths")
            return []


        loader = self.build_loader(file_paths)

        docs: List[LangChainDocument] = loader.load()

        print(f"Loaded {len(docs)} documents from {folder_path}")
        # print(docs[0])

        docs_with_metadata : List[LangChainDocument] = []
        for i,d in enumerate(docs):
            metadata = d.metadata or {}
            file_path = metadata.get("source",f"unknown_source_{i}")
            file_name = Path(file_path).name
            metadata.update({"filename":file_name})

            stable_id = self.stable_doc_id(file_path)
            metadata.update({"doc_id": stable_id})

            docs_with_metadata.append(
                LangChainDocument(
                    page_content=d.page_content,
                    metadata=metadata
                )
            )
            if (i + 1) % 25 == 0 or (i + 1) == len(docs):
                print(f"Processed {i+1}/{len(docs)} documents")
            

        return docs_with_metadata
            

        
        

if __name__ == "__main__":
    docling_config = DoclingLoadConfig(allow_external_plugins=True)
    docloader = DocumentLoader(docling_config)
    docloader.load_folder("data")




        
