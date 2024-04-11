
from pydantic import BaseModel


class RegisterDto(BaseModel):
    email: str 
    full_name: str | None = None
    password: str
    
