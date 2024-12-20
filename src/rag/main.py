from pydantic import BaseModel, Field
from typing import List, Dict
from src.rag.file_loader import Loader
from src.rag.vectorstore import VectorDB
from src.rag.offline_rag import Offline_RAG

class InputQA(BaseModel):
    question: str = Field(..., title="Question to ask the model")
    thread_id: str = Field(..., title="Thread ID")

class OutputQA(BaseModel):
    conversation: List[Dict[str, str]]

def retriever(data_dir, data_type):
    doc_loaded = Loader(file_type=data_type).load_dir(data_dir, workers=2)
    retriever = VectorDB(documents = doc_loaded).get_retriever()

    return retriever

def build_rag_chain(llm, retriever):
    rag_chain = Offline_RAG(llm).get_chain(retriever)

    return rag_chain
