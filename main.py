from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import models
from database import engine
from routers import enum, event, parent, kid_permission, kid

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(enum.router)
app.include_router(event.router)
app.include_router(parent.router)
app.include_router(kid_permission.router)
app.include_router(kid.router)


