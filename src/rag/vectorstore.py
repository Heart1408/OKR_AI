from typing import Union
from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from src.base.llm_model import get_model_embedding
# from vertexai.language_models import TextEmbeddingModel

class VectorDB:
    def __init__(self,
                # documents = None,
                # vector_db: Union[Chroma, FAISS] = Chroma,
                embedding=None
                ) -> None:
        
        # self.embedding = embedding or TextEmbeddingModel.from_pretrained("textembedding-gecko-multilingual@001")
        self.embedding = embedding or get_model_embedding()
        # self.vector_db = vector_db
        # self.db = self._build_db(documents)

    # def _build_db(self, documents):
    #     db = self.vector_db.from_documents(documents=documents, embedding=self.embedding)

    #     return db

    # def get_retriever(self,
    #                 search_type: str = "similarity",
    #                 search_kwargs: dict = {"k": 3}
    #                 ):
    #     retriever = self.db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

    #     return retriever

    def get_retriever(self, 
                    search_type: str = "similarity",
                    search_kwargs: dict = {"k": 3}
                    ):
        vectorstore_path = "../data_source/vector_stores"
        vectorstore = Chroma(
                embedding_function=self.embedding,
                persist_directory=vectorstore_path,
            )
        retriever = vectorstore.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

        return retriever

#------------------------------------------------------------------------------
def create_vectorstore(documents, embedding, persist_directory):
    """Create a vectorstore from the documents."""
    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=persist_directory)

    return db
