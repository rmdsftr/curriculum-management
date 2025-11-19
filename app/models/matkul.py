from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .cpl_matkul import CPLMataKuliah

class MataKuliah(SQLModel, table=True):
    __tablename__ = "mata_kuliah"

    id_matkul: str = Field(primary_key=True, max_length=50)
    mata_kuliah: str = Field(max_length=255)
    sks: int
    semester: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    cpl_list: List["CPLMataKuliah"] = Relationship(back_populates="mata_kuliah")