# ADD MISSING CHAPTERS COLUMN
from working_database import db_manager
from sqlalchemy import text

print("🔧 ADDING MISSING 'chapters' COLUMN...")

db = db_manager.get_session()
try:
    # Add the missing chapters column
    db.execute(text("ALTER TABLE stories ADD COLUMN chapters JSON"))
    db.commit()
    print("✅ Added 'chapters' column to stories table")
    
    print("🎉 DATABASE SCHEMA NOW COMPLETE!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
