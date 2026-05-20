from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.core.config import get_settings

settings = get_settings()

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CricketIQ X — CSK Analyst Edition",
    description="AI-powered IPL tactical intelligence for Chennai Super Kings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "product": "CricketIQ X",
        "edition": "CSK Analyst Edition",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}