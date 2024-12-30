# FastAPI CRUD Backend Tutorial

This tutorial will guide you through creating a CRUD (Create, Read, Update, Delete) API using **FastAPI** from scratch. We'll start from setting up the environment to implementing all the CRUD operations.

---

## Prerequisites

Ensure you have the following installed on your system:

- **Python 3.9+**
- **pip** (Python package manager)

You should also have basic knowledge of Python, RESTful APIs, and basic SQL concepts.

---

## Step 1: Setting Up the Environment

### 1.1 Create a Project Directory

Start by creating a new directory for your FastAPI project and navigate into it:

```bash
mkdir fastapi_crud_tutorial
cd fastapi_crud_tutorial
```

### 1.2 Create a Virtual Environment

Set up a virtual environment to manage project dependencies:

```bash
python3 -m venv env
source env/bin/activate
```

### 1.3 Install FastAPI and Uvicorn

Install FastAPI and Uvicorn (the ASGI server) along with SQLAlchemy for database management:

```bash
pip install fastapi uvicorn sqlalchemy
```

### 1.4 Create the Main Application File

Create a single Python file for your project:

```bash
touch app.py
```

---

## Step 2: Setting Up the Database

We will use SQLite for simplicity. Here's how to set up the database connection:

### 2.1 Add Database Setup Code

Open `app.py` and add the following code for database configuration:

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL
DATABASE_URL = "sqlite:///./users.db"

# Database Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session Maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class for Models
Base = declarative_base()
```

This setup creates the SQLite database `users.db` and configures the SQLAlchemy ORM.

---

## Step 3: Defining the Models

### 3.1 Create the User Model

Add the following code to define the `User` table:

```python
# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True, index=True)
```

This creates a `users` table with fields: `id`, `name`, `email`, and `mobile_number`.

### 3.2 Create the Database Tables

Initialize the database tables by calling `Base.metadata.create_all`:

```python
# Create tables
Base.metadata.create_all(bind=engine)
```

---

## Step 4: Pydantic Schemas for Validation

### 4.1 Add User Schemas

Use **Pydantic** for request and response validation:

```python
from pydantic import BaseModel

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
```

These schemas will ensure that API requests and responses have the correct structure.

---

## Step 5: CRUD Operations

### 5.1 Add Database Utility Functions

Define utility functions for database operations:

```python
from sqlalchemy.orm import Session

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
```

---

## Step 6: Building the API Endpoints

### 6.1 Initialize the FastAPI App

Start by importing FastAPI and setting up the application:

```python
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()
```

### 6.2 Add Dependency for Database Session

Add a dependency to provide a database session:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 6.3 Create API Endpoints

Add the following routes to handle CRUD operations:

```python
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
```

---

## Step 7: Running the Application

### 7.1 Start the Server

Run the following command to start the development server:

```bash
uvicorn app:app --reload
```

### 7.2 Test the API

Visit the interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Step 8: Save Dependencies

Save your project dependencies:

```bash
pip freeze > requirements.txt
```

---

## Conclusion

Congratulations! You have successfully built a FastAPI CRUD API. This backend serves as a solid foundation for more advanced features like authentication, deployment, and integration with a frontend application. Keep exploring and happy coding!

