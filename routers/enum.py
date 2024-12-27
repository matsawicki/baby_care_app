from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from typing import List

router = APIRouter()


class EnumCreateRequest(BaseModel):
    enum_name: str = Field(..., max_length=100, example="unit")
    name: str = Field(..., max_length=100, example="kg")


# Mock database (in-memory storage for demonstration purposes)
mock_db: List[dict] = []


@router.post("/enums", status_code=status.HTTP_201_CREATED)
async def create_enum(enum_request: EnumCreateRequest):
    new_enum = {
        "enum_name": enum_request.enum_name,
        "name": enum_request.name,
    }

    mock_db.append(new_enum)
    return new_enum
