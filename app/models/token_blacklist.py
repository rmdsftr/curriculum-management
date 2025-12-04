from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
import uuid

class TokenBlacklist(SQLModel, table=True):
    __tablename__ = "token_blacklist"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    token: str = Field(index=True, unique=True)
    blacklisted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime  
    user_id: str = Field(foreign_key="users.user_id", max_length=25)