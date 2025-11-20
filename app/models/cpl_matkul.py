from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from typing import TYPE_CHECKING, Optional
import uuid

if TYPE_CHECKING:
    from .cpl import CPL
    from .matkul import MataKuliah

class CPLMataKuliah(SQLModel, table=True):
    __tablename__ = "cpl_matkul"

    id_kurikulum: uuid.UUID = Field()
    id_cpl: str = Field(max_length=50)
    id_matkul: str = Field(max_length=50)

    __table_args__ = (
        PrimaryKeyConstraint("id_kurikulum", "id_cpl", "id_matkul"),
        ForeignKeyConstraint(
            ["id_kurikulum", "id_cpl"],
            ["cpl.id_kurikulum", "cpl.id_cpl"]
        ),
        ForeignKeyConstraint(
            ["id_matkul"],
            ["mata_kuliah.id_matkul"]
        ),
    )

    cpl: Optional["CPL"] = Relationship(back_populates="matkul_list")
    mata_kuliah: Optional["MataKuliah"] = Relationship(back_populates="cpl_list") 