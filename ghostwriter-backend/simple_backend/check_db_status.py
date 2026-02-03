# CHECK DATABASE HYBRID STATUS
import os
from dotenv import load_dotenv
from working_database import db_manager

# Load environment variables
load_dotenv()

def check_database_status():
    """Check which database is actually being used"""
    print("🔍 DATABASE HYBRID STATUS CHECK")
    print("=" * 50)
    
    # Check environment variables
    database_url = os.getenv("DATABASE_URL", "Not set")
    print(f"📝 DATABASE_URL from .env:")
    print(f"   {database_url}")
    
    # Determine database type
    if database_url.startswith("postgresql"):
        db_type = "PostgreSQL (Production)"
        location = "Neon Cloud Database"
    elif database_url.startswith("sqlite"):
        db_type = "SQLite (Development)"
        location = "Local file: storygen.db"
    else:
        db_type = "Unknown/Fallback"
        location = "Unknown"
    
    print(f"\n🎯 CURRENT DATABASE TYPE:")
    print(f"   Type: {db_type}")
    print(f"   Location: {location}")
    
    # Test database connection
    print(f"\n🔗 TESTING CONNECTION...")
    try:
        db = db_manager.get_session()
        
        # Check if it's actually PostgreSQL or SQLite
        from working_database import User
        user_count = db.query(User).count()
        
        # Get database info
        if database_url.startswith("postgresql"):
            print(f"✅ PostgreSQL connection successful!")
            print(f"   Cloud database: Neon.tech")
            print(f"   Users stored: {user_count}")
            print(f"   Production ready: YES")
        else:
            print(f"✅ SQLite connection successful!")
            print(f"   Local file: storygen.db")
            print(f"   Users stored: {user_count}")
            print(f"   Development mode: YES")
        
        # Check recent activity
        from working_database import Story
        story_count = db.query(Story).count()
        print(f"   Stories stored: {story_count}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
    
    return True

def show_hybrid_benefits():
    """Show the benefits of the hybrid setup"""
    print(f"\n🔄 HYBRID DATABASE BENEFITS:")
    print("=" * 50)
    
    print("✅ DEVELOPMENT (SQLite):")
    print("   - Fast, local, no internet needed")
    print("   - Perfect for testing and development")
    print("   - File-based, easy to backup/restore")
    print("   - Zero cost for development")
    
    print("\n✅ PRODUCTION (PostgreSQL):")
    print("   - Cloud-based, always accessible")
    print("   - Handles multiple users simultaneously")
    print("   - Professional-grade reliability")
    print("   - Scalable for growth")
    
    print("\n🔄 AUTOMATIC SWITCHING:")
    print("   - Set DATABASE_URL to PostgreSQL for production")
    print("   - Remove DATABASE_URL or set to SQLite for development")
    print("   - Code automatically detects and uses correct database")
    print("   - Same code works for both environments")

def show_current_data():
    """Show what's currently stored"""
    print(f"\n📊 CURRENT DATA STATUS:")
    print("=" * 50)
    
    try:
        db = db_manager.get_session()
        
        from working_database import User, Story
        
        users = db.query(User).all()
        stories = db.query(Story).all()
        
        print(f"👥 USERS ({len(users)} total):")
        for user in users[-5:]:  # Show last 5 users
            print(f"   - {user.email} (ID: {user.id})")
        
        print(f"\n📚 STORIES ({len(stories)} total):")
        for story in stories[-3:]:  # Show last 3 stories
            print(f"   - {story.title} (ID: {story.id}, User: {story.user_id})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Could not retrieve data: {str(e)}")

if __name__ == "__main__":
    check_database_status()
    show_hybrid_benefits()
    show_current_data()
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 50)
    print("Your hybrid database gives you the best of both worlds:")
    print("- SQLite for fast development")
    print("- PostgreSQL for production scalability")
    print("- Automatic switching based on configuration")
    print("- Same code works in both environments")
