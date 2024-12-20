from langchain_core.tools import tool
from src.rag.main import retriever

genai_docs = "./data_source/generative_ai"
retriever = retriever(data_dir=genai_docs, data_type="pdf")

@tool
def retrieve(query: str):
    """Retrieve information related to a query."""
    retriever_results = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in retriever_results)

@tool
def suggestOKR(query: str):
    """Suggest corresponding OKR and KR."""
    return ""

