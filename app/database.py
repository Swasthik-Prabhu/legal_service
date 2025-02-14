from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models.user import User

MONGO_URI = "mongodb+srv://swasthikp03:swasthik@swasthikprabhu.fabhbaq.mongodb.net/main"

async def init_db():
    client = AsyncIOMotorClient(MONGO_URI)
    database = client.get_database("Legal")  # Explicitly use the "main" database
    await init_beanie(database, document_models=[User])  # Register user model
