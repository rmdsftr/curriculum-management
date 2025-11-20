from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
import uuid
from sqlalchemy import PrimaryKeyConstraint

if TYPE_CHECKING:
    from .kurikulum import Kurikulum
    from .indikator import IndikatorCPL
    from .cpl_matkul import CPLMataKuliah

class CPL(SQLModel, table=True):
    __tablename__ = "cpl"

    id_kurikulum: uuid.UUID = Field(
        foreign_key="kurikulum.id_kurikulum"
    )
    id_cpl: str = Field(max_length=50)
    deskripsi: str

    __table_args__ = (
        PrimaryKeyConstraint("id_kurikulum", "id_cpl"),
    )

    kurikulum: Optional["Kurikulum"] = Relationship(back_populates="cpl_list")
    indikator_list: List["IndikatorCPL"] = Relationship(back_populates="cpl")
    matkul_list: List["CPLMataKuliah"] = Relationship(back_populates="cpl")
