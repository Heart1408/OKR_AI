import os

from fastapi import FastAPI, APIRouter, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# from langserve import add_routes

from src.auth.authencation_middleware import validate_token
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

@app.middleware("http")
async def check_authen(request: Request, call_next):
    
    token = (request.headers.get('Authorization') or "Bearer").split('Bearer')
    authen_check_routes = ['/generative_ai', '/analysis']
    if(request.url.path not in authen_check_routes):
        response = await call_next(request)
        return response
    final_token = None
    if(len(token) > 1):
        final_token = token[1]
    check_flag = validate_token(token=final_token)
    if check_flag['status'] is True:
        response = await call_next(request)
        return response
    else:
        return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"},
                content={
                         "code": status.HTTP_401_UNAUTHORIZED,
                         "message": check_flag['message']}
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
