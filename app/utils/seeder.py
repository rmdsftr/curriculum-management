from sqlmodel import Session, create_engine, select
from app.models.kurikulum import Kurikulum, StatusEnum
from app.models.cpl import CPL
from app.models.indikator import IndikatorCPL
from app.models.matkul import MataKuliah
from app.models.cpl_matkul import CPLMataKuliah 
from datetime import datetime
import uuid

def seed_kurikulum(session: Session):
    """Seed data untuk tabel kurikulum"""
    print("Seeding kurikulum...")
    
    kurikulum_data = [
        {
            "id_kurikulum": uuid.uuid4(),
            "nama_kurikulum": "Kurikulum Teknik Informatika 2020",
            "revisi": "Rev. 1",
            "status_kurikulum": StatusEnum.aktif
        },
        {
            "id_kurikulum": uuid.uuid4(),
            "nama_kurikulum": "Kurikulum Sistem Informasi 2020",
            "revisi": "Rev. 2",
            "status_kurikulum": StatusEnum.aktif
        },
        {
            "id_kurikulum": uuid.uuid4(),
            "nama_kurikulum": "Kurikulum Teknik Informatika 2016",
            "revisi": "Rev. 3",
            "status_kurikulum": StatusEnum.nonaktif
        }
    ]
    
    kurikulum_list = []
    for data in kurikulum_data:
        kurikulum = Kurikulum(**data)
        session.add(kurikulum)
        kurikulum_list.append(kurikulum)
    
    session.commit()
    print(f"✓ Seeded {len(kurikulum_list)} kurikulum")
    return kurikulum_list

def seed_cpl(session: Session, kurikulum_list):
    """Seed data untuk tabel CPL"""
    print("Seeding CPL...")
    
    cpl_data = [
        {
            "id_kurikulum": kurikulum_list[0].id_kurikulum,
            "id_cpl": "CPL-01",
            "deskripsi": "Mampu menerapkan pemikiran logis, kritis, sistematis, dan inovatif dalam konteks pengembangan atau implementasi ilmu pengetahuan dan teknologi"
        },
        {
            "id_kurikulum": kurikulum_list[0].id_kurikulum,
            "id_cpl": "CPL-02",
            "deskripsi": "Mampu menunjukkan kinerja mandiri, bermutu, dan terukur dalam pengembangan sistem informasi"
        },
        {
            "id_kurikulum": kurikulum_list[0].id_kurikulum,
            "id_cpl": "CPL-03",
            "deskripsi": "Mampu mengkaji implikasi pengembangan atau implementasi ilmu pengetahuan teknologi informasi"
        },
        {
            "id_kurikulum": kurikulum_list[1].id_kurikulum,
            "id_cpl": "CPL-04",
            "deskripsi": "Mampu mengambil keputusan secara tepat dalam konteks penyelesaian masalah di bidang teknologi informasi"
        },
        {
            "id_kurikulum": kurikulum_list[1].id_kurikulum,
            "id_cpl": "CPL-05",
            "deskripsi": "Mampu memelihara dan mengembangkan jaringan kerja dengan pembimbing, kolega, sejawat"
        }
    ]
    
    cpl_list = []
    for data in cpl_data:
        cpl = CPL(**data)
        session.add(cpl)
        cpl_list.append(cpl)
    
    session.commit()
    print(f"✓ Seeded {len(cpl_list)} CPL")
    return cpl_list

def seed_indikator_cpl(session: Session, cpl_list):
    """Seed data untuk tabel indikator CPL"""
    print("Seeding Indikator CPL...")
    
    indikator_data = [
        {
            "id_kurikulum": cpl_list[0].id_kurikulum,
            "id_cpl": cpl_list[0].id_cpl,
            "id_indikator": "IND-01-01",
            "deskripsi": "Mampu mengidentifikasi masalah komputasi dengan pendekatan logis dan sistematis"
        },
        {
            "id_kurikulum": cpl_list[0].id_kurikulum,
            "id_cpl": cpl_list[0].id_cpl,
            "id_indikator": "IND-01-02",
            "deskripsi": "Mampu merancang solusi inovatif untuk permasalahan komputasi"
        },
        {
            "id_kurikulum": cpl_list[0].id_kurikulum,
            "id_cpl": cpl_list[0].id_cpl,
            "id_indikator": "IND-01-03",
            "deskripsi": "Mampu mengimplementasikan algoritma dengan efisien"
        },
        {
            "id_kurikulum": cpl_list[1].id_kurikulum,
            "id_cpl": cpl_list[1].id_cpl,
            "id_indikator": "IND-02-01",
            "deskripsi": "Mampu bekerja secara mandiri dalam pengembangan sistem"
        },
        {
            "id_kurikulum": cpl_list[1].id_kurikulum,
            "id_cpl": cpl_list[1].id_cpl,
            "id_indikator": "IND-02-02",
            "deskripsi": "Mampu menghasilkan dokumentasi teknis yang berkualitas"
        },
        {
            "id_kurikulum": cpl_list[2].id_kurikulum,
            "id_cpl": cpl_list[2].id_cpl,
            "id_indikator": "IND-03-01",
            "deskripsi": "Mampu menganalisis dampak teknologi terhadap masyarakat"
        },
        {
            "id_kurikulum": cpl_list[3].id_kurikulum,
            "id_cpl": cpl_list[3].id_cpl,
            "id_indikator": "IND-04-01",
            "deskripsi": "Mampu mengambil keputusan berdasarkan analisis data yang tepat"
        },
        {
            "id_kurikulum": cpl_list[4].id_kurikulum,
            "id_cpl": cpl_list[4].id_cpl,
            "id_indikator": "IND-05-01",
            "deskripsi": "Mampu berkomunikasi efektif dalam tim multidisiplin"
        }
    ]
    
    indikator_list = []
    for data in indikator_data:
        indikator = IndikatorCPL(**data)
        session.add(indikator)
        indikator_list.append(indikator)
    
    session.commit()
    print(f"✓ Seeded {len(indikator_list)} Indikator CPL")
    return indikator_list


def seed_mata_kuliah(session: Session):
    """Seed data untuk tabel mata kuliah"""
    print("Seeding Mata Kuliah...")
    
    matkul_data = [
        {
            "id_matkul": "MK-001",
            "mata_kuliah": "Algoritma dan Pemrograman",
            "sks": 3,
            "semester": 1
        },
        {
            "id_matkul": "MK-002",
            "mata_kuliah": "Struktur Data",
            "sks": 3,
            "semester": 2
        },
        {
            "id_matkul": "MK-003",
            "mata_kuliah": "Basis Data",
            "sks": 3,
            "semester": 3
        },
        {
            "id_matkul": "MK-004",
            "mata_kuliah": "Pemrograman Web",
            "sks": 3,
            "semester": 3
        },
        {
            "id_matkul": "MK-005",
            "mata_kuliah": "Sistem Operasi",
            "sks": 3,
            "semester": 4
        },
        {
            "id_matkul": "MK-006",
            "mata_kuliah": "Jaringan Komputer",
            "sks": 3,
            "semester": 4
        },
        {
            "id_matkul": "MK-007",
            "mata_kuliah": "Rekayasa Perangkat Lunak",
            "sks": 3,
            "semester": 5
        },
        {
            "id_matkul": "MK-008",
            "mata_kuliah": "Kecerdasan Buatan",
            "sks": 3,
            "semester": 6
        },
        {
            "id_matkul": "MK-009",
            "mata_kuliah": "Machine Learning",
            "sks": 3,
            "semester": 7
        },
        {
            "id_matkul": "MK-010",
            "mata_kuliah": "Keamanan Informasi",
            "sks": 3,
            "semester": 6
        }
    ]
    
    matkul_list = []
    for data in matkul_data:
        matkul = MataKuliah(**data)
        session.add(matkul)
        matkul_list.append(matkul)
    
    session.commit()
    print(f"✓ Seeded {len(matkul_list)} Mata Kuliah")
    return matkul_list

def seed_cpl_matkul(session: Session, cpl_list, matkul_list):
    """Seed data untuk tabel relasi CPL - Mata Kuliah"""
    print("Seeding CPL-MataKuliah relations...")
    
    cpl_matkul_data = [
        # CPL-01 (Kurikulum TI 2020) relationships
        {"id_kurikulum": cpl_list[0].id_kurikulum, "id_cpl": cpl_list[0].id_cpl, "id_matkul": matkul_list[0].id_matkul},  # Algoritma
        {"id_kurikulum": cpl_list[0].id_kurikulum, "id_cpl": cpl_list[0].id_cpl, "id_matkul": matkul_list[1].id_matkul},  # Struktur Data
        {"id_kurikulum": cpl_list[0].id_kurikulum, "id_cpl": cpl_list[0].id_cpl, "id_matkul": matkul_list[7].id_matkul},  # Kecerdasan Buatan
        
        # CPL-02 (Kurikulum TI 2020) relationships
        {"id_kurikulum": cpl_list[1].id_kurikulum, "id_cpl": cpl_list[1].id_cpl, "id_matkul": matkul_list[6].id_matkul},  # RPL
        {"id_kurikulum": cpl_list[1].id_kurikulum, "id_cpl": cpl_list[1].id_cpl, "id_matkul": matkul_list[2].id_matkul},  # Basis Data
        {"id_kurikulum": cpl_list[1].id_kurikulum, "id_cpl": cpl_list[1].id_cpl, "id_matkul": matkul_list[3].id_matkul},  # Pemrograman Web
        
        # CPL-03 (Kurikulum TI 2020) relationships
        {"id_kurikulum": cpl_list[2].id_kurikulum, "id_cpl": cpl_list[2].id_cpl, "id_matkul": matkul_list[7].id_matkul},  # Kecerdasan Buatan
        {"id_kurikulum": cpl_list[2].id_kurikulum, "id_cpl": cpl_list[2].id_cpl, "id_matkul": matkul_list[8].id_matkul},  # Machine Learning
        {"id_kurikulum": cpl_list[2].id_kurikulum, "id_cpl": cpl_list[2].id_cpl, "id_matkul": matkul_list[9].id_matkul},  # Keamanan Informasi
        
        # CPL-04 (Kurikulum SI 2020) relationships
        {"id_kurikulum": cpl_list[3].id_kurikulum, "id_cpl": cpl_list[3].id_cpl, "id_matkul": matkul_list[2].id_matkul},  # Basis Data
        {"id_kurikulum": cpl_list[3].id_kurikulum, "id_cpl": cpl_list[3].id_cpl, "id_matkul": matkul_list[8].id_matkul},  # Machine Learning
        
        # CPL-05 (Kurikulum SI 2020) relationships
        {"id_kurikulum": cpl_list[4].id_kurikulum, "id_cpl": cpl_list[4].id_cpl, "id_matkul": matkul_list[6].id_matkul},  # RPL
        {"id_kurikulum": cpl_list[4].id_kurikulum, "id_cpl": cpl_list[4].id_cpl, "id_matkul": matkul_list[5].id_matkul},  # Jaringan Komputer
    ]
    
    cpl_matkul_list = []
    for data in cpl_matkul_data:
        cpl_matkul = CPLMataKuliah(**data)
        session.add(cpl_matkul)
        cpl_matkul_list.append(cpl_matkul)
    
    session.commit()
    print(f"✓ Seeded {len(cpl_matkul_list)} CPL-MataKuliah relations")
    return cpl_matkul_list


def run_seeder(engine):
    """Jalankan semua seeder"""
    print("\n" + "="*50)
    print("Starting Database Seeding...")
    print("="*50 + "\n")
    
    with Session(engine) as session:
        try:
            # Seed dalam urutan yang benar (respecting foreign keys)
            kurikulum_list = seed_kurikulum(session)
            cpl_list = seed_cpl(session, kurikulum_list)
            indikator_list = seed_indikator_cpl(session, cpl_list)
            matkul_list = seed_mata_kuliah(session)
            cpl_matkul_list = seed_cpl_matkul(session, cpl_list, matkul_list)
            
            print("\n" + "="*50)
            print("✓ Database seeding completed successfully!")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"\n✗ Error during seeding: {e}")
            session.rollback()
            raise

def clear_all_data(engine):
    """Hapus semua data dari tabel (untuk testing)"""
    print("\n" + "="*50)
    print("Clearing all data...")
    print("="*50 + "\n")
    
    with Session(engine) as session:
        try:
            # Hapus dalam urutan terbalik (respecting foreign keys)
            session.query(CPLMataKuliah).delete()
            session.query(IndikatorCPL).delete()
            session.query(MataKuliah).delete()
            session.query(CPL).delete()
            session.query(Kurikulum).delete()
            session.commit()
            
            print("✓ All data cleared successfully!\n")
            
        except Exception as e:
            print(f"✗ Error clearing data: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    from app.db import engine  
    
    run_seeder(engine)