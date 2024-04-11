from datetime import datetime
from bson import ObjectId
from faker import Faker
from fastapi import HTTPException
from common.function import OPEN_AI_TOKEN
from dtos.createChatDto import CreateChatDto
from dtos.createIssueDto import CreateIssueDto
from database.mongodb import database
from models import IssueModel
from models.chatModel import ChatModel
import httpx


fake = Faker()  


async def create_issue(createIssueDto: CreateIssueDto):
  issueModel: IssueModel = {
    "title": createIssueDto["title"],
    "user_id": createIssueDto["user_id"],
    "is_resolved": False,
    "resolved_on": None,
    "created_on": datetime.utcnow(),
  }
  issueModelDb = await database().get_collection("Issues").insert_one(issueModel)
  return str(issueModelDb.inserted_id)


async def resolve_issue(issue_id: str, user_id: str):
  issueModelDb = await database().get_collection("Issues").find_one_and_update({"_id": ObjectId(issue_id), "user_id": user_id }, {"$set": {"is_resolved": True, "resolved_on": datetime.utcnow()}})
  return str(issueModelDb["_id"])


async def create_chat(createChatDto: CreateChatDto, isOpenApi: bool):
  issueModel = await database().get_collection("Issues").find_one({"_id": ObjectId(createChatDto["issue_id"]), "user_id": createChatDto["user_id"]})

  if issueModel["user_id"] != createChatDto["user_id"]:
    raise HTTPException(status_code=400, detail="Issue and user do not match")

  chatModel: ChatModel = {
    "issue_id": createChatDto["issue_id"],
    "user_id": createChatDto["user_id"],
    "is_bot": createChatDto["is_bot"],
    "text": createChatDto["text"],
    "created_on": datetime.utcnow()
  }
  await database().get_collection("Chats").insert_one(chatModel)

  if isOpenApi:
    prompt = await openAiPrompt(createChatDto["text"])

    chatModelBot: ChatModel = {
      "issue_id": createChatDto["issue_id"],
      "user_id": createChatDto["user_id"],
      "is_bot": True,
      "text": "Having some problem, Error." if prompt is None else prompt,
      "created_on": datetime.utcnow()
    }
    await database().get_collection("Chats").insert_one(chatModelBot)

  return "chat created"


async def get_chats(issue_id: str, user_id: str):
  chats = await database().get_collection("Chats").find({"issue_id": issue_id, "user_id": user_id}).to_list(1000)
  result = []
  for chat in chats:
    result.append(chat_Mapper(chat))
  return result


async def get_issues(user_id: str):
  issues = await database().get_collection("Issues").find({"user_id": user_id}).to_list(1000)
  result = []
  for issue in issues:
    result.append(issue_Mapper(issue))
  return result


async def openAiPrompt(prompt: str, useMock: bool = False):
  if useMock:
    return fake.sentence() + " " + fake.sentence()
  
  async with httpx.AsyncClient() as client:
    response = await client.post("https://api.openai.com/v1/completions",
                                  headers=httpx.Headers({"Content-Type": "application/json",
                                                          "Authorization": "Bearer " + OPEN_AI_TOKEN}),
                                  json={
                                    "model": "gpt-3.5-turbo-instruct",
                                    "prompt": prompt,
                                    "max_tokens": 100,
                                    "temperature": 0
                                  })
    responseJson = response.json()
    if ("choices" in responseJson and responseJson["choices"][0] is not None and "text" in responseJson["choices"][0]):
      return responseJson["choices"][0]["text"]
    else: 
      return None


# Mapper


def issue_Mapper(issue):
  return {
    "_id": str(issue["_id"]),
    "user_id": issue["user_id"],
    "title": issue["title"],
    "is_resolved": issue["is_resolved"],
    "resolved_on": issue["resolved_on"],
    "created_on": issue["created_on"]
  }


def chat_Mapper(chat):
  return {
    "_id": str(chat["_id"]),
    "issue_id": chat["issue_id"],
    "user_id": chat["user_id"],
    "is_bot": chat["is_bot"],
    "text": chat["text"],
    "created_on": chat["created_on"]
  }