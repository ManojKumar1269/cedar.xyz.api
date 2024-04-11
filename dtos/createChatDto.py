from pydantic import BaseModel


class CreateChatDto(BaseModel):
  issue_id: str
  user_id: str
  is_bot: bool
  text: str
  collection_name: str
  isOpenAI: bool
    
