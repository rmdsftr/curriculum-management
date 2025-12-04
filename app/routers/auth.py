from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.db import get_session
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.utils.auth import (
    verify_password, 
    create_access_token, 
    get_current_user,
    security,
    decode_token
)
from datetime import timedelta, datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.user_id == login_data.user_id)
    user = session.exec(statement).first()
    
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user_id or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={
            "sub": user.user_id,  
            "nama": user.nama,
            "role": user.role
        },
        expires_delta=timedelta(hours=24)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return UserResponse(
        user_id=current_user.user_id,
        nama=current_user.nama,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    token = credentials.credentials
    
    try:
        token_data = decode_token(token)
        
        existing = session.exec(
            select(TokenBlacklist).where(TokenBlacklist.token == token)
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token already revoked"
            )
        
        blacklist_entry = TokenBlacklist(
            token=token,
            user_id=token_data.user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)  
        )
        session.add(blacklist_entry)
        session.commit()
        
        return {
            "message": "Successfully logged out",
            "detail": "Token has been revoked and can no longer be used"
        }
        
    except HTTPException as e:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )