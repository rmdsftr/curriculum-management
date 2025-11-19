from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    """Initialize database - create all tables"""
    from app.models.kurikulum import Kurikulum
    from app.models.cpl import CPL
    from app.models.indikator import IndikatorCPL
    from app.models.matkul import MataKuliah
    from app.models.cpl_matkul import CPLMataKuliah  
    
    SQLModel.metadata.create_all(engine)
    print("✓ Database tables created successfully!")

def drop_db():
    """Drop all tables - DANGER: Use with caution!"""
    SQLModel.metadata.drop_all(engine)
    print("✓ All tables dropped!")

def get_session():
    with Session(engine) as session:
        yield session