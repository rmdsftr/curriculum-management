from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from datetime import datetime
from sqlalchemy.orm import selectinload
import uuid
from app.utils.current_datetime import timestamp_now
from app.utils.auth import require_kadep, require_kadep_or_dosen
from app.db import get_session
from app.models.kurikulum import Kurikulum
from app.models.cpl import CPL
from app.schemas.kurikulum import KurikulumCreate, KurikulumUpdate, CPLRead

router = APIRouter(
    prefix="/kurikulum", 
    tags=["kurikulum"],
    responses={404: {"description": "Tidak ditemukan"}}
)


@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Kurikulum Baru",
    description="Menambahkan kurikulum baru ke dalam sistem",
    response_description="Data kurikulum yang berhasil ditambahkan",
    dependencies=[Depends(require_kadep)]
)
async def create_kurikulum(data: KurikulumCreate, session: Session = Depends(get_session)):
    """
    Menambahkan kurikulum baru ke database.
    
    **Parameter:**
    - **nama_kurikulum**: Nama kurikulum (harus unik)
    - **revisi**: Nomor revisi kurikulum
    - **status_kurikulum**: Status kurikulum ('aktif' atau 'nonaktif')
    
    **Validasi:**
    - Nama kurikulum harus unik
    - Status harus 'aktif' atau 'nonaktif'
    
    **Return:**
    - Message konfirmasi
    - Data kurikulum yang baru dibuat (ID, nama, revisi, status)
    
    **Error:**
    - 400: Nama kurikulum sudah ada atau status tidak valid
    """
    
    if data.status_kurikulum not in ["aktif", "nonaktif"]:
        raise HTTPException(
            status_code=400,
            detail="status_kurikulum harus 'aktif' atau 'nonaktif'"
        )

    exist = session.exec(
        select(Kurikulum).where(Kurikulum.nama_kurikulum == data.nama_kurikulum)
    ).first()

    if exist:
        raise HTTPException(status_code=400, detail="Nama kurikulum sudah ada.")

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


@router.get(
    "/", 
    status_code=status.HTTP_200_OK,
    summary="Daftar Semua Kurikulum",
    description="Mengambil daftar lengkap semua kurikulum yang ada di sistem",
    response_description="Total dan daftar kurikulum",
    dependencies=[Depends(require_kadep_or_dosen)]
)
async def get_all(session: Session = Depends(get_session)):
    """
    Mengambil semua data kurikulum.
    
    **Return:**
    - **total**: Jumlah total kurikulum
    - **data**: Array berisi semua data kurikulum
    
    Setiap kurikulum berisi:
    - id_kurikulum
    - nama_kurikulum
    - revisi
    - status_kurikulum
    - created_at
    - updated_at
    """
    data = session.exec(select(Kurikulum)).all()

    return {"total": len(data), "data": data}


@router.patch(
    "/{id_kurikulum}", 
    status_code=status.HTTP_200_OK,
    summary="Update Kurikulum",
    description="Mengupdate informasi kurikulum yang sudah ada",
    response_description="Data kurikulum yang telah diupdate",
    dependencies=[Depends(require_kadep_or_dosen)]
)
async def update_kurikulum(
    id_kurikulum: str, 
    data: KurikulumUpdate,
    session: Session = Depends(get_session)
):
    """
    Mengupdate data kurikulum yang sudah ada.
    
    **Parameter:**
    - **id_kurikulum**: ID kurikulum yang akan diupdate (UUID format)
    - **nama_kurikulum** (opsional): Nama kurikulum baru
    - **revisi** (opsional): Nomor revisi baru
    - **status_kurikulum** (opsional): Status baru ('aktif' atau 'nonaktif')
    
    **Catatan:**
    - Hanya field yang diisi yang akan diupdate
    - Timestamp updated_at akan otomatis diperbarui
    
    **Return:**
    - Message konfirmasi
    - Data kurikulum lengkap yang telah diupdate
    
    **Error:**
    - 404: Kurikulum tidak ditemukan
    """
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


@router.get(
    "/{id_kurikulum}", 
    status_code=200,
    summary="Detail Kurikulum",
    description="Mengambil detail lengkap kurikulum beserta daftar CPL yang terkait",
    response_description="Data lengkap kurikulum dengan CPL",
    dependencies=[Depends(require_kadep_or_dosen)]
)
async def detail_kurikulum(id_kurikulum: str, session: Session = Depends(get_session)):
    """
    Mengambil informasi detail kurikulum beserta CPL terkait.
    
    **Parameter:**
    - **id_kurikulum**: ID kurikulum (format UUID)
    
    **Return:**
    - Informasi lengkap kurikulum:
      - id_kurikulum
      - nama_kurikulum
      - revisi
      - status_kurikulum
      - created_at
      - updated_at
    - Daftar CPL (Capaian Pembelajaran Lulusan) yang terkait:
      - id_cpl
      - deskripsi
    
    **Error:**
    - 400: Format ID kurikulum tidak valid (bukan UUID)
    - 404: Kurikulum tidak ditemukan
    """
    try:
        uuid_obj = uuid.UUID(id_kurikulum)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID Kurikulum tidak valid")
    
    item = session.exec(
        select(Kurikulum)
        .where(Kurikulum.id_kurikulum == id_kurikulum)
        .options(selectinload(Kurikulum.cpl_list))
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Kurikulum tidak ditemukan")

    
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


@router.delete(
    "/{id_kurikulum}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus Kurikulum",
    description="Menghapus kurikulum dari sistem",
    response_description="Tidak ada konten (sukses)",
    dependencies=[Depends(require_kadep)]
)
async def delete_kurikulum(id_kurikulum: str, session: Session = Depends(get_session)):
    """
    Menghapus kurikulum dari database.
    
    **Parameter:**
    - **id_kurikulum**: ID kurikulum yang akan dihapus (format UUID)
    
    **Peringatan:**
    - Operasi ini akan menghapus kurikulum secara permanen
    - Pastikan tidak ada relasi yang masih bergantung pada kurikulum ini
    
    **Error:**
    - 404: Kurikulum tidak ditemukan
    """
    item = session.get(Kurikulum, id_kurikulum)
    if not item:
        raise HTTPException(status_code=404, detail="Kurikulum tidak ditemukan")

    session.delete(item)
    session.commit()
    return