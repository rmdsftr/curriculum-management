from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from app.db import get_session
from app.schemas.indikator import CreateIndikator, IndikatorCPLUpdate
from app.models.indikator import IndikatorCPL
from app.models.cpl import CPL
import re
import uuid
from app.utils.auth import require_kadep, require_kadep_or_dosen

router = APIRouter(
    prefix="/indikator", 
    tags=["indikator"],
    responses={404: {"description": "Tidak ditemukan"}}
)

@router.post(
    "/{id_kurikulum}/{id_cpl}", 
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Indikator CPL",
    description="Menambahkan indikator baru untuk CPL tertentu dalam kurikulum",
    response_description="Data indikator yang berhasil ditambahkan",
    dependencies=[Depends(require_kadep)]
)
async def create_indikator(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    data: CreateIndikator,
    session: Session = Depends(get_session)
):
    """
    Menambahkan indikator CPL baru ke database.
    
    **Parameter Path:**
    - **id_kurikulum**: ID kurikulum (format UUID)
    - **id_cpl**: ID CPL yang akan ditambahkan indikatornya
    
    **Parameter Body:**
    - **id_indikator**: ID indikator (format: IND-XX-YY, contoh: IND-01-01)
    - **deskripsi**: Deskripsi indikator
    
    **Validasi:**
    - CPL harus ada di kurikulum yang ditentukan
    - id_indikator tidak boleh kosong
    - id_indikator harus mengikuti format 'IND-XX-YY'
    - id_indikator harus unik untuk CPL tersebut
    - deskripsi tidak boleh kosong
    
    **Return:**
    - Message konfirmasi
    - Data indikator lengkap (id_kurikulum, id_cpl, id_indikator, deskripsi)
    
    **Error:**
    - 400: Format ID tidak valid, field kosong, atau ID sudah digunakan
    - 404: CPL tidak ditemukan
    """
    cpl = session.exec(
        select(CPL).where(
            CPL.id_kurikulum == id_kurikulum,
            CPL.id_cpl == id_cpl
        )
    ).first()

    if not cpl:
        raise HTTPException(
            404,
            "CPL tidak ditemukan di kurikulum ini."
        )
    
    if not data.id_indikator.strip():
        raise HTTPException(400, "id_indikator tidak boleh kosong.")
    
    pattern = r"^IND-\d{2}-\d{2}$"
    if not re.match(pattern, data.id_indikator):
        raise HTTPException(
            400,
            "Format id_indikator tidak valid. Gunakan pola 'IND-XX-YY', XX sesuai no CPL."
        )
    
    existing_indikator = session.exec(
        select(IndikatorCPL).where(
            IndikatorCPL.id_kurikulum == id_kurikulum,
            IndikatorCPL.id_cpl == id_cpl,
            IndikatorCPL.id_indikator == data.id_indikator
        )
    ).first()

    if existing_indikator:
        raise HTTPException(
            400,
            "id_indikator sudah digunakan untuk CPL ini. Gunakan id_indikator lain."
        )

    if not data.deskripsi.strip():
        raise HTTPException(400, "deskripsi tidak boleh kosong.")
     
    new_indikator = IndikatorCPL(
        id_kurikulum=id_kurikulum,
        id_cpl=id_cpl,
        id_indikator=data.id_indikator,
        deskripsi=data.deskripsi
    )

    session.add(new_indikator)
    session.commit()
    session.refresh(new_indikator)

    return {
        "message": "Indikator CPL berhasil dibuat.",
        "data": {
            "id_kurikulum": str(new_indikator.id_kurikulum),
            "id_cpl": new_indikator.id_cpl,
            "id_indikator": new_indikator.id_indikator,
            "deskripsi": new_indikator.deskripsi
        }
    }


@router.delete(
    "/{id_kurikulum}/{id_cpl}/{id_indikator}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus Indikator CPL",
    description="Menghapus indikator CPL dari sistem",
    response_description="Tidak ada konten (sukses)",
    dependencies=[Depends(require_kadep)]
)
async def deleteIndikator(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    id_indikator: str,
    session: Session = Depends(get_session)
):
    """
    Menghapus indikator CPL dari database.
    
    **Parameter Path:**
    - **id_kurikulum**: ID kurikulum (format UUID)
    - **id_cpl**: ID CPL
    - **id_indikator**: ID indikator yang akan dihapus
    
    **Proses:**
    1. Mencari indikator berdasarkan kombinasi id_kurikulum, id_cpl, dan id_indikator
    2. Menghapus indikator jika ditemukan
    
    **Peringatan:**
    - Operasi ini akan menghapus indikator secara permanen
    
    **Error:**
    - 404: Indikator tidak ditemukan
    """
    
    statement = select(IndikatorCPL).where(
        IndikatorCPL.id_kurikulum == id_kurikulum,
        IndikatorCPL.id_cpl == id_cpl,
        IndikatorCPL.id_indikator == id_indikator
    )
    indikator = session.exec(statement).first()
    
    if not indikator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Indikator tidak ditemukan"
        )
    
    hapus = delete(IndikatorCPL).where(
        IndikatorCPL.id_kurikulum == id_kurikulum,
        IndikatorCPL.id_cpl == id_cpl,
        IndikatorCPL.id_indikator == id_indikator
    )
    session.exec(hapus)
    session.commit()


@router.patch(
    "/{id_kurikulum}/{id_cpl}/{id_indikator}", 
    status_code=status.HTTP_200_OK,
    summary="Update Indikator CPL",
    description="Mengupdate informasi indikator CPL, termasuk mengubah CPL parent-nya",
    response_description="Data indikator yang telah diupdate",
    dependencies=[Depends(require_kadep)]
)
async def update_indikator(
    id_kurikulum: uuid.UUID,
    id_cpl: str,
    id_indikator: str,
    data: IndikatorCPLUpdate,
    session: Session = Depends(get_session)
):
    """
    Mengupdate data indikator CPL yang sudah ada.
    
    **Parameter Path:**
    - **id_kurikulum**: ID kurikulum (format UUID)
    - **id_cpl**: ID CPL saat ini
    - **id_indikator**: ID indikator yang akan diupdate
    
    **Parameter Body (semua opsional):**
    - **id_cpl**: ID CPL baru (jika ingin memindahkan indikator ke CPL lain)
    - **deskripsi**: Deskripsi indikator baru
    
    **Fitur Khusus:**
    - Jika id_cpl diubah, indikator akan dipindahkan ke CPL baru
    - Sistem akan memvalidasi CPL baru ada di kurikulum yang sama
    - Mencegah duplikasi kombinasi id_cpl dan id_indikator
    
    **Proses Update id_cpl:**
    1. Validasi CPL baru ada di database
    2. Cek tidak ada duplikasi
    3. Hapus record lama
    4. Buat record baru dengan id_cpl baru
    
    **Return:**
    - Message konfirmasi
    - Data indikator lengkap yang telah diupdate
    
    **Error:**
    - 400: Duplikasi kombinasi id_cpl dan id_indikator
    - 404: Indikator atau CPL baru tidak ditemukan
    """
    statement = select(IndikatorCPL).where(
        IndikatorCPL.id_kurikulum == id_kurikulum,
        IndikatorCPL.id_cpl == id_cpl,
        IndikatorCPL.id_indikator == id_indikator
    )
    item = session.exec(statement).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Indikator tidak ditemukan")

    updates = data.model_dump(exclude_unset=True)

    
    if "id_cpl" in updates:
        new_id_cpl = updates["id_cpl"]
        
        statement_cpl = select(CPL).where(
            CPL.id_kurikulum == id_kurikulum,
            CPL.id_cpl == new_id_cpl
        )
        cpl_item = session.exec(statement_cpl).first()
        
        if not cpl_item:
            raise HTTPException(
                status_code=404, 
                detail=f"CPL '{new_id_cpl}' tidak ditemukan di kurikulum ini"
            )
        
        if new_id_cpl != id_cpl:       
            check_statement = select(IndikatorCPL).where(
                IndikatorCPL.id_kurikulum == id_kurikulum,
                IndikatorCPL.id_cpl == new_id_cpl,
                IndikatorCPL.id_indikator == id_indikator
            )
            existing = session.exec(check_statement).first()
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Indikator dengan id_cpl '{new_id_cpl}' dan id_indikator '{id_indikator}' sudah ada"
                )
              
            session.delete(item)
            session.flush()
            
            new_item = IndikatorCPL(
                id_kurikulum=id_kurikulum,
                id_cpl=new_id_cpl,
                id_indikator=id_indikator,
                deskripsi=updates.get("deskripsi", item.deskripsi)
            )
            session.add(new_item)
            session.commit()
            session.refresh(new_item)
            
            return {
                "message": "Berhasil memperbarui indikator (dengan id_cpl baru)",
                "indikator": {
                    "id_kurikulum": str(new_item.id_kurikulum),
                    "id_cpl": new_item.id_cpl,
                    "id_indikator": new_item.id_indikator,
                    "deskripsi": new_item.deskripsi
                }
            }

    for key, value in updates.items():
        if key not in ["id_kurikulum", "id_cpl", "id_indikator"]:  
            setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)

    return {
        "message": "Berhasil memperbarui indikator",
        "indikator": {
            "id_kurikulum": str(item.id_kurikulum),
            "id_cpl": item.id_cpl,
            "id_indikator": item.id_indikator,
            "deskripsi": item.deskripsi
        }
    }