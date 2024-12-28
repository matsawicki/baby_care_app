from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from database import SessionLocal
from models import KidPermission
from datetime import datetime
from typing import Optional

router = APIRouter(
    prefix="/kid_permission",
    tags=["kid_permission"],
    responses={404: {"description": "Not found"}}
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)

class KidPermissionCreateRequest(BaseModel):
    kid_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    parent_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174001")
    role_id: str = Field(..., example="123e4567-e89b-12d3-a456-426614174002")


class KidPermissionResponse(BaseModel):
    id: str
    kid_id: str
    parent_id: str
    role_id: str
    created_datetime: datetime
    modified_datetime: Optional[datetime]

    class Config:
        orm_mode = True


@router.post(
    "/kid_permissions",
    response_model=KidPermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_kid_permission(
    kid_permission_request: KidPermissionCreateRequest, db: Session = db_dependency
):
    new_kid_permission = KidPermission(
        kid_id=kid_permission_request.kid_id,
        parent_id=kid_permission_request.parent_id,
        role_id=kid_permission_request.role_id,
    )

    try:
        db.add(new_kid_permission)
        db.commit()
        db.refresh(new_kid_permission)
        return new_kid_permission
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KidPermission with the same kid_id, parent_id, and role_id already exists.",
        )
