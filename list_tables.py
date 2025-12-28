
import sqlite3
import os

db_paths = ['database.db', os.path.join('instance', 'database.db')]
for db_path in db_paths:
    if not os.path.exists(db_path):
        print(f"Skipping: {db_path} (not found)")
        continue
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in {db_path}:", [t[0] for t in tables])
    conn.close()
