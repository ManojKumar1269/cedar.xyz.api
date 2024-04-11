from datetime import datetime

class IssueModel():
  _id: str
  user_id: str
  title: str
  is_resolved: bool
  resolved_on: datetime
  created_on: datetime
