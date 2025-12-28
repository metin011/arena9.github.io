import sqlite3
import os

db_path = 'football_stats.db'

def create_audit_table():
    if not os.path.exists(db_path):
        print(f"❌ Database {db_path} tapılmadı.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'")
        if cursor.fetchone():
            print("✅ 'audit_log' cədvəli artıq mövcuddur.")
        else:
            print("📝 'audit_log' cədvəli yaradılır...")
            cursor.execute("""
                CREATE TABLE audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action VARCHAR(50) NOT NULL,
                    target_type VARCHAR(50) NOT NULL,
                    target_id INTEGER,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES user(id)
                )
            """)
            conn.commit()
            print("✅ 'audit_log' cədvəli uğurla yaradıldı!")
            
    except sqlite3.Error as e:
        print(f"❌ SQLite xətası: {e}")
    except Exception as e:
        print(f"❌ Ümumi xəta: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_audit_table()
