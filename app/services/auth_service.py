from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database import init_db
from models.user import User  # Import the User model

SECRET_KEY = "your_secret_key"  # Replace with a secure, environment-stored key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generates a JWT access token with an expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     """Decodes JWT token and retrieves the authenticated user."""
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if not isinstance(username, str):
#             raise HTTPException(status_code=401, detail="Invalid token")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     return username  # Return username to fetch user details in route handlers


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not isinstance(username, str):
            raise HTTPException(status_code=401, detail="Invalid token")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        await init_db()  # Ensure DB is initialized before querying
        user = await User.find_one(User.username == username)  # Fetch full user object
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user  # Return full User object, not just username

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")