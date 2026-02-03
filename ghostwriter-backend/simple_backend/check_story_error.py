# CHECK WHY STORY FAILED
from working_database import db_manager

print("🔍 CHECKING STORY ERROR DETAILS...")
print("=" * 60)

db = db_manager.get_session()
try:
    from working_database import Story
    story = db.query(Story).filter(Story.id == 4).first()
    
    if story:
        print(f"📖 Story ID: {story.id}")
        print(f"📖 Title: {story.title}")
        print(f"📖 Status: {story.status}")
        print(f"📖 Type: {story.story_type}")
        print(f"📖 Length: {story.length}")
        print(f"📖 Genre: {story.genre}")
        print(f"📖 Theme: {story.theme}")
        print(f"📖 Error: {story.error_message}")
        print(f"📖 Word Count: {story.word_count}")
        print(f"📖 Chapters: {story.chapters_completed}/{story.total_chapters}")
        
        if story.error_message:
            print(f"\n❌ ERROR DETAILS:")
            print(f"{story.error_message}")
    else:
        print("❌ Story not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
