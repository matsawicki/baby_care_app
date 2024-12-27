from fastapi import FastAPI
from routers import enum

app = FastAPI()

app.include_router(enum.router)


