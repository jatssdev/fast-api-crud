from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()
# Configure CORS
origins = [
    "http://127.0.0.1:5500",  # Add the exact URL where your HTML is served (e.g., Live Server)
    "http://localhost:5500",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)
# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic models for input validation
class UserCreate(BaseModel):
    name: str
    email: str
    mobile_number: str

class UserUpdate(BaseModel):
    name: str
    email: str
    mobile_number: str

# Add a new user
@app.post("/users/")
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.mobile_number == user.mobile_number)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or mobile number already exists")
    new_user = User(name=user.name, email=user.email, mobile_number=user.mobile_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User added successfully", "user": new_user}

# Index route
@app.get("/")
def index():
    return "Hello, Magan!"

# Get all users
@app.get("/users/")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Get a single user by ID
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update a user
@app.put("/users/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = user_update.name
    user.email = user_update.email
    user.mobile_number = user_update.mobile_number
    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully", "user": user}

# Delete a user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
