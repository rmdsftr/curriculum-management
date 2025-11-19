from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cpl import CPL
    from .matkul import MataKuliah

class CPLMataKuliah(SQLModel, table=True):
    __tablename__ = "cpl_matkul"

    id_cpl: str = Field(foreign_key="cpl.id_cpl", primary_key=True, max_length=50)
    id_matkul: str = Field(foreign_key="mata_kuliah.id_matkul", primary_key=True, max_length=50)
    
    cpl: Optional["CPL"] = Relationship(back_populates="matkul_list")
    mata_kuliah: Optional["MataKuliah"] = Relationship(back_populates="cpl_list")