from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from app.db import get_session
from app.schemas.indikator import CreateIndikator
from app.models.indikator import IndikatorCPL
from app.models.cpl import CPL
import re

router = APIRouter(prefix="/indikator", tags=["indikator"])

@router.post("/{id_cpl}", status_code=status.HTTP_201_CREATED)
async def create_indikator(
    id_cpl: str,
    data: CreateIndikator,
    session: Session = Depends(get_session)
):
    cpl = session.exec(
        select(CPL).where(CPL.id_cpl == id_cpl)
    ).first()

    if not cpl:
        raise HTTPException(
            404,
            "CPL tidak ditemukan."
        )
    
    if not data.id_indikator.strip():
        raise HTTPException(400, "id_indikator tidak boleh kosong.")
  
    if not data.deskripsi.strip():
        raise HTTPException(400, "deskripsi tidak boleh kosong.")

    pattern = r"^IND-\d{2}-\d{2}$"
    if not re.match(pattern, data.id_indikator):
        raise HTTPException(
            400,
            "Format id_indikator tidak valid. Gunakan pola 'IND-XX-YY', XX untuk no CPL, YY untuk noo Indikator."
        )
    
    existing_indikator = session.exec(
        select(IndikatorCPL).where(IndikatorCPL.id_indikator == data.id_indikator)
    ).first()

    if existing_indikator:
        raise HTTPException(
            400,
            "id_indikator sudah digunakan. Gunakan id_indikator lain."
        )

    new_indikator = IndikatorCPL(
        id_indikator=data.id_indikator,
        deskripsi=data.deskripsi,
        id_cpl=id_cpl
    )

    session.add(new_indikator)
    session.commit()
    session.refresh(new_indikator)

    return {
        "message": "Indikator CPL berhasil dibuat.",
        "data": new_indikator
    }


@router.delete("/{id_indikator}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteIndikator(id_indikator:str, session: Session = Depends(get_session)):
    indikator = session.get(IndikatorCPL, id_indikator)
    if not indikator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indikator tidak ditemukan")
    
    hapus = delete(IndikatorCPL).where(IndikatorCPL.id_indikator == id_indikator)
    session.exec(hapus)
    session.commit()