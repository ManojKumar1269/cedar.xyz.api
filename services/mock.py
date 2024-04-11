from fastapi import HTTPException
from dtos.createChatDto import CreateChatDto
from dtos.createIssueDto import CreateIssueDto
from dtos.registerDto import RegisterDto
from faker import Faker
from services.bl import create_chat, create_issue  
from services.user import register
from database.mongodb import database

USER_COUNT = 5
ISSUES_COUNT = 5
CHAT_COUNT = 25

fake = Faker()  

async def mock():
  users = await database().get_collection("Users").count_documents({})
  
  if users > 0: 
    raise HTTPException(status_code=500, detail="Database already has data")
  
  for i in range(0, USER_COUNT):
    registerDto: RegisterDto = {
      "email": "user" + str(i) + "@example.com",
      "full_name": fake.name(),
      "password": "password123"
    }
    await register(registerDto)

  users = await database().get_collection("Users").find({}).to_list(1000)

  for u in users:
    for i in range(0, ISSUES_COUNT):
      createIssueDto: CreateIssueDto = {
        "title": fake.sentence(),
        "user_id": str(u["_id"])
      }
      await create_issue(createIssueDto, True)
    
    issues = await database().get_collection("Issues").find({}).to_list(1000)
    for i in issues:
      for c in range(0, fake.random_int(1, CHAT_COUNT)):
        createChatDto: CreateChatDto = {
          "issue_id": str(i["_id"]),
          "user_id": str(u["_id"]),
          "text": fake.sentence(),
          "is_bot": fake.boolean()
        }
        await create_chat(createChatDto, True)

  return {"message": "Mock data created"}


async def clear_db():
  await database().get_collection("Users").delete_many({})
  await database().get_collection("Issues").delete_many({})
  await database().get_collection("Chats").delete_many({})
  return {"message": "Database cleared"}