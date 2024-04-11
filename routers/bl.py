from typing import Annotated, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from dtos.createChatDto import CreateChatDto
from dtos.createIssueDto import CreateIssueDto
from dtos.userDto import UserDto
from services.bl import create_chat, create_issue, get_chats, get_issues, resolve_issue
from services.rag import get_existing_docs, upload_file
from services.user import get_current_active_user
from typing import Annotated
from dtos.userDto import UserDto

router = APIRouter()


@router.get("/issues", tags=["issues"])
async def getIssues(current_user: Annotated[UserDto, Depends(get_current_active_user)]):
  loggedInUser = current_user
  return await get_issues(loggedInUser["_id"])


@router.post("/issues/create", tags=["issues"])
async def createIssue(createIssueDto: CreateIssueDto, current_user: Annotated[UserDto, Depends(get_current_active_user)]):
  loggedInUser = current_user
  data = {
    "title": createIssueDto.title,
    "user_id": loggedInUser["_id"],
    "is_resolved": False,
  }
  return await create_issue(data)


@router.patch("/issues/resolve/{issue_id}", tags=["issues"])
async def resolveIssue(issue_id: str, current_user: Annotated[UserDto, Depends(get_current_active_user)]):
  loggedInUser = current_user
  return await resolve_issue(issue_id, loggedInUser["_id"])


@router.get("/chats/{issue_id}", tags=["chats"])
async def getChats(issue_id: str, current_user: Annotated[UserDto, Depends(get_current_active_user)]):
  loggedInUser = current_user
  return await get_chats(issue_id, loggedInUser["_id"])


@router.get("/collections", tags=["chats"])
async def getCollectionsName(current_user: Annotated[UserDto, Depends(get_current_active_user)]):
  return await get_existing_docs()

# rag 

@router.post("/upload/{collection_name}")
async def uploadFile(current_user: Annotated[UserDto, Depends(get_current_active_user)], file: UploadFile = File(...), collection_name : Optional[str] = "test_collection"):
  return await upload_file(file, collection_name)
