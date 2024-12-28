from fastapi import FastAPI
import models
from database import engine
from routers import enum, event_type

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(enum.router)
app.include_router(event_type.router)


