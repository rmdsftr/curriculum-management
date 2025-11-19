from sqlmodel import SQLModel
from app.models.user import RoleEnum
from typing import Optional

class CreateUser(SQLModel):
    name:str
    role: RoleEnum

class UpdateUser(SQLModel):
    name: Optional[str]
    role: Optional[RoleEnum]
