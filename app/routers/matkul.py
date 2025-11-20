from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from app.db import get_session
from app.schemas.matkul import createMatkul, updateMatkul
from app.models.matkul import MataKuliah
from app.models.cpl_matkul import CPLMataKuliah
from app.models.cpl import CPL
from app.models.indikator import IndikatorCPL
from app.utils.current_datetime import timestamp_now


router = APIRouter(prefix="/matkul", tags=["matkul"])


@router.post("/", status_code=status.HTTP_201_CREATED)  
async def inputMatkul(data: createMatkul, session: Session = Depends(get_session)):
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


@router.delete("/{id_matkul}", status_code=status.HTTP_204_NO_CONTENT)
async def deleteMatkul(id_matkul: str, session: Session = Depends(get_session)):
    matkul = session.get(MataKuliah, id_matkul)
    if not matkul:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mata kuliah tidak ditemukan")
    
    
    delete_cpl_matkul = delete(CPLMataKuliah).where(CPLMataKuliah.id_matkul == id_matkul)
    session.exec(delete_cpl_matkul)
    
    
    delete_matkul = delete(MataKuliah).where(MataKuliah.id_matkul == id_matkul)
    session.exec(delete_matkul)
    
    session.commit()


@router.patch("/{id_matkul}", status_code=status.HTTP_200_OK)
async def updateMatkul(id_matkul: str, data: updateMatkul, session: Session = Depends(get_session)):
    matkul = session.get(MataKuliah, id_matkul)
    if not matkul:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mata kuliah tidak ditemukan")
    
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


@router.get("/{id_matkul}", status_code=status.HTTP_200_OK)
async def getDetailMatkul(id_matkul: str, session: Session = Depends(get_session)):
    matkul = session.get(MataKuliah, id_matkul)
    if not matkul:
        raise HTTPException(status_code=404, detail="Mata kuliah tidak ditemukan")

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