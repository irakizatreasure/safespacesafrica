import os
from app import DEFAULT_DB, init_db

if __name__ == "__main__":
    init_db(os.environ.get("SISP_DB_PATH", DEFAULT_DB))
    print(f"Database initialized and starter content seeded at {os.environ.get('SISP_DB_PATH', DEFAULT_DB)}")
