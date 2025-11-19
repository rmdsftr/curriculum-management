from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .cpl import CPL

class StatusEnum(str, Enum):
    aktif = "aktif"
    nonaktif = "nonaktif"

class Kurikulum(SQLModel, table=True):
    __tablename__ = "kurikulum"

    id_kurikulum: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    nama_kurikulum: str = Field(max_length=255)
    revisi: Optional[str] = Field(default=None, max_length=50)
    status_kurikulum: Optional[StatusEnum] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    cpl_list: List["CPL"] = Relationship(back_populates="kurikulum")