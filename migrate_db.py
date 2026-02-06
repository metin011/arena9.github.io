import sqlite3

# Connect to database
conn = sqlite3.connect('football_stats.db')
cursor = conn.cursor()

try:
    # Add missing columns to season_stats table
    cursor.execute("ALTER TABLE season_stats ADD COLUMN xg REAL DEFAULT 0.0")
    print("✓ Added 'xg' column to season_stats")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("✓ Column 'xg' already exists")
    else:
        print(f"✗ Error adding 'xg': {e}")

try:
    cursor.execute("ALTER TABLE season_stats ADD COLUMN pass_accuracy REAL DEFAULT 0.0")
    print("✓ Added 'pass_accuracy' column to season_stats")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("✓ Column 'pass_accuracy' already exists")
    else:
        print(f"✗ Error adding 'pass_accuracy': {e}")

conn.commit()
conn.close()
print("\n✓ Database migration completed successfully!")
