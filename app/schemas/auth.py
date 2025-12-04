from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    user_id: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    user_id: str
    nama: str
    role: str
    created_at: datetime
    updated_at: datetime

class TokenData(BaseModel):
    user_id: Optional[str] = None
    nama: Optional[str] = None
    role: Optional[str] = None