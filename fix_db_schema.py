import sqlite3
import os

db_path = 'football_stats.db'

def check_and_fix_db():
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(match)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'lineups' not in columns:
            print("'lineups' column missing. Adding it...")
            cursor.execute("ALTER TABLE match ADD COLUMN lineups TEXT DEFAULT '{\"home\": [], \"away\": []}'")
            conn.commit()
            print("Successfully added 'lineups' column.")
        else:
            print("'lineups' column already exists.")
            
    except sqlite3.OperationalError as e:
        print(f"SQLite Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_and_fix_db()
