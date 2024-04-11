from datetime import datetime


class ChatModel():
  _id: str
  issue_id: str
  user_id: str
  is_bot: bool
  text: str
  created_on: datetime
