from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime
from app.models.kurikulum import StatusEnum


# ========== CREATE REQUEST ==========
class KurikulumCreate(SQLModel):
    nama_kurikulum: str
    revisi: Optional[str] = None
    status_kurikulum: StatusEnum = StatusEnum.aktif   # FIX ✔


# ========== UPDATE REQUEST ==========
class KurikulumUpdate(SQLModel):
    nama_kurikulum: Optional[str] = None
    revisi: Optional[str] = None
    status_kurikulum: Optional[StatusEnum] = None


# ========== CPL READ ==========
class CPLRead(SQLModel):
    id_cpl: str
    deskripsi: str


# ========== SINGLE READ ==========
class KurikulumRead(SQLModel):
    id_kurikulum: str
    nama_kurikulum: str
    revisi: Optional[str]
    status_kurikulum: StatusEnum
    created_at: datetime
    updated_at: datetime


# ========== DETAIL READ (WITH CPL) ==========
class KurikulumDetail(SQLModel):
    id_kurikulum: str
    nama_kurikulum: str
    revisi: Optional[str]
    status_kurikulum: StatusEnum
    created_at: datetime
    updated_at: datetime
    cpl: List[CPLRead]
