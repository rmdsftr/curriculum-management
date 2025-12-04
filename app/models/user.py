from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime, timezone

class RoleEnum(str, Enum):
    kadep = "kadep"
    dosen = "dosen"

class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: str = Field(max_length=25, primary_key=True)
    nama: str = Field(max_length=255)
    password: str = Field(max_length=255)  
    role: RoleEnum = Field(sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))