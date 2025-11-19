from sqlmodel import SQLModel

class CreateIndikator(SQLModel):
    id_indikator: str
    deskripsi: str

    