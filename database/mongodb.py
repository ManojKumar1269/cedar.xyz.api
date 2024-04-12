import motor.motor_asyncio
from common.function import PRODUCTION

MONGO_SERVER = "mongodb+srv://mongocluster:EDIH%40123@edihmongo.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000" if PRODUCTION else "mongodb://localhost:27017"

def database():
  client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_SERVER)
  return client.get_database("xzy_customer_portal_db")
