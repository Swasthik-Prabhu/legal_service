from fastapi import APIRouter, HTTPException, Depends
from models.user import User, UserUpdate
from services.auth_service import get_current_user
from database import init_db

router = APIRouter()

@router.get("/profile/{username}")
async def get_user_profile(username: str, current_user: User = Depends(get_current_user)):
    await init_db()
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Access denied")

    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.to_dict()

@router.put("/profile/{username}")
async def update_user_profile(username: str, update_data: UserUpdate, current_user: User = Depends(get_current_user)):
    await init_db()
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Access denied")

    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.full_name is not None:
        user.full_name = update_data.full_name

    if update_data.username is not None:
        user.username = update_data.username

    if update_data.experience is not None:
        user.experience = update_data.experience

    if update_data.location is not None:
        user.location = update_data.location

    await user.save()
    return {"message": "Profile updated successfully"}

@router.delete("/profile/{username}")
async def delete_user(username: str, current_user: User = Depends(get_current_user)):
    await init_db()
    if current_user.username != username:
        raise HTTPException(status_code=403, detail="Access denied")

    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user.delete()
    return {"message": "User deleted successfully"}
