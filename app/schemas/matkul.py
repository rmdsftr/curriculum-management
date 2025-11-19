from sqlmodel import SQLModel, Field
from pydantic import field_validator
from typing import List, Optional
import datetime

class createMatkul(SQLModel):
    id_matkul: str
    mata_kuliah: str
    sks: int
    semester: int
    id_cpl: List[str]  

    @field_validator("id_matkul", mode="before")
    def uppercase_id_matkul(cls, v):
        return v.upper()
    
    @field_validator("id_cpl", mode="before")
    def uppercase_id_cpls(cls, v):
        if isinstance(v, list):
            return [item.upper() for item in v]
        return v
    


class updateMatkul(SQLModel):
    mata_kuliah: Optional[str] = None
    sks: Optional[int] = None
    semester: Optional[int] = None
    id_cpl: Optional[List[str]] = None

    @field_validator("id_cpl", mode="before")
    def uppercase_id_cpls(cls, v):
        if v is not None and isinstance(v, list):  
            return [item.upper() for item in v]
        return v