# CHECK ACTUAL DATABASE SCHEMA
from working_database import db_manager

print("🔍 CHECKING ACTUAL DATABASE SCHEMA...")
print("=" * 60)

db = db_manager.get_session()
try:
    # Get actual table schema
    from sqlalchemy import text
    result = db.execute(text("PRAGMA table_info(stories)"))
    columns = result.fetchall()
    
    print("📋 ACTUAL COLUMNS IN 'stories' TABLE:")
    print("-" * 40)
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    print(f"\n📊 TOTAL COLUMNS: {len(columns)}")
    
    # Check if chapters column exists
    has_chapters = any(col[1] == 'chapters' for col in columns)
    print(f"✅ Has 'chapters' column: {has_chapters}")
    
    if not has_chapters:
        print("\n❌ MISSING 'chapters' COLUMN!")
        print("This is why your original system is failing.")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
