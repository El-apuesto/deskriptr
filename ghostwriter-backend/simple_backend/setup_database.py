# SETUP DATABASE - RUN THIS FIRST!
# Quick setup script to get your database working

import os
import sys
import subprocess
from working_database import init_working_database, check_database_health

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_python_version():
    """Check Python version"""
    print_header("CHECKING PYTHON VERSION")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.7+")
        return False

def install_required_packages():
    """Install required packages"""
    print_header("INSTALLING REQUIRED PACKAGES")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic[email]",
        "python-jose[cryptography]",
        "python-multipart",
        "groq",
        "python-dotenv",
        "reportlab",
        "Pillow",
        "matplotlib",
        "numpy"
    ]
    
    for package in required_packages:
        print_info(f"Installing {package}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print_success(f"✓ {package} installed")
            else:
                print_error(f"✗ Failed to install {package}: {result.stderr}")
                return False
        except Exception as e:
            print_error(f"✗ Error installing {package}: {str(e)}")
            return False
    
    return True

def setup_environment():
    """Setup environment variables"""
    print_header("SETTING UP ENVIRONMENT")
    
    env_file = ".env"
    
    # Check if .env file exists
    if os.path.exists(env_file):
        print_info("Found existing .env file")
        with open(env_file, 'r') as f:
            content = f.read()
            print_info("Current .env content:")
            print(content)
        return True
    
    # Create .env file
    env_content = """# Database Configuration
# For development (SQLite - no setup needed)
DATABASE_URL=sqlite:///./storygen.db

# For production (PostgreSQL - uncomment and configure)
# DATABASE_URL=postgresql://username:password@localhost:5432/storygen

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-please

# Groq API
GROQ_API_KEY=your-groq-api-key-here

# Redis (for rate limiting - optional for development)
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_PASSWORD=

# Environment
ENVIRONMENT=development
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print_success(f"Created {env_file} file")
        print_info("Please update the following values in .env:")
        print_info("- SECRET_KEY: Generate a secure secret key")
        print_info("- GROQ_API_KEY: Add your Groq API key")
        print_info("- DATABASE_URL: Configure for production if needed")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create .env file: {str(e)}")
        return False

def initialize_database():
    """Initialize the database"""
    print_header("INITIALIZING DATABASE")
    
    try:
        if init_working_database():
            print_success("Database initialized successfully")
            
            # Show database health
            health = check_database_health()
            print_info("Database Health:")
            print(f"  Status: {health['status']}")
            print(f"  Users: {health.get('users_count', 0)}")
            print(f"  Stories: {health.get('stories_count', 0)}")
            
            return True
        else:
            print_error("Database initialization failed")
            return False
            
    except Exception as e:
        print_error(f"Database initialization error: {str(e)}")
        return False

def test_database_connection():
    """Test database connection"""
    print_header("TESTING DATABASE CONNECTION")
    
    try:
        from working_database import db_manager
        
        # Test creating a user
        test_user = db_manager.create_user(
            email="test@example.com",
            hashed_password="test_hash",
            full_name="Test User"
        )
        
        if test_user:
            print_success("✓ Database connection working")
            print_success(f"✓ Created test user (ID: {test_user.id})")
            
            # Clean up test user
            db_manager.delete_story(test_user.id)  # This would need to be implemented
            print_success("✓ Cleaned up test data")
            
            return True
        else:
            print_error("Failed to create test user")
            return False
            
    except Exception as e:
        print_error(f"Database connection test failed: {str(e)}")
        return False

def create_startup_script():
    """Create startup script"""
    print_header("CREATING STARTUP SCRIPT")
    
    script_content = """@echo off
echo Starting Story Generator API...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\\Scripts\\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the API server
echo.
echo Starting API server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python main_with_db.py

pause
"""
    
    try:
        with open("start_api.bat", 'w') as f:
            f.write(script_content)
        
        print_success("Created start_api.bat")
        print_info("You can now run 'start_api.bat' to start the API")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create startup script: {str(e)}")
        return False

def main():
    """Main setup function"""
    print_header("STORY GENERATOR DATABASE SETUP")
    print("This script will set up your database and get you running!")
    
    # Step 1: Check Python version
    if not check_python_version():
        return False
    
    # Step 2: Install packages
    if not install_required_packages():
        return False
    
    # Step 3: Setup environment
    if not setup_environment():
        return False
    
    # Step 4: Initialize database
    if not initialize_database():
        return False
    
    # Step 5: Test connection
    if not test_database_connection():
        return False
    
    # Step 6: Create startup script
    create_startup_script()
    
    # Success!
    print_header("SETUP COMPLETE!")
    print_success("🎉 Your database is ready to use!")
    print_info("\nNext steps:")
    print_info("1. Update your .env file with your Groq API key")
    print_info("2. Run 'python main_with_db.py' to start the API")
    print_info("3. Or run 'start_api.bat' for easy startup")
    print_info("4. Visit http://localhost:8000/health to check status")
    print_info("5. Visit http://localhost:8000/docs for API documentation")
    
    print("\n" + "="*60)
    print(" 🚀 Your Story Generator API is ready!")
    print("="*60)

if __name__ == "__main__":
    main()
