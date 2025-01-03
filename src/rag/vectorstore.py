from typing import Union
# from langchain_chroma import Chroma
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS
from src.base.llm_model import get_model_embedding

class VectorDB:
    def __init__(self,
                documents = None,
                vector_db: Union[Chroma, FAISS] = Chroma,
                embedding=None
                ) -> None:
        self.embedding = embedding or get_model_embedding()
        self.vector_db = vector_db
        self.db = self._build_db(documents)

    def _build_db(self, documents):
        db = self.vector_db.from_documents(documents=documents, embedding=self.embedding)

        return db

    def get_retriever(self,
                    search_type: str = "similarity",
                    search_kwargs: dict = {"k": 3}
                    ):
        retriever = self.db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

        return retriever
