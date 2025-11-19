from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.schemas.user import CreateUser, UpdateUser
from app.models.user import User
import uuid

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_all_users(session: Session = Depends(get_session)):
    data = select(User)
    results = session.exec(data).all()
    return results


@router.get("/{user_id}")
async def get_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user


@router.post("/")
async def create_user(data: CreateUser, session: Session = Depends(get_session)):
    new_user = User(name=data.name, role=data.role)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.put("/{user_id}")
async def update_user(
    user_id: uuid.UUID, 
    data: UpdateUser, 
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    if data.name is not None:
        user.name = data.name
    if data.role is not None:
        user.role = data.role
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    session.delete(user)
    session.commit()
    return {"message": "User berhasil dihapus"}