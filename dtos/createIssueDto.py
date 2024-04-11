
from pydantic import BaseModel


class CreateIssueDto(BaseModel):
  title: str
  user_id: str
    
