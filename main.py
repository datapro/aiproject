from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

from app.dbconfig.database import engine, Base, get_db
from app.dbconfig.models import User
from app.dbconfig.schemas import UserRegister

# route 
from routes.login import login_router
from routes.login import admin_router
from routes.aimarker import ai_router  # Import the admin_router from aimarker.py
from routes.students import studentrouter


# Create FastAPI application
app = FastAPI(
    title="Member Registration API"
)



# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Automatically create tables
Base.metadata.create_all(bind=engine)

# Register login routes
app.include_router(login_router)
app.include_router(admin_router)
app.include_router(ai_router)  # Include the admin_router from aimarker.py
app.include_router(studentrouter)


@app.get("/")
def home():
    return {
        "message": "FastAPI is running"
    }


@app.post("/register")
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    password_bytes = user.password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    ).decode("utf-8")

    # Create user
    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }