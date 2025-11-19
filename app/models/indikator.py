from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .cpl import CPL

class IndikatorCPL(SQLModel, table=True):
    __tablename__ = "indikator_cpl"

    id_indikator: str = Field(primary_key=True, max_length=50)
    deskripsi: str
    id_cpl: Optional[str] = Field(default=None, foreign_key="cpl.id_cpl", max_length=50)
    
    cpl: Optional["CPL"] = Relationship(back_populates="indikator_list")