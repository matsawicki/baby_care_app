from fastapi import FastAPI
from routers.enum import router as enum_router

app = FastAPI()

app.include_router(enum_router, prefix="/api/v1/enums", tags=["Enums"])


