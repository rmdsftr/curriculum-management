from sqlmodel import SQLModel, Field
from typing import Optional

class CreateIndikator(SQLModel):
    id_indikator: str
    deskripsi: str

# ================= UPDATE REQUEST =================
class IndikatorCPLUpdate(SQLModel):
    deskripsi: Optional[str] = None
    id_cpl: Optional[str] = None  # Opsional, kalau mau pindahkan ke CPL lain

