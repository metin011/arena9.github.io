
import sqlite3
import os

db_paths = [
    'football_stats.db', 
    os.path.join('instance', 'football_stats.db'),
    'database.db',
    os.path.join('instance', 'database.db')
]

with open('verify_log.txt', 'w') as f:
    for db_path in db_paths:
        if not os.path.exists(db_path):
            f.write(f"{db_path}: NOT FOUND\n")
            continue
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='match';")
            if not cursor.fetchone():
                f.write(f"{db_path}: Table 'match' DOES NOT EXIST\n")
            else:
                cursor.execute("PRAGMA table_info(match);")
                cols = [c[1] for c in cursor.fetchall()]
                f.write(f"{db_path}: Match columns: {cols}\n")
        except Exception as e:
            f.write(f"{db_path}: Error: {e}\n")
        conn.close()
    f.write("Verification finished.\n")
