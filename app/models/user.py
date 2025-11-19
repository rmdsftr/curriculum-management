from sqlmodel import SQLModel, Field
from enum import Enum
import uuid

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"

class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: uuid.UUID = Field(
        default_factory= uuid.uuid4,
        primary_key=True,
        index=True
    )
    name: str
    role: RoleEnum