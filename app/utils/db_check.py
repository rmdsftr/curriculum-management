from sqlmodel import Session, text
from app.db import engine

def db_connection():
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        return True
    except Exception as e:
        return False