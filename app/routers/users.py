from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserResponse

router=APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.post("/register",response_model=UserResponse)
def register(
        user:UserCreate,
        db: Session = Depends(get_db)
):
    check_query=text("""
    SELECT id 
    FROM users 
    WHERE email=:email
    """)

    existing_user=db.execute(
        check_query,
        {"email":user.email}
    ).fetchone()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    hashed_password = hash_password(user.password)

    insert_query=text("""
    INSERT INTO users(name,surname,email,password,role)
    VALUES(:name,:surname,:email,:password,'customer')
    RETURNING id,name,surname,email,role
    """)

    result=db.execute(
        insert_query,
        {
            "name":user.name,
            "surname":user.surname,
            "email":user.email,
            "password":hashed_password
        }
    )

    db.commit()

    new_user=result.fetchone()

    return new_user