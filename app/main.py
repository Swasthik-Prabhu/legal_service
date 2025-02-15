from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.notification import router as notification_router
from routes.cases import router as cases_router
from routes.message import router as message_router

# import asyncio
from database import init_db



app = FastAPI()
# async def startup():
#     await init_db()

# asyncio.run(startup())

app.include_router(auth_router, tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["User Management"])
app.include_router(cases_router, prefix="/cases", tags=["Case Management"])
app.include_router(notification_router, tags=["Notifications"])
app.include_router(message_router, tags=["Messages"])



@app.get("/")
def read_root():
    return {"message": "Welcome to the Legal Aid Platform"}
