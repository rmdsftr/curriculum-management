from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
import uuid
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint

if TYPE_CHECKING:
    from .cpl import CPL

class IndikatorCPL(SQLModel, table=True):
    __tablename__ = "indikator_cpl"

    id_kurikulum: uuid.UUID = Field()
    id_cpl: str = Field(max_length=50)
    id_indikator: str = Field(max_length=50)
    deskripsi: str

    __table_args__ = (
        PrimaryKeyConstraint("id_kurikulum", "id_cpl", "id_indikator"),
        ForeignKeyConstraint(
            ["id_kurikulum", "id_cpl"],
            ["cpl.id_kurikulum", "cpl.id_cpl"]
        ),
    )

    cpl: Optional["CPL"] = Relationship(back_populates="indikator_list")
