import os

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
# from langserve import add_routes

from src.base.llm_model import get_llm
from src.rag.main import build_rag_chain, retriever, InputQA, OutputQA
from src.assistant.assistant import assistant
from src.database.main import InputObject, OutputAnalysis, analysis

os.environ["TOKENIZERS_PARALLELISM"] = "false"
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath("gg_authentication.json")

llm = get_llm()
genai_docs = "./data_source/generative_ai"

retriever = retriever(data_dir=genai_docs, data_type="pdf")
genai_chain = build_rag_chain(llm, retriever)
router = APIRouter()
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Simple api with LangChain Server",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/check")
async def check():
    return {"status": "ok"}

@app.post("/generative_ai", response_model=OutputQA)
async def generative_ai(inputs: InputQA):
    conversation = assistant(inputs.question, inputs.thread_id)
    return {"conversation": conversation}

@app.post("/analysis", response_model=OutputAnalysis)
async def analysisonOKR(inputs: InputObject):
    answer = analysis(inputs.object_id)
    return {"answer": answer}
# add_routes(app,
#             genai_chain,
#             playground_type="default",
#             path="/generative_ai")
