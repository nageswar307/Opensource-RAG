import os
from dataclasses import dataclass
from dotenv import load_dotenv
import params


load_dotenv()

@dataclass(frozen=True)
class Settings:
    EMBEDDING_MODEL :  str  = params.EMBEDDING_MODEL
    LLM_MODEL : str = params.LLM_MODEL

    CHUNK_SIZE : int = params.CHUNK_SIZE
    CHUNK_OVERLAP : int = params.CHUNK_OVERLAP

    DATA_FOLDER : str = params.DATA_FOLDER

    DB_HOST: str = params.DB_HOST
    DB_PORT: str = params.DB_PORT
    DB_NAME: str = params.DB_NAME
    DB_USER: str = params.DB_USER
    DB_PASSWORD: str = params.DB_PASSWORD


settings = Settings()
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
CHUNK_SIZE = settings.CHUNK_SIZE
CHUNK_OVERLAP = settings.CHUNK_OVERLAP
DATA_FOLDER = settings.DATA_FOLDER

