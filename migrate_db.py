
import sqlite3
import os

db_paths = [
    'football_stats.db', 
    os.path.join('instance', 'football_stats.db'),
    'database.db',
    os.path.join('instance', 'database.db')
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        print(f"Skipping: {db_path} (not found)")
        continue
    
    print(f"Migrating: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE match ADD COLUMN lineups TEXT;")
        print("  Added lineups column.")
    except sqlite3.OperationalError as e:
        print(f"  lineups column: {e}")

    try:
        cursor.execute("ALTER TABLE match ADD COLUMN timeline TEXT;")
        print("  Added timeline column.")
    except sqlite3.OperationalError as e:
        print(f"  timeline column: {e}")

    conn.commit()
    conn.close()

print("Migration process finished.")
