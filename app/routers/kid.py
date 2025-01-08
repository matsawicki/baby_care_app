from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.database import SessionLocal
from app.models import Kid, Parent, KidPermission, Enum

router = APIRouter(
    prefix="/kid", tags=["kid"], responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)


class KidCreateRequest(BaseModel):
    first_name: str = Field(..., max_length=100, example="John")
    last_name: Optional[str] = Field(None, max_length=100, example="Doe")
    birth_date: Optional[datetime] = Field(None, example="2015-06-15T00:00:00Z")
    parent_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174001")
    role_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174002")


class KidResponse(BaseModel):
    id: str
    first_name: str
    last_name: Optional[str]
    birth_date: Optional[datetime]
    parent_id: Optional[str]
    created_datetime: datetime
    modified_datetime: Optional[datetime]

    class Config:
        orm_mode = True


@router.post("/kids", response_model=KidResponse, status_code=status.HTTP_201_CREATED)
async def create_kid(kid_request: KidCreateRequest, db: Session = db_dependency):
    new_kid = Kid(
        first_name=kid_request.first_name,
        last_name=kid_request.last_name,
        birth_date=kid_request.birth_date,
        parent_id=kid_request.parent_id,
    )

    try:
        # Check if the parent exists
        parent = db.query(Parent).filter(Parent.id == kid_request.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent ID does not exist.",
            )

        # Check if the role_id is valid
        valid_role = db.query(Enum).filter(Enum.id == kid_request.role_id).first()
        if not valid_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided role_id does not exist.",
            )

        # Create the new kid
        db.add(new_kid)
        db.commit()
        db.refresh(new_kid)

        # Assign the permission to the parent
        new_permission = KidPermission(
            kid_id=new_kid.id,
            parent_id=kid_request.parent_id,
            role_id=kid_request.role_id,
        )
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)

        return new_kid
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Constraints were violated, such as duplicate data.",
        )




@router.put(
    "/kids/{id}", response_model=KidResponse, status_code=status.HTTP_202_ACCEPTED
)
async def update_kid(
    id: str,
    kid_request: KidCreateRequest,
    db: Session = db_dependency,
):
    kid_to_update = db.get(Kid, id)
    if not kid_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kid with id '{id}' not found.",
        )

    kid_to_update.first_name = kid_request.first_name
    kid_to_update.last_name = kid_request.last_name
    kid_to_update.birth_date = kid_request.birth_date
    kid_to_update.parent_id = kid_request.parent_id

    db.commit()
    db.refresh(kid_to_update)
    return kid_to_update


@router.delete("/kids/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kid(id: str, db: Session = db_dependency):
    kid_to_delete = db.get(Kid, id)
    if not kid_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kid with id '{id}' not found.",
        )

    kid_to_delete.is_deleted = True
    db.commit()
    return {"message": "Kid deleted successfully."}
