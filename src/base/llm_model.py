import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("OPENAI_MODEL") or os.getenv("GOOGLE_MODEL")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL") or os.getenv("GOOGLE_EMBEDDING_MODEL")

def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        llm = ChatOpenAI(model=MODEL, openai_api_key=API_KEY, temperature=0.0)
    else:
        llm = ChatGoogleGenerativeAI(model=MODEL, google_api_key=API_KEY, template=0.0)

    return llm

def get_model_embedding():
    if os.getenv("OPENAI_API_KEY"):
        model = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    else:
        model = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    return model
