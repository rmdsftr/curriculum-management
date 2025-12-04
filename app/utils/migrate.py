import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from app.db import init_db, drop_db, engine
from sqlmodel import text, inspect

def check_tables():
    """Check existing tables in database"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return tables
    except Exception as e:
        print(f"Error checking tables: {e}")
        return []

def show_table_info():
    """Show detailed table information"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("  No tables found in database")
            return
        
        for table in tables:
            print(f"\n  Table: {table}")
            columns = inspector.get_columns(table)
            print(f"  Columns ({len(columns)}):")
            for col in columns:
                col_type = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"    - {col['name']}: {col_type} {nullable}")
            
            fks = inspector.get_foreign_keys(table)
            if fks:
                print(f"  Foreign Keys:")
                for fk in fks:
                    print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    except Exception as e:
        print(f"Error showing table info: {e}")

def migrate():
    """Run migration - create/update tables"""
    print("\n" + "="*60)
    print(" DATABASE MIGRATION")
    print("="*60 + "\n")
    
    print("📋 Checking existing tables...")
    tables_before = check_tables()
    
    if tables_before:
        print(f"Found {len(tables_before)} existing table(s):")
        for table in tables_before:
            print(f"  ✓ {table}")
    else:
        print("  No existing tables found")
    
    print("\n🔧 Creating/Updating tables...")
    try:
        init_db()
        
        print("\n📋 Tables after migration:")
        tables_after = check_tables()
        for table in tables_after:
            if table in tables_before:
                print(f"  ✓ {table} (existing)")
            else:
                print(f"  ✓ {table} (new)")
        
        print("\n" + "="*60)
        print(" ✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("\n" + "="*60)
        print(" ❌ MIGRATION FAILED!")
        print("="*60 + "\n")
        raise

def reset():
    """Drop all tables and recreate"""
    print("\n" + "="*60)
    print(" DATABASE RESET (DROP + CREATE)")
    print("="*60 + "\n")
    
    tables = check_tables()
    if tables:
        print(f"⚠️  This will DELETE {len(tables)} table(s):")
        for table in tables:
            print(f"  - {table}")
    else:
        print("No existing tables to drop")
    
    print("\n⚠️  WARNING: All data will be lost!")
    confirm = input("Type 'yes' to confirm reset: ")
    
    if confirm.lower() == 'yes':
        print("\n🗑️  Dropping all tables...")
        try:
            drop_db()
            
            print("🔧 Creating tables...")
            init_db()
            
            print("\n📋 New tables:")
            tables_after = check_tables()
            for table in tables_after:
                print(f"  ✓ {table}")
            
            print("\n" + "="*60)
            print(" ✅ RESET COMPLETED SUCCESSFULLY!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error during reset: {e}")
            print("\n" + "="*60)
            print(" ❌ RESET FAILED!")
            print("="*60 + "\n")
            raise
    else:
        print("\n❌ Reset cancelled.")

def status():
    """Show database status and table information"""
    print("\n" + "="*60)
    print(" DATABASE STATUS")
    print("="*60 + "\n")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection: OK")
            print(f"Database: PostgreSQL")
            print(f"Version: {version.split(',')[0]}\n")
        
        tables = check_tables()
        print(f"📊 Total tables: {len(tables)}\n")
        
        if tables:
            show_table_info()
        else:
            print("  No tables found in database")
        
        print("\n" + "="*60)
        print(" STATUS CHECK COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n" + "="*60)
        print(" ❌ STATUS CHECK FAILED")
        print("="*60 + "\n")

def drop():
    """Drop all tables only"""
    print("\n" + "="*60)
    print(" DROP ALL TABLES")
    print("="*60 + "\n")
    
    tables = check_tables()
    if tables:
        print(f"⚠️  This will DELETE {len(tables)} table(s):")
        for table in tables:
            print(f"  - {table}")
    else:
        print("No tables to drop")
        return
    
    print("\n⚠️  WARNING: All data will be lost!")
    confirm = input("Type 'DROP' to confirm: ")
    
    if confirm == 'DROP':
        print("\n🗑️  Dropping all tables...")
        try:
            drop_db()
            
            remaining = check_tables()
            if not remaining:
                print("\n✅ All tables dropped successfully")
            else:
                print(f"\n⚠️  {len(remaining)} table(s) remaining:")
                for table in remaining:
                    print(f"  - {table}")
            
            print("\n" + "="*60)
            print(" DROP COMPLETED")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error dropping tables: {e}")
            print("\n" + "="*60)
            print(" ❌ DROP FAILED!")
            print("="*60 + "\n")
            raise
    else:
        print("\n❌ Drop cancelled.")

def help_text():
    """Show help information"""
    print("\n" + "="*60)
    print(" DATABASE MIGRATION TOOL - HELP")
    print("="*60 + "\n")
    print("Usage: python -m app.utils.migrate [command]\n")
    print("Available commands:")
    print("  (no args)    Run migration (create/update tables)")
    print("  --status     Show database status and table information")
    print("  --reset      Drop all tables and recreate")
    print("  --drop       Drop all tables only")
    print("  --help       Show this help message")
    print("\nExamples:")
    print("  python -m app.utils.migrate")
    print("  python -m app.utils.migrate --status")
    print("  python -m app.utils.migrate --reset")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Database Migration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m app.utils.migrate              
  python -m app.utils.migrate --status     
  python -m app.utils.migrate --reset      
  python -m app.utils.migrate --drop       
        """
    )
    
    parser.add_argument('--reset', action='store_true', 
                       help='Drop all tables and recreate')
    parser.add_argument('--status', action='store_true', 
                       help='Show database status and table information')
    parser.add_argument('--drop', action='store_true', 
                       help='Drop all tables only')
    parser.add_argument('--help-text', action='store_true',
                       help='Show detailed help information')
    
    args = parser.parse_args()
    
    try:
        if args.help_text:
            help_text()
        elif args.status:
            status()
        elif args.reset:
            reset()
        elif args.drop:
            drop()
        else:
            migrate()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)