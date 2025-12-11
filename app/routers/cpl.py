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
from app.utils.auth import require_kadep, require_kadep_or_dosen

router = APIRouter(
    prefix="/cpl", 
    tags=["cpl"],
    responses={404: {"description": "Tidak ditemukan"}}
)

@router.post(
    "/{id_kurikulum}", 
    status_code=status.HTTP_201_CREATED,
    summary="Tambah CPL Baru",
    description="Menambahkan CPL (Capaian Pembelajaran Lulusan) baru ke kurikulum tertentu",
    response_description="Data CPL yang berhasil ditambahkan",
    dependencies=[Depends(require_kadep)]
)
async def create_cpl(
    id_kurikulum: uuid.UUID,
    data: CreateCPL,
    session: Session = Depends(get_session)
):
    """
    Menambahkan CPL baru ke kurikulum.
    
    **Parameter Path:**
    - **id_kurikulum**: ID kurikulum tempat CPL akan ditambahkan (format UUID)
    
    **Parameter Body:**
    - **id_cpl**: ID CPL dengan format 'CPL-XX' (contoh: CPL-01, CPL-02)
    - **deskripsi**: Deskripsi capaian pembelajaran lulusan
    
    **Validasi:**
    - Kurikulum harus ada di database
    - id_cpl tidak boleh kosong
    - id_cpl harus mengikuti format 'CPL-XX' (dua digit angka)
    - id_cpl harus unik dalam kurikulum yang sama
    - deskripsi tidak boleh kosong
    
    **Contoh Format ID yang Valid:**
    - CPL-01, CPL-02, CPL-10, CPL-99
    
    **Return:**
    - Message konfirmasi
    - Data CPL lengkap (id_cpl, deskripsi, id_kurikulum)
    
    **Error:**
    - 400: Format ID tidak valid, field kosong, atau ID sudah digunakan
    - 404: Kurikulum tidak ditemukan
    """
    kurikulum = session.exec(
        select(Kurikulum).where(Kurikulum.id_kurikulum == id_kurikulum)
    ).first()

    if not kurikulum:
        raise HTTPException(404, "Kurikulum tidak ditemukan.")
    
    if not data.id_cpl.strip():
        raise HTTPException(400, "id_cpl tidak boleh kosong.")
    
    
    pattern = r"^CPL-\d{2}$"
    if not re.match(pattern, data.id_cpl):
        raise HTTPException(
            400,
            "Format id_cpl tidak valid. Gunakan pola 'CPL-XX' (dua digit)."
        )

    existing_cpl = session.exec(
        select(CPL).where(
            (CPL.id_cpl == data.id_cpl) & (CPL.id_kurikulum == id_kurikulum)
        )
    ).first()

    if existing_cpl:
        raise HTTPException(400, "id_cpl sudah digunakan. Gunakan id_cpl lain.")
  
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

@router.get(
    "/{id_kurikulum}/{id_cpl}", 
    status_code=status.HTTP_200_OK,
    summary="Detail CPL Lengkap",
    description="Mengambil detail lengkap CPL beserta kurikulum, indikator, dan mata kuliah terkait",
    response_description="Data lengkap CPL dengan semua relasinya",
    dependencies=[Depends(require_kadep_or_dosen)]
)
async def get_detail_cpl(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    session: Session = Depends(get_session) 
):
    """
    Mengambil informasi detail CPL lengkap dengan semua relasinya.
    
    **Parameter Path:**
    - **id_kurikulum**: ID kurikulum (format UUID)
    - **id_cpl**: ID CPL yang ingin dilihat
    
    **Return:**
    - **cpl**: Data CPL (id_cpl, deskripsi)
    - **kurikulum**: Informasi kurikulum parent (id, nama, revisi)
    - **indikator**: Array indikator CPL
      - id_indikator
      - deskripsi
    - **mata_kuliah**: Array mata kuliah yang menggunakan CPL ini
      - id_matkul
      - mata_kuliah (nama)
      - sks
      - semester
    
    **Fitur:**
    - Menampilkan semua relasi CPL dalam satu response
    - Berguna untuk melihat dampak CPL terhadap mata kuliah
    
    **Error:**
    - 404: CPL tidak ditemukan
    """
    cpl = session.exec(
        select(CPL).where(
            (CPL.id_kurikulum == id_kurikulum) & (CPL.id_cpl == id_cpl)
        )
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


@router.patch(
    "/{id_kurikulum}/{id_cpl}", 
    status_code=status.HTTP_200_OK,
    summary="Update CPL",
    description="Mengupdate deskripsi CPL",
    response_description="Data CPL yang telah diupdate",
    dependencies=[Depends(require_kadep)]
)
async def update_cpl(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    data: UpdateCPL,
    session: Session = Depends(get_session)
):
    """
    Mengupdate data CPL yang sudah ada.
    
    **Parameter Path:**
    - **id_kurikulum**: ID kurikulum (format UUID)
    - **id_cpl**: ID CPL yang akan diupdate
    
    **Parameter Body:**
    - **deskripsi** (opsional): Deskripsi CPL baru
    
    **Catatan:**
    - id_cpl tidak dapat diubah (merupakan primary key)
    - id_kurikulum tidak dapat diubah (merupakan primary key)
    - Hanya deskripsi yang dapat diupdate
    - Deskripsi tidak boleh kosong jika diisi
    
    **Return:**
    - Message konfirmasi
    - Data CPL lengkap yang telah diupdate
    
    **Error:**
    - 400: Deskripsi kosong
    - 404: CPL tidak ditemukan
    """
    cpl = session.exec(
        select(CPL).where(
            (CPL.id_kurikulum == id_kurikulum) & (CPL.id_cpl == id_cpl)
        )
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

@router.delete(
    "/{id_kurikulum}/{id_cpl}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus CPL",
    description="Menghapus CPL dari kurikulum",
    response_description="Tidak ada konten (sukses)",
    dependencies=[Depends(require_kadep)]
)
async def delete_cpl(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    session: Session = Depends(get_session)
):
    """
    Menghapus CPL dari database.
    
    **Parameter Path:**
    - **id_kurikulum**: ID kurikulum (format UUID)
    - **id_cpl**: ID CPL yang akan dihapus
    
    **Peringatan:**
    - Operasi ini akan menghapus CPL secara permanen
    - Pastikan tidak ada relasi yang masih bergantung pada CPL ini
    - Indikator dan relasi mata kuliah yang terkait mungkin juga terhapus (tergantung constraint DB)
    
    **Dampak:**
    - CPL akan dihapus dari kurikulum
    - Relasi dengan mata kuliah akan terputus
    - Indikator CPL mungkin ikut terhapus (cascade delete)
    
    **Error:**
    - 404: CPL tidak ditemukan
    """
    cpl = session.exec(
        select(CPL).where(
            (CPL.id_kurikulum == id_kurikulum) & (CPL.id_cpl == id_cpl)
        )
    ).first()

    if not cpl:
        raise HTTPException(404, "CPL tidak ditemukan.")

    session.delete(cpl)
    session.commit()