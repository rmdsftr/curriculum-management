from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from app.db import get_session
from app.schemas.matkul import createMatkul, updateMatkul
from app.models.matkul import MataKuliah
from app.models.cpl_matkul import CPLMataKuliah
from app.models.cpl import CPL
from app.models.indikator import IndikatorCPL
from app.utils.current_datetime import timestamp_now
from app.utils.auth import require_kadep, require_kadep_or_dosen

router = APIRouter(
    prefix="/matkul", 
    tags=["matkul"],
    responses={404: {"description": "Tidak ditemukan"}}
)

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Mata Kuliah Baru",
    description="Menambahkan mata kuliah baru beserta relasi dengan CPL (Capaian Pembelajaran Lulusan)",
    response_description="Data mata kuliah dan relasi CPL yang berhasil ditambahkan",
    dependencies=[Depends(require_kadep_or_dosen)]
)  
async def inputMatkul(data: createMatkul, session: Session = Depends(get_session)):
    """
    Menambahkan mata kuliah baru ke database.
    
    **Parameter:**
    - **id_matkul**: ID unik mata kuliah
    - **mata_kuliah**: Nama mata kuliah
    - **sks**: Jumlah SKS
    - **semester**: Semester pengajaran
    - **cpl_list**: Daftar CPL yang terkait dengan mata kuliah
    
    **Validasi:**
    - ID mata kuliah harus unik
    - Semua CPL dalam cpl_list harus sudah ada di database
    
    **Return:**
    - Data mata kuliah yang baru dibuat
    - Daftar relasi CPL-Matkul yang terbentuk
    """
    existing_matkul = session.exec(
        select(MataKuliah).where(MataKuliah.id_matkul == data.id_matkul)
    ).first()

    if existing_matkul:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mata kuliah dengan ID tersebut sudah ada."
        )

    for cpl_input in data.cpl_list:
        cpl_exists = session.exec(
            select(CPL).where(
                CPL.id_kurikulum == cpl_input.id_kurikulum,
                CPL.id_cpl == cpl_input.id_cpl
            )
        ).first()

        if not cpl_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CPL dengan ID {cpl_input.id_cpl} di kurikulum {cpl_input.id_kurikulum} tidak ditemukan."
            )

    newMatkul = MataKuliah(
        id_matkul=data.id_matkul,
        mata_kuliah=data.mata_kuliah,
        sks=data.sks,
        semester=data.semester
    )
    session.add(newMatkul)
    session.commit()
    session.refresh(newMatkul)

    newRelations = []
    for cpl_input in data.cpl_list:
        existing_relation = session.exec(
            select(CPLMataKuliah).where(
                CPLMataKuliah.id_kurikulum == cpl_input.id_kurikulum,
                CPLMataKuliah.id_cpl == cpl_input.id_cpl,
                CPLMataKuliah.id_matkul == data.id_matkul
            )
        ).first()

        if not existing_relation:
            newCplMatkul = CPLMataKuliah(
                id_kurikulum=cpl_input.id_kurikulum,
                id_cpl=cpl_input.id_cpl,
                id_matkul=newMatkul.id_matkul
            )
            session.add(newCplMatkul)
            newRelations.append(newCplMatkul)
    
    session.commit()
    
    for relation in newRelations:
        session.refresh(relation)

    return {
        "message": "Berhasil menambahkan mata kuliah",
        "matkul": {
            "id_matkul": newMatkul.id_matkul,
            "mata_kuliah": newMatkul.mata_kuliah,
            "sks": newMatkul.sks,
            "semester": newMatkul.semester,
            "created_at": newMatkul.created_at,
            "updated_at": newMatkul.updated_at
        },
        "relasi": [
            {
                "id_kurikulum": str(r.id_kurikulum),
                "id_cpl": r.id_cpl,
                "id_matkul": r.id_matkul
            }
            for r in newRelations
        ]
    }


@router.delete(
    "/{id_matkul}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus Mata Kuliah",
    description="Menghapus mata kuliah beserta semua relasi CPL yang terkait",
    response_description="Tidak ada konten (sukses)",
    dependencies=[Depends(require_kadep)]
)
async def deleteMatkul(id_matkul: str, session: Session = Depends(get_session)):
    """
    Menghapus mata kuliah dari database.
    
    **Parameter:**
    - **id_matkul**: ID mata kuliah yang akan dihapus
    
    **Proses:**
    1. Menghapus semua relasi CPL-Matkul
    2. Menghapus data mata kuliah
    
    **Error:**
    - 404: Mata kuliah tidak ditemukan
    """
    matkul = session.get(MataKuliah, id_matkul)
    if not matkul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Mata kuliah tidak ditemukan"
        )
    
    delete_cpl_matkul = delete(CPLMataKuliah).where(CPLMataKuliah.id_matkul == id_matkul)
    session.exec(delete_cpl_matkul)
    
    delete_matkul = delete(MataKuliah).where(MataKuliah.id_matkul == id_matkul)
    session.exec(delete_matkul)
    
    session.commit()


@router.patch(
    "/{id_matkul}", 
    status_code=status.HTTP_200_OK,
    summary="Update Mata Kuliah",
    description="Mengupdate informasi mata kuliah dan/atau relasi CPL",
    response_description="Data mata kuliah dan relasi CPL yang telah diupdate",
    dependencies=[Depends(require_kadep_or_dosen)]
)
async def updateMatkul(id_matkul: str, data: updateMatkul, session: Session = Depends(get_session)):
    """
    Mengupdate data mata kuliah yang sudah ada.
    
    **Parameter:**
    - **id_matkul**: ID mata kuliah yang akan diupdate
    - **mata_kuliah** (opsional): Nama mata kuliah baru
    - **sks** (opsional): Jumlah SKS baru
    - **semester** (opsional): Semester baru
    - **cpl_list** (opsional): Daftar CPL baru (akan mengganti semua relasi lama)
    
    **Catatan:**
    - Hanya field yang diisi yang akan diupdate
    - Jika cpl_list diisi, semua relasi CPL lama akan dihapus dan diganti dengan yang baru
    - Timestamp updated_at akan otomatis diupdate
    
    **Return:**
    - Data mata kuliah yang telah diupdate
    - Daftar relasi CPL terkini
    """
    matkul = session.get(MataKuliah, id_matkul)
    if not matkul:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Mata kuliah tidak ditemukan"
        )
    
    if data.mata_kuliah is not None:
        matkul.mata_kuliah = data.mata_kuliah
    
    if data.sks is not None:
        matkul.sks = data.sks
    
    if data.semester is not None:
        matkul.semester = data.semester
    
    matkul.updated_at = timestamp_now()
    
    if data.cpl_list is not None:
        
        for cpl_input in data.cpl_list:
            cpl_exists = session.exec(
                select(CPL).where(
                    CPL.id_kurikulum == cpl_input.id_kurikulum,
                    CPL.id_cpl == cpl_input.id_cpl
                )
            ).first()
            
            if not cpl_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"CPL dengan ID {cpl_input.id_cpl} di kurikulum {cpl_input.id_kurikulum} tidak ditemukan."
                )
         
        delete_stmt = delete(CPLMataKuliah).where(
            CPLMataKuliah.id_matkul == id_matkul
        )
        session.exec(delete_stmt)
          
        for cpl_input in data.cpl_list:
            new_relation = CPLMataKuliah(
                id_kurikulum=cpl_input.id_kurikulum,
                id_cpl=cpl_input.id_cpl,
                id_matkul=id_matkul
            )
            session.add(new_relation)
    
    session.add(matkul)
    session.commit()
    session.refresh(matkul)
    
    relations = session.exec(
        select(CPLMataKuliah).where(CPLMataKuliah.id_matkul == id_matkul)
    ).all()
    
    return {
        "message": "Berhasil mengupdate mata kuliah",
        "matkul": {
            "id_matkul": matkul.id_matkul,
            "mata_kuliah": matkul.mata_kuliah,
            "sks": matkul.sks,
            "semester": matkul.semester,
            "created_at": matkul.created_at,
            "updated_at": matkul.updated_at
        },
        "relasi": [
            {
                "id_kurikulum": str(r.id_kurikulum),
                "id_cpl": r.id_cpl,
                "id_matkul": r.id_matkul
            }
            for r in relations
        ]
    }


@router.get(
    "/{id_matkul}", 
    status_code=status.HTTP_200_OK,
    summary="Detail Mata Kuliah",
    description="Mengambil detail lengkap mata kuliah beserta CPL dan indikator yang terkait",
    response_description="Data lengkap mata kuliah dengan CPL dan indikator",
    dependencies=[Depends(require_kadep_or_dosen)]
)
async def getDetailMatkul(id_matkul: str, session: Session = Depends(get_session)):
    """
    Mengambil informasi detail mata kuliah.
    
    **Parameter:**
    - **id_matkul**: ID mata kuliah yang ingin dilihat
    
    **Return:**
    - Informasi lengkap mata kuliah (ID, nama, SKS, semester, timestamps)
    - Daftar CPL yang terkait beserta:
      - ID kurikulum
      - ID CPL
      - Deskripsi CPL
      - Daftar indikator CPL (ID dan deskripsi)
    
    **Error:**
    - 404: Mata kuliah tidak ditemukan
    """
    matkul = session.get(MataKuliah, id_matkul)
    if not matkul:
        raise HTTPException(
            status_code=404, 
            detail="Mata kuliah tidak ditemukan"
        )

    cpl_rows = session.exec(
        select(CPL, CPLMataKuliah.id_kurikulum)
        .join(CPLMataKuliah, 
              (CPL.id_kurikulum == CPLMataKuliah.id_kurikulum) & 
              (CPL.id_cpl == CPLMataKuliah.id_cpl))
        .where(CPLMataKuliah.id_matkul == id_matkul)
    ).all()

    cpl_list = []

    for cpl, id_kurikulum in cpl_rows:
        
        indikator_rows = session.exec(
            select(IndikatorCPL).where(
                IndikatorCPL.id_kurikulum == cpl.id_kurikulum,
                IndikatorCPL.id_cpl == cpl.id_cpl
            )
        ).all()

        indikator_list = [
            {
                "id_indikator": i.id_indikator,
                "deskripsi": i.deskripsi
            }
            for i in indikator_rows
        ]

        cpl_list.append({
            "id_kurikulum": str(cpl.id_kurikulum),
            "id_cpl": cpl.id_cpl,
            "deskripsi": cpl.deskripsi,
            "indikator": indikator_list
        })

    return {
        "mata_kuliah": {
            "id_matkul": matkul.id_matkul,
            "mata_kuliah": matkul.mata_kuliah,
            "sks": matkul.sks,
            "semester": matkul.semester,
            "created_at": matkul.created_at,
            "updated_at": matkul.updated_at,
        },
        "cpl": cpl_list  
    }


@router.get(
    "/", 
    status_code=status.HTTP_200_OK,
    summary="Daftar Semua Mata Kuliah",
    description="Mengambil daftar semua mata kuliah beserta CPL yang terkait",
    response_description="Daftar lengkap mata kuliah dengan CPL masing-masing",
    dependencies=[Depends(require_kadep_or_dosen)]
)
async def getAllMatkul(session: Session = Depends(get_session)):
    """
    Mengambil daftar semua mata kuliah beserta CPL yang terkait.
    
    **Return:**
    - Daftar mata kuliah yang berisi:
      - id_matkul: Kode mata kuliah
      - mata_kuliah: Nama mata kuliah
      - sks: Jumlah SKS
      - semester: Semester pengajaran
      - cpl: Daftar CPL yang terkait (id_kurikulum, id_cpl, deskripsi)
    """
    
    all_matkul = session.exec(select(MataKuliah)).all()
    
    result = []
    
    for matkul in all_matkul:
        
        cpl_rows = session.exec(
            select(CPL, CPLMataKuliah.id_kurikulum)
            .join(CPLMataKuliah, 
                  (CPL.id_kurikulum == CPLMataKuliah.id_kurikulum) & 
                  (CPL.id_cpl == CPLMataKuliah.id_cpl))
            .where(CPLMataKuliah.id_matkul == matkul.id_matkul)
        ).all()
        
        
        cpl_list = [
            {
                "id_kurikulum": str(cpl.id_kurikulum),
                "id_cpl": cpl.id_cpl,
                "deskripsi": cpl.deskripsi
            }
            for cpl, _ in cpl_rows
        ]
        
        
        result.append({
            "id_matkul": matkul.id_matkul,
            "mata_kuliah": matkul.mata_kuliah,
            "sks": matkul.sks,
            "semester": matkul.semester,
            "cpl": cpl_list
        })
    
    return {
        "message": "Berhasil mengambil semua mata kuliah",
        "data": result
    }