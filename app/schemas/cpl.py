from sqlmodel import SQLModel

class CreateCPL(SQLModel):
    id_cpl: str
    deskripsi: str

class UpdateCPL(SQLModel):
    deskripsi: str

  
    