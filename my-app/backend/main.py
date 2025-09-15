from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.responses import JSONResponse

# -------------------
# SQLite setup
# -------------------
DATABASE_URL = "sqlite:///./submissions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    nisit_id = Column(String(10), unique=True, index=True, nullable=False)
    password = Column(String(8), nullable=False)
    time_sec = Column(Float, nullable=False)
    collected = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# -------------------
# FastAPI setup
# -------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# Pydantic model
# -------------------
class PasswordEntry(BaseModel):
    nisitId: constr(min_length=10, max_length=10)
    password: constr(min_length=1, max_length=8)

# -------------------
# Password crack estimation
# -------------------
CHARSETS = {"lower": 26, "upper": 26, "digits": 10, "symbols": 33}

def estimate_crack_time(password: str, guesses_per_sec: int = 1e10) -> float:
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += CHARSETS['lower']
    if any(c.isupper() for c in password):
        charset_size += CHARSETS['upper']
    if any(c.isdigit() for c in password):
        charset_size += CHARSETS['digits']
    if any(not c.isalnum() for c in password):
        charset_size += CHARSETS['symbols']
    combinations = charset_size ** len(password)
    return combinations / guesses_per_sec

# -------------------
# API Endpoints
# -------------------
@app.post("/submit_password/")
def submit_password(entry: PasswordEntry):
    db = SessionLocal()

    # Check duplicate Nisit ID
    existing = db.query(Submission).filter(Submission.nisit_id == entry.nisitId).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="This Nisit ID has already played.")

    # Estimate crack time
    time_sec = estimate_crack_time(entry.password)

    # Save submission
    new_submission = Submission(
        nisit_id=entry.nisitId,
        password=entry.password,
        time_sec=time_sec
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    # Calculate rank
    submissions = db.query(Submission).order_by(Submission.time_sec.desc()).all()
    rank = [s.nisit_id for s in submissions].index(entry.nisitId) + 1
    db.close()

    return {"estimated_time_sec": time_sec, "rank": rank}

@app.get("/leaderboard/")
def get_leaderboard():
    db = SessionLocal()
    submissions = db.query(Submission).order_by(Submission.time_sec.desc()).all()
    result = [
        {"nisitId": s.nisit_id, "password": s.password, "time_sec": s.time_sec} 
        for s in submissions
    ]
    db.close()
    return result

@app.get("/check_status/{nisit_id}")
def check_status(nisit_id: str):
    db = SessionLocal()
    existing = db.query(Submission).filter(Submission.nisit_id == nisit_id).first()
    if not existing:
        db.close()
        return JSONResponse({"played": False})

    # Determine if winner
    submissions = db.query(Submission).order_by(Submission.time_sec.asc()).all()
    winner_id = submissions[0].nisit_id if submissions else None
    is_winner = nisit_id == winner_id
    db.close()
    return {"played": True, "winner": is_winner}

@app.post("/collect_reward/{nisit_id}")
def collect_reward(nisit_id: str):
    db = SessionLocal()
    submission = db.query(Submission).filter(Submission.nisit_id == nisit_id).first()
    if not submission:
        db.close()
        raise HTTPException(status_code=404, detail="Nisit ID not found")

    if submission.collected:
        db.close()
        raise HTTPException(status_code=400, detail="Reward already collected")

    submission.collected = True
    db.commit()
    db.refresh(submission)
    db.close()

    return {"message": "Reward collected successfully!"}
