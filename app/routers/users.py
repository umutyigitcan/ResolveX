from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    check_query = text("""
        SELECT id
        FROM users
        WHERE email = :email
    """)

    existing_user = db.execute(
        check_query,
        {"email": user.email}
    ).fetchone()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    insert_query = text("""
        INSERT INTO users (
            name,
            surname,
            email,
            password,
            role
        )
        VALUES (
            :name,
            :surname,
            :email,
            :password,
            'customer'
        )
        RETURNING id, name, surname, email, role
    """)

    result = db.execute(
        insert_query,
        {
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "password": hashed_password
        }
    )

    db.commit()

    new_user = result.fetchone()

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT id, email, password
        FROM users
        WHERE email = :email
    """)

    db_user = db.execute(
        query,
        {"email": credentials.email}
    ).fetchone()

    if db_user is None or not verify_password(
        credentials.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": str(db_user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }