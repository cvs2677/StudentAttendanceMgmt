from typing import Annotated
from fastapi.params import Depends
from sqlalchemy.orm import session
from app.db.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[session, Depends(get_db)]