import os
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

class Embedder:
    def __init__(self):
        self.model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.device = "cpu"

    def get_embeddings(self):
        return HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={'device': self.device}
        )