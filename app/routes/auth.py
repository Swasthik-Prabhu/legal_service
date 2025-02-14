from fastapi import APIRouter, HTTPException, Depends, Form
from models.user import User, RoleEnum
from services.auth_service import hash_password, verify_password, create_access_token
from database import init_db
from pydantic import BaseModel
from datetime import timedelta

router = APIRouter()

class RegisterUser(BaseModel):
    full_name: str
    username: str
    password: str
    role: RoleEnum
    experience: int = 0
    location: str = ""

class LoginUser(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register_user(user_data: RegisterUser):
    await init_db()
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        full_name=user_data.full_name,
        username=user_data.username,
        password=hash_password(user_data.password),
        role=user_data.role,
        experience=user_data.experience if user_data.role == "lawyer" else None,
        location=user_data.location
    )
    await user.insert()
    return {"message": "User registered successfully"}

@router.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    await init_db()
    user = await User.find_one(User.username == username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
