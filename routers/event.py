from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel, Field
from database import SessionLocal
from models import Event
from datetime import datetime, timezone
import uuid

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)

class EventCreateRequest(BaseModel):
    kid_id: str = Field(..., example="kid123")
    event_type_id: str = Field(..., example="event123")
    timestamp: datetime = Field(..., example="2024-12-01T14:30:00Z")
    string_value: Optional[str] = Field(None, max_length=255, example="sample string")
    float_value: Optional[float] = Field(None, example=10.5)
    bool_value: Optional[bool] = Field(None, example=True)
    int_value: Optional[int] = Field(None, example=42)
    unit_id: Optional[str] = Field(None, example="unit123")


class EventResponse(BaseModel):
    id: str
    kid_id: str
    event_type_id: str
    timestamp: datetime
    string_value: Optional[str]
    float_value: Optional[float]
    bool_value: Optional[bool]
    int_value: Optional[int]
    unit_id: Optional[str]
    created_datetime: datetime
    modified_datetime: Optional[datetime]

    class Config:
        orm_mode = True


@router.get(
    "/events/", response_model=List[EventResponse], status_code=status.HTTP_200_OK
)
async def get_all_events(
    kid_id: Optional[str] = None,
    event_type_id: Optional[str] = None,
    db: Session = db_dependency,
):
    query = select(Event).where(not Event.is_deleted)
    if kid_id:
        query = query.where(Event.kid_id == kid_id)
    if event_type_id:
        query = query.where(Event.event_type_id == event_type_id)

    results = db.execute(query).scalars().all()
    return results


@router.get(
    "/events/{id}", response_model=EventResponse, status_code=status.HTTP_200_OK
)
async def get_event(id: str, db: Session = db_dependency):
    event = db.get(Event, id)
    if not event or event.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id '{id}' not found.",
        )
    return event


@router.post(
    "/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED
)
async def post_event(event_request: EventCreateRequest, db: Session = db_dependency):
    new_event = Event(
        id=str(uuid.uuid4()),
        kid_id=event_request.kid_id,
        event_type_id=event_request.event_type_id,
        timestamp=event_request.timestamp,
        string_value=event_request.string_value,
        float_value=event_request.float_value,
        bool_value=event_request.bool_value,
        int_value=event_request.int_value,
        unit_id=event_request.unit_id,
        created_datetime=datetime.now(timezone.utc),
    )

    try:
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return new_event
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or duplicate event data.",
        )


@router.put(
    "/events/{id}", response_model=EventResponse, status_code=status.HTTP_202_ACCEPTED
)
async def put_event(
    id: str,
    event_request: EventCreateRequest,
    db: Session = db_dependency,
):
    event_to_update = db.get(Event, id)
    if not event_to_update or event_to_update.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id '{id}' not found.",
        )

    event_to_update.kid_id = event_request.kid_id
    event_to_update.event_type_id = event_request.event_type_id
    event_to_update.timestamp = event_request.timestamp
    event_to_update.string_value = event_request.string_value
    event_to_update.float_value = event_request.float_value
    event_to_update.bool_value = event_request.bool_value
    event_to_update.int_value = event_request.int_value
    event_to_update.unit_id = event_request.unit_id
    event_to_update.modified_datetime = datetime.now(timezone.utc)

    db.commit()
    db.refresh(event_to_update)
    return event_to_update


@router.delete("/events/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(id: str, db: Session = db_dependency):
    event_to_delete = db.get(Event, id)
    if not event_to_delete or event_to_delete.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id '{id}' not found.",
        )

    event_to_delete.is_deleted = True
    event_to_delete.modified_datetime = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Event deleted successfully."}