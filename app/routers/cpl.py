from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db import get_session
from app.schemas.cpl import CreateCPL, UpdateCPL
from app.models.cpl import CPL
from app.models.kurikulum import Kurikulum
from app.models.indikator import IndikatorCPL
from app.models.cpl_matkul import CPLMataKuliah
from app.models.matkul import MataKuliah
import re
import uuid

router = APIRouter(prefix="/cpl", tags=["cpl"])

@router.post("/{id_kurikulum}", status_code=status.HTTP_201_CREATED)
async def create_cpl(
    id_kurikulum: uuid.UUID,
    data: CreateCPL,
    session: Session = Depends(get_session)
):    
    kurikulum = session.exec(
        select(Kurikulum).where(Kurikulum.id_kurikulum == id_kurikulum)
    ).first()

    if not kurikulum:
        raise HTTPException(404,"Kurikulum tidak ditemukan.")
    
    if not data.id_cpl.strip():
        raise HTTPException(400, "id_cpl tidak boleh kosong.")
    
    pattern = r"^CPL-\d{2}$"
    if not re.match(pattern, data.id_cpl):
        raise HTTPException(400,"Format id_cpl tidak valid. Gunakan pola 'CPL-XX' (dua digit).")

    existing_cpl = session.exec(
        select(CPL).where((CPL.id_cpl == data.id_cpl) & (CPL.id_kurikulum == id_kurikulum))
    ).first()

    if existing_cpl:
        raise HTTPException(400,"id_cpl sudah digunakan. Gunakan id_cpl lain.")
  
    if not data.deskripsi.strip():
        raise HTTPException(400, "deskripsi tidak boleh kosong.")

    new_cpl = CPL(
        id_cpl=data.id_cpl,
        deskripsi=data.deskripsi,
        id_kurikulum=id_kurikulum
    )

    session.add(new_cpl)
    session.commit()
    session.refresh(new_cpl)

    return {
        "message": "Berhasil menambahkan CPL",
        "cpl": new_cpl
    }

@router.get("/{id_kurikulum}/{id_cpl}", status_code=status.HTTP_200_OK)
async def get_detail_cpl(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    session: Session = Depends(get_session) 
):   
    cpl = session.exec(
        select(CPL).where((CPL.id_kurikulum == id_kurikulum) & (CPL.id_cpl == id_cpl))
    ).first()

    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan.")
    
    kurikulum = session.get(Kurikulum, cpl.id_kurikulum)

    indikator_list = session.exec(
        select(IndikatorCPL).where(IndikatorCPL.id_cpl == id_cpl)
    ).all()

    relasi = session.exec(
        select(CPLMataKuliah).where(CPLMataKuliah.id_cpl == id_cpl)
    ).all()

    id_matkul_list = [r.id_matkul for r in relasi]

    matkul_list = []
    if id_matkul_list:
        matkul_list = session.exec(
            select(MataKuliah).where(MataKuliah.id_matkul.in_(id_matkul_list))
        ).all()

    return {
        "cpl": {
            "id_cpl": cpl.id_cpl,
            "deskripsi": cpl.deskripsi,
        },
        "kurikulum": {
            "id_kurikulum": kurikulum.id_kurikulum,
            "nama_kurikulum": kurikulum.nama_kurikulum,
            "revisi": kurikulum.revisi
        } if kurikulum else None,
        "indikator": [
            {
                "id_indikator": i.id_indikator,
                "deskripsi": i.deskripsi
            }
            for i in indikator_list
        ],
        "mata_kuliah": [
            {
                "id_matkul": m.id_matkul,
                "mata_kuliah": m.mata_kuliah,
                "sks": m.sks,
                "semester": m.semester
            }
            for m in matkul_list
        ]
    }


@router.patch("/{id_kurikulum}/{id_cpl}", status_code=status.HTTP_200_OK)
async def update_cpl(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    data: UpdateCPL,
    session: Session = Depends(get_session)
):   
    cpl = session.exec(
        select(CPL).where((CPL.id_kurikulum == id_kurikulum) & (CPL.id_cpl == id_cpl))
    ).first()

    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan.")

    if data.deskripsi is not None:
        if not data.deskripsi.strip():
            raise HTTPException(400, "deskripsi tidak boleh kosong.")
        cpl.deskripsi = data.deskripsi

    session.add(cpl)
    session.commit()
    session.refresh(cpl)

    return {
        "message": "Berhasil memperbarui CPL",
        "cpl": cpl
    }

@router.delete("/{id_kurikulum}/{id_cpl}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cpl(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    session: Session = Depends(get_session)
):    
    cpl = session.exec(
        select(CPL).where((CPL.id_kurikulum == id_kurikulum) & (CPL.id_cpl == id_cpl))
    ).first()

    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan.")

    session.delete(cpl)
    session.commit()