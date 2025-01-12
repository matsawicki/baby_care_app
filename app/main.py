from fastapi import FastAPI
import app.models as models
from app.database import engine
from app.routers import enum, event, parent, kid_permission, kid

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.include_router(enum.router)
app.include_router(event.router)
app.include_router(parent.router)
app.include_router(kid_permission.router)
app.include_router(kid.router)
