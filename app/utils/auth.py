from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.db import get_session
from app.models.user import User, RoleEnum
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth import TokenData
from app.config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            
            password = password_bytes[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decode and verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        nama: str = payload.get("nama")
        role: str = payload.get("role")
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(
            user_id=user_id,  
            nama=nama,
            role=role
        )
        return token_data
    except JWTError:
        raise credentials_exception

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user from token"""
    token = credentials.credentials
    
    
    blacklisted = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token == token)
    ).first()
    
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked (logged out)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = decode_token(token)
    
    statement = select(User).where(User.user_id == token_data.user_id)
    user = session.exec(statement).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_kadep(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user is Kadep"""
    if current_user.role != "kadep":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Kadep role required."
        )
    return current_user

async def get_current_dosen(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user is Dosen"""
    if current_user.role != "dosen":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Dosen role required."
        )
    return current_user

class RoleChecker:
    """
    Dependency untuk mengecek apakah user memiliki role yang diizinkan.
    
    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleChecker([RoleEnum.kadep]))])
        async def admin_endpoint():
            return {"message": "Hanya kadep yang bisa akses"}
    """
    
    def __init__(self, allowed_roles: List[RoleEnum]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in self.allowed_roles]}"
            )
        return current_user

def require_kadep(current_user: User = Depends(get_current_user)):
    """
    Dependency untuk endpoint yang hanya bisa diakses kadep.
    
    Usage:
        @router.post("/kurikulum", dependencies=[Depends(require_kadep)])
        async def create_kurikulum(data: KurikulumCreate):
            return {"message": "Created by kadep"}
    """
    if current_user.role != RoleEnum.kadep:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only 'kadep' role can access this endpoint."
        )
    return current_user

def require_dosen(current_user: User = Depends(get_current_user)):
    """
    Dependency untuk endpoint yang hanya bisa diakses dosen.
    
    Usage:
        @router.get("/matkul", dependencies=[Depends(require_dosen)])
        async def get_matkul():
            return {"message": "Accessible by dosen"}
    """
    if current_user.role != RoleEnum.dosen:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only 'dosen' role can access this endpoint."
        )
    return current_user


def require_kadep_or_dosen(current_user: User = Depends(get_current_user)):
    """
    Dependency untuk endpoint yang bisa diakses kadep atau dosen.
    
    Usage:
        @router.get("/cpl", dependencies=[Depends(require_kadep_or_dosen)])
        async def get_cpl():
            return {"message": "Accessible by kadep or dosen"}
    """
    if current_user.role not in [RoleEnum.kadep, RoleEnum.dosen]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only 'kadep' or 'dosen' role can access this endpoint."
        )
    return current_user