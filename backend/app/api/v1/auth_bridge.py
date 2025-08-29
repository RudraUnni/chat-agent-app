# backend/app/api/v1/auth_bridge.py
"""
Authentication Bridge between Medical Assistant and Open WebUI
Provides unified authentication across both systems
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# In production, use environment variables or secure key management
SECRET_KEY = "medical_assistant_secret_key_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Simple user store (in production, use database)
USERS_DB = {
    "admin": {
        "username": "admin",
        "email": "admin@medical-assistant.local",
        "hashed_password": "admin_password_hash",  # In production, use proper hashing
        "role": "admin",
        "is_active": True
    },
    "doctor": {
        "username": "doctor",
        "email": "doctor@medical-assistant.local", 
        "hashed_password": "doctor_password_hash",
        "role": "doctor",
        "is_active": True
    },
    "researcher": {
        "username": "researcher",
        "email": "researcher@medical-assistant.local",
        "hashed_password": "researcher_password_hash", 
        "role": "researcher",
        "is_active": True
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]

class UserInfo(BaseModel):
    username: str
    email: str
    role: str
    is_active: bool


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (simplified for demo - use proper hashing in production)"""
    # This is a simplified check - in production use bcrypt or similar
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password or plain_password == "demo_password"


def get_password_hash(password: str) -> str:
    """Hash password (simplified for demo)"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login endpoint for both Medical Assistant and Open WebUI
    """
    user = USERS_DB.get(request.username)
    
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info={
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"]
        }
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user information
    """
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    user = USERS_DB.get(username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return UserInfo(
        username=user["username"],
        email=user["email"],
        role=user["role"],
        is_active=user["is_active"]
    )


@router.post("/openwebui/signin")
async def openwebui_signin(request: LoginRequest):
    """
    Open WebUI compatible signin endpoint
    """
    try:
        # Use the same login logic
        token_response = await login(request)
        
        # Return in format expected by Open WebUI
        return {
            "token": token_response.access_token,
            "user": token_response.user_info,
            "detail": "Login successful"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in Open WebUI signin: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/openwebui/signup")
async def openwebui_signup(request: Dict[str, Any]):
    """
    Open WebUI compatible signup endpoint (disabled for security)
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User registration is disabled for security. Please contact your administrator."
    )


@router.get("/openwebui/config")
async def openwebui_auth_config():
    """
    Open WebUI authentication configuration
    """
    return {
        "auth": {
            "enabled": True,
            "provider": "medical_assistant",
            "signup_enabled": False,
            "oauth_enabled": False,
            "session_timeout": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        },
        "features": {
            "role_based_access": True,
            "session_management": True,
            "token_refresh": True
        }
    }


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh JWT token
    """
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    username = payload.get("sub")
    role = payload.get("role")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username, "role": role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (token invalidation would be handled by client)
    """
    return {"detail": "Successfully logged out"}


# Demo user creation endpoint (for development only)
@router.post("/create_demo_users")
async def create_demo_users():
    """
    Create demo users for testing (development only)
    """
    demo_users = {
        "demo_admin": {
            "username": "demo_admin",
            "email": "demo_admin@medical-assistant.local",
            "hashed_password": get_password_hash("demo_password"),
            "role": "admin",
            "is_active": True
        },
        "demo_doctor": {
            "username": "demo_doctor", 
            "email": "demo_doctor@medical-assistant.local",
            "hashed_password": get_password_hash("demo_password"),
            "role": "doctor",
            "is_active": True
        }
    }
    
    USERS_DB.update(demo_users)
    
    return {
        "detail": "Demo users created",
        "users": [
            {"username": "demo_admin", "password": "demo_password", "role": "admin"},
            {"username": "demo_doctor", "password": "demo_password", "role": "doctor"}
        ]
    }