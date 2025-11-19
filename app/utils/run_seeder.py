import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from app.db import engine
from app.utils.seeder import run_seeder, clear_all_data

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Seeder')
    parser.add_argument('--clear', action='store_true', help='Clear all data before seeding')
    args = parser.parse_args()
    
    if args.clear:
        clear_all_data(engine)
    
    run_seeder(engine)