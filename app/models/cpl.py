from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .kurikulum import Kurikulum
    from .indikator import IndikatorCPL

class CPL(SQLModel, table=True):
    __tablename__ = "cpl"

    id_cpl: str = Field(primary_key=True, max_length=50)
    deskripsi: str
    id_kurikulum: Optional[uuid.UUID] = Field(default=None, foreign_key="kurikulum.id_kurikulum")
    
    kurikulum: Optional["Kurikulum"] = Relationship(back_populates="cpl_list")
    indikator_list: List["IndikatorCPL"] = Relationship(back_populates="cpl")