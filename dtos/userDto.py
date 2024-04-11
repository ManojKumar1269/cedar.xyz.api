from datetime import datetime
from pydantic import BaseModel

class UserDto(BaseModel):
    _id: str
    full_name: str
    email: str
    disabled: bool
    last_login: datetime
    created_on: datetime
    access_token: str
    access_token_expires: datetime
