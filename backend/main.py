from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os

app = FastAPI()

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/voting_app")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model for votes
class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    team = Column(String, index=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic model for vote input
class VoteInput(BaseModel):
    team: str

# Endpoints
@app.post("/vote/")
async def cast_vote(vote: VoteInput):
    if vote.team not in ["A", "B"]:
        raise HTTPException(status_code=400, detail="Invalid team. Use 'A' or 'B'.")
    db = SessionLocal()
    try:
        db_vote = Vote(team=vote.team)
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return {"message": f"Voted for Team {vote.team}"}
    finally:
        db.close()

@app.get("/results/")
async def get_results():
    db = SessionLocal()
    try:
        team_a_count = db.query(Vote).filter(Vote.team == "A").count()
        team_b_count = db.query(Vote).filter(Vote.team == "B").count()
        return {"team_a": team_a_count, "team_b": team_b_count}
    finally:
        db.close()

@app.post("/reset/")
async def reset_votes():
    db = SessionLocal()
    try:
        db.query(Vote).delete()
        db.commit()
        return {"message": "All votes reset"}
    finally:
        db.close()