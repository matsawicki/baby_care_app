from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from pydantic import BaseModel

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.post("/parents")
def create_parent(data: Parent, db: Session = Depends(get_db)):
    new_parent = Parent(
        email=data.email,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=data.password,
        role=data.role,
    )
    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)
    return {"message": "Parent created", "parent_id": new_parent.id}
