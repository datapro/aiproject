from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from auth.security import create_access_token
import bcrypt

from app.dbconfig.database import get_db
from app.dbconfig.models import User
from app.dbconfig.models import EssayMarking


# security
from auth.security import require_admin

# Create router
login_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@login_router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # Find user by email
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check password
    password_valid = bcrypt.checkpw(
        user.password.encode("utf-8"),
        existing_user.password.encode("utf-8")
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
      # ==============================
    # CREATE JWT
    # ==============================

    access_token = create_access_token(
        data={
            "sub": str(existing_user.id),
            "role": existing_user.role
        }
    )



    # Check role
    if existing_user.role == "admin":
        redirect_url = "/admin"

    elif existing_user.role == "student":
        redirect_url = "/student"

    else:
        redirect_url = "/dashboard"

    return {
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": existing_user.id,
            "name": existing_user.name,
            "email": existing_user.email,
            "role": existing_user.role
        },
        "redirect": redirect_url
    }


@admin_router.get("/")
def admin_dashboard(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # =========================
    # STATISTICS
    # =========================

    total_users = db.query(User).count()
    # total exams
    total_examinations = db.query(EssayMarking).count()
    # total PASS
    total_pass = (
    db.query(EssayMarking)
    .filter(EssayMarking.grade.in_(["A", "B", "C", "D"]))
    .count()
    )
    # total fail
    total_fail = (
    db.query(EssayMarking)
    .filter(EssayMarking.grade.in_(["F"]))
    .count()
    )

    total_students = (
        db.query(User)
        .filter(User.role == "student")
        .count()
    )

    total_admins = (
        db.query(User)
        .filter(User.role == "admin")
        .count()
    )

    # =========================
    # PAGINATION
    # =========================

    total_pages = (
        (total_users + limit - 1) // limit
        if total_users > 0
        else 1
    )

    offset = (page - 1) * limit

    recent_users = (
        db.query(User)
        .order_by(User.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    

    return {
        "total_examinations": total_examinations,
        "total_pass":total_pass,
        "total_fail":total_fail,
        "admin": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        },

        "statistics": {
            "total_users": total_users,
            "total_students": total_students,
            "total_admins": total_admins
        },

        "pagination": {
            "page": page,
            "limit": limit,
            "total_users": total_users,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        },

        "recent_users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at
            }
            for user in recent_users
        ]
    }

@admin_router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete yourself"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }