from datetime import datetime

class UserModel():
    _id: str
    full_name: str
    hashed_password: str
    email: str
    disabled: bool
    last_login: datetime
    created_on: datetime
