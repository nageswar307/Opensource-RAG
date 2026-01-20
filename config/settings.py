import os
from dataclasses import dataclass
from dotenv import load_dotenv
import params


load_dotenv()

@dataclass(frozen=True)
class Settings:
    EMBEDDING_MODEL :  str  = params.EMBEDDING_MODEL

    CHUNK_SIZE : int = params.CHUNK_SIZE
    CHUNK_OVERLAP : int = params.CHUNK_OVERLAP

    DATA_FOLDER : str = params.DATA_FOLDER


