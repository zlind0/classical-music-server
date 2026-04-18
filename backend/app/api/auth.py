from fastapi import APIRouter, HTTPException, Depends, Form, Header
from datetime import datetime, timedelta
import jwt
from typing import Optional
from app.core.config import settings

router = APIRouter()

# Mock user database for now
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user": {"password": "user123", "role": "user"},
}

def create_token(data: dict, expires_delta: timedelta = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

@router.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login endpoint - returns JWT token"""

    # Verify user credentials
    if username not in USERS or USERS[username]["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token
    access_token = create_token(
        data={
            "sub": username,
            "role": USERS[username]["role"],
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": username,
            "role": USERS[username]["role"],
        }
    }

@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user info"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        role = payload.get("role")

        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "username": username,
            "role": role,
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

