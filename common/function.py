from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
import pickle
import yaml
from rag.loadData import initialize_splitter

PRODUCTION = True

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600
VECTOR_DB_MODEL_NAME = "all-MiniLM-L6-v2"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
OPEN_AI_TOKEN =  "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"# "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"

def decode_userId(token: str):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    return username
  except JWTError:
    return None


# responseJson = {
#     "id": "cmpl-8qHS9FSMhQUZyHzP3coM15vBSU7JX",
#     "object": "text_completion",
#     "created": 1707470837,
#     "model": "gpt-3.5-turbo-instruct",
#     "choices": [
#       {
#         "text": "\n\nI"m sorry, I am an AI and cannot physically test things out. Is there something specific you would like me to",
#         "index": 0,
#         "finish_reason": "length"
#       }
#     ],
#     "usage": {
#       "prompt_tokens": 4,
#       "completion_tokens": 25,
#       "total_tokens": 29
#     }
#   }
  

def read_file(file_path):
    with open(file_path, "r") as f:
        data = f.read()
    return data


def load_yml_file(path):
    with open(path, "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

