from typing import Generator
from sqlalchemy.orm import Session

from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user():
    class DummyUser:
        id = 1
        email = "test@example.com"
    return DummyUser()