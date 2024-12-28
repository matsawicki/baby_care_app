from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel, Field
from database import SessionLocal
from models import Enum, EnumHistory
from datetime import datetime, timezone
import uuid

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)


class EnumCreateRequest(BaseModel):
    enum_name: str = Field(..., max_length=100, example="unit")
    name: str = Field(..., max_length=100, example="kg")


class EnumResponse(BaseModel):
    id: str
    enum_name: str
    name: str
    created_datetime: datetime
    modified_datetime: Optional[datetime]

    class Config:
        orm_mode = True


class EnumHistoryResponse(BaseModel):
    id: str
    enum_id: str
    enum_name: str
    name: str
    valid_from: datetime
    valid_to: Optional[datetime]
    is_deleted: bool

    class Config:
        orm_mode = True


def update_enum_history(
    db: Session, enum: Enum, is_deleted: bool = False
):
    db.query(EnumHistory).filter(
        EnumHistory.enum_id == enum.id, EnumHistory.valid_to.is_(None)
    ).update({"valid_to": datetime.now(timezone.utc)})

    new_history = EnumHistory(
        id=str(uuid.uuid4()),
        enum_id=enum.id,
        enum_name=enum.enum_name,
        name=enum.name,
        valid_from=datetime.now(timezone.utc),
        valid_to=None,
        is_deleted=is_deleted,
    )
    db.add(new_history)
    db.commit()


@router.get(
    "/enums/", response_model=List[EnumResponse], status_code=status.HTTP_200_OK
)
async def get_all_enums(
    enum_name: Optional[str] = None,
    name: Optional[str] = None,
    db: Session = db_dependency,
):
    query = select(Enum)
    if enum_name:
        query = query.where(Enum.enum_name == enum_name)
    if name:
        query = query.where(Enum.name == name)

    results = db.execute(query).scalars().all()
    return results


@router.get("/enums/{id}", response_model=EnumResponse, status_code=status.HTTP_200_OK)
async def get_enum(id: str, db: Session = db_dependency):
    result = db.get(Enum, id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enum with id '{id}' not found.",
        )
    return result


@router.post("/enums", response_model=EnumResponse, status_code=status.HTTP_201_CREATED)
async def post_enum(enum_request: EnumCreateRequest, db: Session = db_dependency):
    new_enum = Enum(
        id=str(uuid.uuid4()),
        enum_name=enum_request.enum_name,
        name=enum_request.name,
        created_datetime=datetime.now(timezone.utc),
    )

    try:
        db.add(new_enum)
        db.commit()
        db.refresh(new_enum)
        update_enum_history(db, new_enum)
        return new_enum
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enum with the same name and enum_name already exists.",
        )


@router.put(
    "/enums/{id}", response_model=EnumResponse, status_code=status.HTTP_202_ACCEPTED
)
async def put_enum(
    id: str,
    enum_request: EnumCreateRequest,
    db: Session = db_dependency,
):
    enum_to_update = db.get(Enum, id)
    if not enum_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enum with id '{id}' not found.",
        )

    enum_to_update.enum_name = enum_request.enum_name
    enum_to_update.name = enum_request.name
    enum_to_update.modified_datetime = datetime.now(timezone.utc)

    db.commit()
    db.refresh(enum_to_update)
    update_enum_history(db, enum_to_update)
    return enum_to_update


@router.delete("/enums/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enum(id: str, db: Session = db_dependency):
    enum_to_delete = db.get(Enum, id)
    if not enum_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enum with id '{id}' not found.",
        )

    update_enum_history(db, enum_to_delete, is_deleted=True)
    db.delete(enum_to_delete)
    db.commit()
    return {"message": "Enum deleted successfully."}


@router.get(
    "/enums/{id}/history",
    response_model=List[EnumHistoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_enum_history(id: str, db: Session = db_dependency):
    query = (
        select(EnumHistory)
        .where(EnumHistory.enum_id == id)
        .order_by(EnumHistory.valid_from.asc())
    )
    results = db.execute(query).scalars().all()

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No history found for enum with id '{id}'.",
        )

    return results
