import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models import Database

if __name__ == '__main__':
    print("Initializing database...")
    Database.init_db()
    print("✓ Database initialized successfully")
