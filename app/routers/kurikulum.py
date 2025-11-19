from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from datetime import datetime
from sqlalchemy.orm import selectinload
import uuid
from app.utils.current_datetime import timestamp_now


from app.db import get_session
from app.models.kurikulum import Kurikulum
from app.models.cpl import CPL
from app.schemas.kurikulum import KurikulumCreate, KurikulumUpdate, CPLRead

router = APIRouter(prefix="/kurikulum", tags=["kurikulum"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_kurikulum(data: KurikulumCreate, session: Session = Depends(get_session)):

    # Validasi status_kurikulum
    if data.status_kurikulum not in ["aktif", "nonaktif"]:
        raise HTTPException(
            status_code=400,
            detail="status_kurikulum harus 'aktif' atau 'nonaktif'"
        )

    # Cek nama kurikulum sudah ada
    exist = session.exec(
        select(Kurikulum).where(Kurikulum.nama_kurikulum == data.nama_kurikulum)
    ).first()

    if exist:
        raise HTTPException(status_code=400, detail="Nama kurikulum sudah ada.")

    # Buat objek baru
    new_item = Kurikulum(
        nama_kurikulum=data.nama_kurikulum,
        revisi=data.revisi,
        status_kurikulum=data.status_kurikulum,
    )

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    return {
        "message": "Berhasil menambahkan kurikulum",
        "kurikulum": {
            "id_kurikulum": str(new_item.id_kurikulum),
            "nama_kurikulum": new_item.nama_kurikulum,
            "revisi": new_item.revisi,
            "status_kurikulum": new_item.status_kurikulum
        }
    }

# GET ALL
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(session: Session = Depends(get_session)):
    data = session.exec(select(Kurikulum)).all()

    return {"total": len(data), "data": data}



# UPDATE
@router.patch("/{id_kurikulum}", status_code=status.HTTP_200_OK)
async def update_kurikulum(id_kurikulum: str, data: KurikulumUpdate,
                           session: Session = Depends(get_session)):

    item = session.get(Kurikulum, id_kurikulum)

    if not item:
        raise HTTPException(status_code=404, detail="Kurikulum tidak ditemukan.")

    updates = data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(item, key, value)

    item.updated_at = timestamp_now()
    session.add(item)
    session.commit()
    session.refresh(item)

    return {"message": "Berhasil memperbarui kurikulum", "kurikulum": item}



# DETAIL
@router.get("/{id_kurikulum}", status_code=200)
async def detail_kurikulum(id_kurikulum: str, session: Session = Depends(get_session)):

    try :
        uuid_obj = uuid.UUID(id_kurikulum)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Kurikulum tidak valid")
    # Pakai selectinload supaya relasi cpl_list sudah dimuat
    item = session.exec(
        select(Kurikulum)
        .where(Kurikulum.id_kurikulum == id_kurikulum)
        .options(selectinload(Kurikulum.cpl_list))
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Kurikulum tidak ditemukan")

    # Gunakan cpl_list sesuai nama attribute di model
    cpl_list = [
        CPLRead(id_cpl=c.id_cpl, deskripsi=c.deskripsi)
        for c in item.cpl_list
    ]

    return {
        "kurikulum": {
            "id_kurikulum": item.id_kurikulum,
            "nama_kurikulum": item.nama_kurikulum,
            "revisi": item.revisi,
            "status_kurikulum": item.status_kurikulum,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "cpl": cpl_list
        }
    }



# DELETE
@router.delete("/{id_kurikulum}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kurikulum(id_kurikulum: str, session: Session = Depends(get_session)):
    item = session.get(Kurikulum, id_kurikulum)
    if not item:
        raise HTTPException(status_code=404, detail="Kurikulum tidak ditemukan")

    session.delete(item)
    session.commit()
    return
