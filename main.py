from fastapi import FastAPI
import models
from database import engine
from routers import enum, event, parent

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(enum.router)
app.include_router(event.router)
app.include_router(parent.router)

