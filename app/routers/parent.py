from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, EmailStr
from app.database import SessionLocal
from app.models import Parent
from datetime import datetime
from passlib.context import CryptContext
from typing import Optional

router = APIRouter(
    prefix="/parent", tags=["parent"], responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ParentCreateRequest(BaseModel):
    email: EmailStr = Field(..., example="parent@example.com")
    username: str = Field(..., max_length=100, example="parent_user")
    first_name: str = Field(..., max_length=100, example="John")
    last_name: Optional[str] = Field(None, max_length=100, example="Doe")
    password: str = Field(..., min_length=8, example="securepassword123")
    role: Optional[str] = Field(None, example="parent_role")


class ParentResponse(BaseModel):
    id: str
    email: str
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    role: Optional[str]
    created_datetime: datetime
    modified_datetime: Optional[datetime]

    class Config:
        orm_mode = True


@router.post(
    "/parents", response_model=ParentResponse, status_code=status.HTTP_201_CREATED
)
async def post_parent(parent_request: ParentCreateRequest, db: Session = db_dependency):
    hashed_password = pwd_context.hash(parent_request.password)

    new_parent = Parent(
        email=parent_request.email,
        username=parent_request.username,
        first_name=parent_request.first_name,
        last_name=parent_request.last_name,
        hashed_password=hashed_password,
        role=parent_request.role,
    )

    try:
        db.add(new_parent)
        db.commit()
        db.refresh(new_parent)
        return new_parent
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent with the same email or username already exists.",
        )
