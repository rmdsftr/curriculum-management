from sqlmodel import SQLModel, Field
from pydantic import field_validator
from typing import List, Optional
import datetime
import uuid

class CPLInput(SQLModel):
    id_kurikulum: uuid.UUID
    id_cpl: str


class createMatkul(SQLModel):
    id_matkul: str
    mata_kuliah: str
    sks: int
    semester: int
    cpl_list: List[CPLInput]  

    @field_validator("id_matkul", mode="before")
    def uppercase_id_matkul(cls, v):
        return v.upper()
    
    @field_validator("cpl_list", mode="before")
    def uppercase_id_cpls(cls, v):
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and 'id_cpl' in item:
                    item['id_cpl'] = item['id_cpl'].upper()
        return v


class updateMatkul(SQLModel):
    mata_kuliah: Optional[str] = None
    sks: Optional[int] = None
    semester: Optional[int] = None
    cpl_list: Optional[List[CPLInput]] = None  

    @field_validator("cpl_list", mode="before")
    def uppercase_id_cpls(cls, v):
        if v is not None and isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and 'id_cpl' in item:
                    item['id_cpl'] = item['id_cpl'].upper()
        return v