import sqlite3
import os

db_path = 'instance/football_stats.db'

def apply_updates():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    updates = [
        # Player table
        ("ALTER TABLE player ADD COLUMN xg_total FLOAT DEFAULT 0.0", "player.xg_total"),
        ("ALTER TABLE player ADD COLUMN pass_accuracy FLOAT DEFAULT 0.0", "player.pass_accuracy"),
        
        # SeasonStats table
        ("ALTER TABLE season_stats ADD COLUMN xg FLOAT DEFAULT 0.0", "season_stats.xg"),
        ("ALTER TABLE season_stats ADD COLUMN pass_accuracy FLOAT DEFAULT 0.0", "season_stats.pass_accuracy"),
        
        ("ALTER TABLE player ADD COLUMN height INTEGER DEFAULT 0", "player.height"),
        ("ALTER TABLE player ADD COLUMN weight INTEGER DEFAULT 0", "player.weight"),
        ("ALTER TABLE player ADD COLUMN preferred_foot TEXT", "player.preferred_foot"),
        
        # Match table
        ("ALTER TABLE match ADD COLUMN home_xg FLOAT DEFAULT 0.0", "match.home_xg"),
        ("ALTER TABLE match ADD COLUMN away_xg FLOAT DEFAULT 0.0", "match.away_xg"),
    ]
    
    for sql, name in updates:
        try:
            cursor.execute(sql)
            print(f"✅ Added {name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"ℹ️ {name} already exists")
            else:
                print(f"❌ Error adding {name}: {e}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    apply_updates()
