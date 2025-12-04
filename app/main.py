from fastapi import FastAPI
from app.db import init_db
from app.utils.db_check import db_connection
from app.routers import auth
from app.routers import kurikulum
from app.routers import cpl
from app.routers import indikator
from app.routers import matkul

app = FastAPI(
    title="Curriculum Management API",
    description="API untuk manajemen kurikulum, CPL, dan mata kuliah",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    print("Starting up application...")
    print("Application ready!")

@app.get("/")
async def main():
    if db_connection:
        status = "connection success"
    else:
        status = "connection failed"
    return {
        "database": status
    }

app.include_router(auth.router)
app.include_router(kurikulum.router)
app.include_router(cpl.router)
app.include_router(indikator.router)
app.include_router(matkul.router)
app.include_router(auth.router)