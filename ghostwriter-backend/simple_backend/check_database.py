# CHECK DATABASE CONTENTS - See what we created during testing
from working_database import db_manager

def check_database_contents():
    """Check what's in the database after all testing"""
    print("🔍 CHECKING DATABASE CONTENTS")
    print("=" * 50)
    
    # Get database session
    db = db_manager.get_session()
    
    try:
        # Check users
        from working_database import User
        users = db.query(User).all()
        print(f"👥 Total Users: {len(users)}")
        
        for user in users:
            print(f"  - ID: {user.id}, Email: {user.email}, Name: {user.full_name}")
            print(f"    Created: {user.created_at}, Stories: {user.stories_count}")
        
        print()
        
        # Check stories
        from working_database import Story
        stories = db.query(Story).all()
        print(f"📚 Total Stories: {len(stories)}")
        
        for story in stories:
            print(f"  - ID: {story.id}, Title: {story.title}")
            print(f"    User ID: {story.user_id}, Genre: {story.genre}")
            print(f"    Word Count: {story.word_count}")
            print(f"    Created: {story.created_at}")
            if story.content:
                print(f"    Content Preview: {story.content[:100]}...")
            print()
        
        # Check chapters
        from working_database import Chapter
        chapters = db.query(Chapter).all()
        print(f"📖 Total Chapters: {len(chapters)}")
        
        for chapter in chapters:
            print(f"  - ID: {chapter.id}, Story ID: {chapter.story_id}")
            print(f"    Chapter: {chapter.chapter_number}, Title: {chapter.title}")
            print(f"    Word Count: {chapter.word_count}")
        
        print()
        
        # Check exports
        from working_database import ExportFile
        exports = db.query(ExportFile).all()
        print(f"📁 Total Export Files: {len(exports)}")
        
        for export in exports:
            print(f"  - ID: {export.id}, Story ID: {export.story_id}")
            print(f"    Type: {export.file_type}, Size: {export.file_size}")
        
        print()
        
        # Check API usage
        from working_database import APIUsage
        usage = db.query(APIUsage).all()
        print(f"📊 Total API Calls: {len(usage)}")
        
        # Count by endpoint
        endpoints = {}
        for call in usage:
            endpoint = call.endpoint
            if endpoint not in endpoints:
                endpoints[endpoint] = 0
            endpoints[endpoint] += 1
        
        print("  API Calls by Endpoint:")
        for endpoint, count in endpoints.items():
            print(f"    - {endpoint}: {count} calls")
        
        print()
        print("=" * 50)
        print("📋 SUMMARY:")
        print(f"  Users: {len(users)}")
        print(f"  Stories: {len(stories)}")
        print(f"  Chapters: {len(chapters)}")
        print(f"  Exports: {len(exports)}")
        print(f"  API Calls: {len(usage)}")
        
        # Calculate total words written
        total_words = sum(story.word_count for story in stories if story.word_count)
        print(f"  Total Words Written: {total_words:,}")
        
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database_contents()
