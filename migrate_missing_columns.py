#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete Database Migration Script
Adds ALL missing columns to player and match tables
"""
import sqlite3
import os

# Database paths to check
db_paths = [
    'instance/football_stats.db',
    'instance/database.db',
    'football_stats.db',
    'database.db'
]

# Complete list of columns for each table
PLAYER_COLUMNS = {
    'height': 'INTEGER DEFAULT 0',
    'weight': 'INTEGER DEFAULT 0',
    'preferred_foot': 'VARCHAR(10)',
    'xg_total': 'FLOAT DEFAULT 0.0',
    'pass_accuracy': 'FLOAT DEFAULT 0.0',
    'position_map': 'TEXT DEFAULT "{}"',
    'detailed_skills': 'TEXT DEFAULT "{}"',
}

MATCH_COLUMNS = {
    'home_xg': 'FLOAT DEFAULT 0.0',
    'away_xg': 'FLOAT DEFAULT 0.0',
    'lineups': 'TEXT DEFAULT \'{"home": [], "away": []}\'',
    'timeline': 'TEXT DEFAULT "[]"',
}

def migrate_database(db_path):
    """Add ALL missing columns to database"""
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"\n🔧 Migrating: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player';")
        has_player = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='match';")
        has_match = cursor.fetchone() is not None
        
        if not has_player and not has_match:
            print(f"  ⚠️  No player or match tables found")
            conn.close()
            return False
        
        # Migrate player table
        if has_player:
            print("  📊 Migrating player table...")
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(player);")
            existing_cols = [col[1] for col in cursor.fetchall()]
            
            # Add missing columns
            for col_name, col_type in PLAYER_COLUMNS.items():
                if col_name not in existing_cols:
                    try:
                        cursor.execute(f"ALTER TABLE player ADD COLUMN {col_name} {col_type};")
                        print(f"    ✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"    ⚠️  Could not add {col_name}: {e}")
        
        # Migrate match table
        if has_match:
            print("  ⚽ Migrating match table...")
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(match);")
            existing_cols = [col[1] for col in cursor.fetchall()]
            
            # Add missing columns
            for col_name, col_type in MATCH_COLUMNS.items():
                if col_name not in existing_cols:
                    try:
                        cursor.execute(f"ALTER TABLE match ADD COLUMN {col_name} {col_type};")
                        print(f"    ✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"    ⚠️  Could not add {col_name}: {e}")
        
        conn.commit()
        print(f"  ✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    print("=" * 60)
    print("🚀 Arena9 Complete Database Migration")
    print("=" * 60)
    
    migrated_count = 0
    for db_path in db_paths:
        if migrate_database(db_path):
            migrated_count += 1
    
    print("\n" + "=" * 60)
    if migrated_count > 0:
        print(f"✅ Successfully migrated {migrated_count} database(s)!")
        print("🔄 Please restart the Flask server for changes to take effect.")
    else:
        print("⚠️  No databases were migrated.")
    print("=" * 60)

if __name__ == "__main__":
    main()
