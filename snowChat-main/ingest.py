import streamlit as st

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader
from supabase.client import Client, create_client
from typing import Any, Dict
from pydantic import BaseModel

class Secrets(BaseModel):
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    OPENAI_API_KEY: str

class Config(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 0
    docs_dir: str = "docs/"
    docs_glob: str = "**/*.md"

class DocumentProcessor:
    def __init__(self, secrets: Secrets, config: Config):
        self.client: Client = create_client(
            secrets.SUPABASE_URL, secrets.SUPABASE_SERVICE_KEY
        )
        self.loader = DirectoryLoader(config.docs_dir, glob=config.docs_glob)
        self.text_splitter = CharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=secrets.OPENAI_API_KEY)

    def process(self) -> Dict[str, Any]:
        data = self.loader.load()
        texts = self.text_splitter.split_documents(data)
        vector_store = SupabaseVectorStore.from_documents(
            texts, self.embeddings, client=self.client
        )
        return vector_store

def run():
    secrets = Secrets(
        SUPABASE_URL="https://iswyfnwvskzdzhjezptr.supabase.co",
        SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlzd3lmbnd2c2t6ZHpoamV6cHRyIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTExNDI0ODYsImV4cCI6MjAwNjcxODQ4Nn0.BcEA4GDQbyJ_d5dvm-o_aF8b2Amdd2Xexw3RKzDjR9s",
        OPENAI_API_KEY="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",
    )
    config = Config()
    doc_processor = DocumentProcessor(secrets, config)
    result = doc_processor.process()
    return result


if __name__ == "__main__":
    run()
