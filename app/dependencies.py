from typing import Generator
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.loan_repository import LoanRepository
from app.services.loan_service import LoanService

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

def get_loan_repository(db: Session = next(get_db())) -> LoanRepository:
    if db is None:
        db = next(get_db())
    return LoanRepository(db)

def get_loan_service(db: Session = next(get_db())) -> LoanService:
    if db is None:
        db = next(get_db())
    loan_repo = get_loan_repository(db)
    return LoanService(loan_repo)