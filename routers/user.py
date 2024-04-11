from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from dtos.loginDto import LoginDto
from dtos.userDto import UserDto
from services.user import get_current_active_user, register, get_user, login
from dtos.registerDto import RegisterDto
from services.user import get_current_active_user

router = APIRouter()

@router.post("/users/login", tags=["users"])
async def loginUser(loginDto: LoginDto):
    return await login(loginDto)


@router.post("/token")
async def loginUser(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    loginData = await login(LoginDto(email=form_data.username, password=form_data.password))
    return {"access_token": loginData["access_token"], "token_type": "bearer"}


@router.get("/users/get", tags=["users"])
async def getUser(current_user: Annotated[UserDto, Depends(get_current_active_user)]):
    return await get_user(current_user["_id"])


@router.post("/users/register", tags=["users"])
async def registerUser(registerDto: RegisterDto):
    return await register(registerDto)