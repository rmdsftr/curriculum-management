from fastapi import FastAPI
from app.db import init_db
from app.utils.db_check import db_connection
from app.routers import user

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
async def main():
    if db_connection:
        status = "connection success"
    else:
        status = "connection failed"
    return {
        "database" : status
    }

app.include_router(user.router)