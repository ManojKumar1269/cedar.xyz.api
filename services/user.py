from datetime import datetime, timedelta, timezone
from typing import Annotated
from jose import JWTError, jwt
from database.mongodb import database
from dtos.registerDto import RegisterDto
from dtos.userDto import UserDto
from dtos.loginDto import LoginDto
from models.userModel import UserModel
from bson import ObjectId
from common.function import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, decode_userId, oauth2_scheme, pwd_context
from fastapi import Depends, HTTPException

from services.bl import create_issue


async def register(registerDto: RegisterDto):
  userModel : UserModel = {
    "full_name": registerDto.full_name,
    "hashed_password": pwd_context.hash(registerDto.password),
    "email": registerDto.email,
    "disabled": False,
    "last_login": None,
    "created_on": datetime.utcnow()
  }

  existingEmail = await database().get_collection("Users").find_one({"email": registerDto.email })

  if existingEmail is not None:
    return "Email already exists."
  
  newModel = await database().get_collection("Users").insert_one(userModel)
  issue = {
    "title": "Welcome to the app",
    "user_id": str(newModel.inserted_id),
  }
  
  await create_issue(issue)

  return str(newModel.inserted_id)


async def get_user(id: str | None):
  userModel = await database().get_collection("Users").find_one({"_id": ObjectId(id) })

  if userModel is None:
    raise HTTPException(status_code=500, detail="user does not exist")
  
  userDto: UserDto = {
    "_id": str(userModel["_id"]),
    "full_name": userModel["full_name"],
    "email": userModel["email"],
    "disabled": userModel["disabled"],
    "last_login": userModel["last_login"],
    "created_on": userModel["created_on"]
  }
  return userDto


async def login(loginDto: LoginDto):
  userModel = await database().get_collection("Users").find_one({ "email": loginDto.email })

  if userModel is None:
    raise HTTPException(status_code=500, detail="username or password is incorrect")
  
  passwordHash = pwd_context.verify(loginDto.password, userModel["hashed_password"])

  if (passwordHash is False):
    raise HTTPException(status_code=500, detail="username or password is incorrect")

  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
      data={"sub": str(userModel["_id"])}, expires_delta=access_token_expires
  )
  result = await get_user(str(userModel["_id"]))
  result["access_token"] = access_token
  result["access_token_expires"] = datetime.utcnow() + access_token_expires
  return result


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  to_encode = data.copy()
  if expires_delta:
      expire = datetime.now(timezone.utc) + expires_delta
  else:
      expire = datetime.now(timezone.utc) + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  return encoded_jwt


async def get_current_active_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(user_id)
    if user is None:
        raise credentials_exception
    return user