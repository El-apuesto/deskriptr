# SHOW CURRENT DATABASE CONTENTS
from working_database import db_manager

def show_current_data():
    """Display all current data in database"""
    print("📊 CURRENT DATABASE CONTENTS")
    print("=" * 60)
    
    db = db_manager.get_session()
    
    try:
        # Get users
        from working_database import User
        users = db.query(User).all()
        print(f"👥 USERS ({len(users)} total):")
        print("-" * 40)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Name: {user.full_name}")
            print(f"Stories: {user.stories_count}")
            print(f"Tier: {user.subscription_tier}")
            print(f"Created: {user.created_at}")
            print(f"Last Login: {user.last_login or 'Never'}")
            print("-" * 40)
        
        print(f"\n📚 STORIES:")
        from working_database import Story
        stories = db.query(Story).all()
        print(f"Total Stories: {len(stories)}")
        print("-" * 40)
        
        for story in stories:
            print(f"ID: {story.id}")
            print(f"Title: {story.title}")
            print(f"User ID: {story.user_id}")
            print(f"Genre: {story.genre}")
            print(f"Word Count: {story.word_count}")
            print(f"Created: {story.created_at}")
            
            # Show content preview
            if story.content:
                preview = story.content[:100] + "..." if len(story.content) > 100 else story.content
                print(f"Content: {preview}")
            print("-" * 40)
        
        print(f"\n📖 CHAPTERS:")
        from working_database import Chapter
        chapters = db.query(Chapter).all()
        print(f"Total Chapters: {len(chapters)}")
        for chapter in chapters:
            print(f"ID: {chapter.id}, Story: {chapter.story_id}, Chapter: {chapter.chapter_number}")
        
        print(f"\n📁 EXPORTS:")
        from working_database import ExportFile
        exports = db.query(ExportFile).all()
        print(f"Total Exports: {len(exports)}")
        for export in exports:
            print(f"ID: {export.id}, Story: {export.story_id}, Type: {export.file_type}")
        
        print(f"\n📊 API USAGE:")
        from working_database import APIUsage
        usage = db.query(APIUsage).all()
        print(f"Total API Calls: {len(usage)}")
        
        # Group by endpoint
        endpoints = {}
        for call in usage:
            endpoint = call.endpoint
            if endpoint not in endpoints:
                endpoints[endpoint] = 0
            endpoints[endpoint] += 1
        
        for endpoint, count in endpoints.items():
            print(f"  {endpoint}: {count} calls")
        
        print(f"\n🎯 SUMMARY:")
        print("=" * 60)
        print(f"Users: {len(users)}")
        print(f"Stories: {len(stories)}")
        print(f"Total Words: {sum(story.word_count for story in stories)}")
        print(f"Chapters: {len(chapters)}")
        print(f"Exports: {len(exports)}")
        print(f"API Calls: {len(usage)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    show_current_data()
