# DROP AND RECREATE DATABASE WITH CORRECT SCHEMA
from working_database import db_manager

print("🔧 DROPPING AND RECREATING DATABASE...")

db = db_manager.get_session()
try:
    # Drop all tables
    from working_database import Base
    Base.metadata.drop_all(bind=db_manager.engine)
    print("✅ Dropped all tables")
    
    # Recreate all tables with new schema
    Base.metadata.create_all(bind=db_manager.engine)
    print("✅ Recreated all tables with correct schema")
    
    print("🎉 DATABASE SCHEMA FIXED!")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
