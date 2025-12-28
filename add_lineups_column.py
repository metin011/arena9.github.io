import sqlite3

try:
    conn = sqlite3.connect('football_stats.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE match ADD COLUMN lineups TEXT")
    conn.commit()
    print("Migration successful: Added 'lineups' column to 'match' table.")
except sqlite3.OperationalError as e:
    print(f"Migration skipped: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
