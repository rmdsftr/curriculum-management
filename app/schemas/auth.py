from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime
from app.models.user import RoleEnum

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

class RegisterRequest(BaseModel):
    """Schema untuk request registrasi user baru"""
    user_id: str = Field(
        ..., 
        max_length=25,
        description="User ID unik (max 25 karakter)",
        examples=["dosen001", "kadep001"]
    )
    nama: str = Field(
        ..., 
        max_length=255,
        description="Nama lengkap user",
        examples=["Dr. John Doe"]
    )
    password: str = Field(
        ..., 
        min_length=8,
        description="Password minimal 8 karakter",
        examples=["SecurePass123!"]
    )
    role: RoleEnum = Field(
        ...,
        description="Role user dalam sistem"
    )
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validasi format user_id"""
        if not v or v.strip() == "":
            raise ValueError("user_id tidak boleh kosong")
        if len(v) > 25:
            raise ValueError("user_id tidak boleh lebih dari 25 karakter")
        
        if not v.replace("_", "").isalnum():
            raise ValueError("user_id hanya boleh mengandung huruf, angka, dan underscore")
        return v.strip()
    
    @field_validator('nama')
    @classmethod
    def validate_nama(cls, v: str) -> str:
        """Validasi nama"""
        if not v or v.strip() == "":
            raise ValueError("nama tidak boleh kosong")
        if len(v) > 255:
            raise ValueError("nama tidak boleh lebih dari 255 karakter")
        return v.strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validasi password"""
        if len(v) < 8:
            raise ValueError("password minimal 8 karakter")
        return v