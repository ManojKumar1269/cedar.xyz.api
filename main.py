from contextlib import asynccontextmanager
from typing import Optional
from dtos.createChatDto import CreateChatDto
from fastapi import FastAPI, Depends
from rag.loadData import initialize_splitter
from rag.load_llm import load_lamma_cpp
from routers.user import router as userRouter
from routers.bl import router as blRouter
from fastapi.middleware.cors import CORSMiddleware
from services.bl import create_chat, openAiPrompt
from services.mock import clear_db, mock
from common.function import read_file, load_yml_file
import torch
from dtos.userDto import UserDto
from services.rag import create_prompt, get_collections
from typing import Annotated
from services.user import get_current_active_user

# llms

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

ml_models = {}
db_name = {}
model_args = load_yml_file("./rag/llm2config.yml")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    llm = load_lamma_cpp(model_args)
    ml_models["choices"] = llm
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()

app = FastAPI(
    lifespan=lifespan,
    title="XYZ Customer Portal API",
)

origins = [
    "http://localhost:3000",
    "https://green-sand-0980ce503.4.azurestaticapps.net",
    "http://20.82.177.97:3000"    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(userRouter)
app.include_router(blRouter)

@app.get("/")
async def root():
    return {"message": "XZY API!"}


@app.get("/mock")
async def mockData():
    return await mock()


@app.get("/clear-db")
async def clearDatabase(current_user: Annotated[UserDto, Depends(get_current_active_user)]):
    return await clear_db()


@app.get("/promptOpenAI/{prompt_str}")
async def promptOpenAi(prompt_str: str, current_user: Annotated[UserDto, Depends(get_current_active_user)]):
    return await openAiPrompt(prompt_str)


@app.post("/chats/create", tags=["chats"])
async def createChat(createChatDto: CreateChatDto, current_user: Annotated[UserDto, Depends(get_current_active_user)]):
  loggedInUser = current_user
  data = {
    "issue_id": createChatDto.issue_id,
    "user_id": loggedInUser["_id"],
    "is_bot": createChatDto.is_bot,
    "text": createChatDto.text
  }
  await create_chat(data, createChatDto.isOpenAI)
  
  if not createChatDto.isOpenAI:
    prompt = ragPrompt(createChatDto.text, 2, createChatDto.collection_name)
    data = {
    "issue_id": createChatDto.issue_id,
    "user_id": loggedInUser["_id"],
    "is_bot": True,
    "text": prompt["llm_output"]
    }
    await create_chat(data, False)
  return "chat created"	


@app.get("/promptLLM")
def promptLLM(current_user: Annotated[UserDto, Depends(get_current_active_user)], query : str, n_results : Optional[int] = 2, collection_name : Optional[str] = "test_collection"):
    return ragPrompt(query, n_results, collection_name)


def ragPrompt(query : str, n_results : Optional[int] = 2, collection_name : Optional[str] = "test_collection"): 
    collection = get_collections(collection_name)
    results = collection.query(query_texts=[query], n_results = n_results)
    prompt = create_prompt(query, results)
    output = ml_models["choices"](prompt)
    return {f"message": "Query is " + query,
            "relavent_docs" : results,
            "llm_output" : output }
