from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from passlib.context import CryptContext
import jwt
from groq import Groq
import os

# Initialize FastAPI
app = FastAPI(title="Simple Story Generator", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allow OPTIONS
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)

# Database
DATABASE_URL = "postgresql://neondb_owner:npg_P8aIqQ5cXSDm@ep-cold-hat-aeuoyp65-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DATABASE_URL, echo=False)  # Disable echo for cleaner logs
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"❌ Database error: {e}")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    plot = Column(Text)
    when_where = Column(Text)
    characters = Column(Text)
    genre = Column(String)
    writing_style = Column(String)
    timeline = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Auth
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class StoryRequest(BaseModel):
    plot: str
    when_where: str
    characters: str
    genre: str
    writing_style: str
    timeline: str

# Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", "your-groq-api-key-here"))

# Story Generation
def generate_story_content(request: StoryRequest):
    prompt = f"""
    Write a {request.genre} story with the following details:
    
    Plot: {request.plot}
    Setting (When & Where): {request.when_where}
    Characters: {request.characters}
    Writing Style: {request.writing_style}
    Timeline: {request.timeline}
    
    Write a complete, engaging story that incorporates all these elements.
    """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a master storyteller. Write engaging, well-crafted stories."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Story generation failed: {str(e)}")

# Routes
@app.post("/api/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        email=user.email,
        password=hashed_password,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    token = jwt.encode({"user_id": new_user.id}, SECRET_KEY)
    return {"access_token": token, "user": {"id": new_user.id, "email": new_user.email}}

@app.post("/api/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({"user_id": db_user.id}, SECRET_KEY)
    return {"access_token": token, "user": {"id": db_user.id, "email": db_user.email}}

@app.post("/api/stories/generate")
def generate_story(request: StoryRequest, db: Session = Depends(get_db)):
    try:
        # Generate story content
        content = generate_story_content(request)
        
        # Save story (for now, without user auth - we'll add this later)
        story = Story(
            user_id=1,  # Temporary
            plot=request.plot,
            when_where=request.when_where,
            characters=request.characters,
            genre=request.genre,
            writing_style=request.writing_style,
            timeline=request.timeline,
            content=content
        )
        db.add(story)
        db.commit()
        db.refresh(story)
        
        return {
            "id": story.id,
            "content": content,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Simple Story Generator API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
