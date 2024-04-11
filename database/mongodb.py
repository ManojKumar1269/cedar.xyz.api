import motor.motor_asyncio
from common.function import PRODUCTION

MONGO_SERVER = "mongodb+srv://manoj_kumar:Password123@cluster0.59iyyti.mongodb.net/" if PRODUCTION else "mongodb://localhost:27017"

def database():
  client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_SERVER)
  return client.get_database("xzy_customer_portal_db")