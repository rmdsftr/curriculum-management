from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.db import get_session
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, RegisterRequest
from app.utils.auth import (
    verify_password, 
    create_access_token, 
    get_current_user,
    security,
    decode_token,
    hash_password
)
from datetime import timedelta, datetime, timezone
from app.utils.auth import require_kadep

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized - Invalid credentials or token"},
        400: {"description": "Bad Request"}
    }
)

@router.post(
    "/login", 
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login User",
    description="Autentikasi user dan mendapatkan JWT access token",
    response_description="JWT access token untuk autentikasi dan otorisasi endpoint lain"
)
def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login user dan mendapatkan JWT access token.
    
    **Parameter Body:**
    - **user_id**: ID user yang akan login
    - **password**: Password user dalam plain text
    
    **Proses:**
    1. Mencari user berdasarkan user_id
    2. Memverifikasi password (hashed comparison)
    3. Membuat JWT token dengan payload user info
    4. Token berlaku selama 24 jam
    
    **Token Payload:**
    - sub: user_id
    - nama: nama lengkap user
    - role: role user (kadep/dosen)
    
    **Return:**
    - **access_token**: JWT token untuk autentikasi
    - **token_type**: "bearer" (untuk Authorization header)
    
    **Cara Penggunaan Token:**
    - Tambahkan ke request header: `Authorization: Bearer <access_token>`
    - Token berlaku selama 24 jam sejak dibuat
    
    **Error:**
    - 401: user_id tidak ditemukan atau password salah
    
    **Security:**
    - Password di-hash menggunakan bcrypt
    - Token menggunakan JWT dengan signing algorithm
    """
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

@router.get(
    "/me", 
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Info",
    description="Mengambil informasi user yang sedang login berdasarkan JWT token",
    response_description="Data lengkap user yang sedang terautentikasi"
)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil informasi user yang sedang login.
    
    **Authorization Required:**
    - Header: `Authorization: Bearer <access_token>`
    - Token harus valid dan belum expired
    - Token tidak boleh ada di blacklist
    
    **Return:**
    - **user_id**: ID user
    - **nama**: Nama lengkap user
    - **role**: Role user dalam sistem
    - **created_at**: Timestamp pembuatan akun
    - **updated_at**: Timestamp update terakhir
    
    **Use Case:**
    - Mengambil profile user yang sedang login
    - Validasi token masih aktif
    - Mendapatkan role untuk authorization
    
    **Error:**
    - 401: Token tidak valid, expired, atau sudah di-revoke
    
    **Catatan:**
    - Endpoint ini otomatis mengecek validitas token
    - Password tidak akan dikembalikan dalam response
    """
    return UserResponse(
        user_id=current_user.user_id,
        nama=current_user.nama,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout User",
    description="Logout user dengan cara memasukkan token ke blacklist",
    response_description="Konfirmasi logout berhasil"
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    """
    Logout user dengan cara me-revoke JWT token.
    
    **Authorization Required:**
    - Header: `Authorization: Bearer <access_token>`
    - Token harus valid dan belum di-revoke
    
    **Proses:**
    1. Decode dan validasi JWT token
    2. Cek apakah token sudah ada di blacklist
    3. Tambahkan token ke blacklist dengan expires_at 24 jam
    4. Token tidak bisa digunakan lagi setelah logout
    
    **Token Blacklist:**
    - Token yang di-logout disimpan di database
    - Token tetap di blacklist sampai expires_at tercapai
    - Mencegah token yang sama digunakan ulang
    
    **Return:**
    - Message konfirmasi logout
    - Detail bahwa token sudah di-revoke
    
    **Error:**
    - 400: Token sudah pernah di-revoke sebelumnya
    - 401: Token tidak valid atau format salah
    
    **Security Note:**
    - Logout bersifat server-side (token blacklisting)
    - Client tetap harus menghapus token dari storage mereka
    - Token yang di-revoke tidak bisa digunakan meskipun belum expired
    
    **Best Practice:**
    - Hapus token dari localStorage/sessionStorage setelah logout
    - Redirect user ke halaman login
    """
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
        raise
    except Exception:  
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register User Baru",
    description="Mendaftarkan user baru ke sistem, hanya bisa dilakukan kadep",
    response_description="Data user yang berhasil didaftarkan",
    dependencies=[Depends(require_kadep)]
)
def register(
    register_data: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Mendaftarkan user baru ke sistem.
    
    **Parameter Body:**
    - **user_id**: ID user (max 25 karakter, harus unik)
    - **nama**: Nama lengkap user (max 255 karakter)
    - **password**: Password minimal 8 karakter
    - **role**: Role user ('kadep' atau 'dosen')
    
    **Validasi:**
    - user_id harus unik (tidak boleh duplikat)
    - Password minimal 8 karakter
    - Role harus 'kadep' atau 'dosen'
    
    **Proses:**
    1. Validasi user_id belum ada di database
    2. Hash password menggunakan bcrypt
    3. Simpan user baru ke database
    4. Return data user (tanpa password)
    
    **Return:**
    - Message konfirmasi
    - Data user baru (user_id, nama, role, timestamps)
    
    **Error:**
    - 400: user_id sudah digunakan atau role tidak valid
    
    **Security Note:**
    - Password akan di-hash sebelum disimpan
    - Password tidak akan pernah dikembalikan dalam response
    - Gunakan password yang kuat (kombinasi huruf, angka, simbol)
    
    **Production Note:**
    - Endpoint ini sebaiknya dibatasi hanya untuk admin
    - Pertimbangkan menambahkan email verification
    - Tambahkan captcha untuk mencegah spam registration
    """
    
    existing_user = session.exec(
        select(User).where(User.user_id == register_data.user_id)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id already exists. Please choose a different user_id."
        )
    
    from app.models.user import RoleEnum
    if register_data.role not in [RoleEnum.kadep, RoleEnum.dosen]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'kadep' or 'dosen'."
        )
    
    if len(register_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long."
        )
    
    hashed_password = hash_password(register_data.password)
     
    new_user = User(
        user_id=register_data.user_id,
        nama=register_data.nama,
        password=hashed_password,
        role=register_data.role
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return {
        "message": "User registered successfully",
        "user": {
            "user_id": new_user.user_id,
            "nama": new_user.nama,
            "role": new_user.role,
            "created_at": new_user.created_at,
            "updated_at": new_user.updated_at
        }
    }