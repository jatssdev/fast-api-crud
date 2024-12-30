from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database setup
DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True, index=True)

# Schemas
class UserBase(BaseModel):
    name: str
    email: str
    mobile_number: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

# Database utilities
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD Operations
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email, mobile_number=user.mobile_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserCreate):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.name = user.name
        db_user.email = user.email
        db_user.mobile_number = user.mobile_number
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

@app.post("/users/", response_model=UserResponse)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    return db_user

@app.get("/users/", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return get_users(db)

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_existing_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", response_model=UserResponse)
def delete_existing_user(user_id: int, db: Session = Depends(get_db)):
    db_user = delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
