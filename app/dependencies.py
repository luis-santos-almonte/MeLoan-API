from typing import Generator
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.loan_repository import LoanRepository
from app.repositories.amortization_repository import AmortizationRepository
from app.services.loan_service import LoanService
from app.services.calculation_service import CalculationService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_loan_repository(db: Session = None) -> LoanRepository:
    if db is None:
        db = next(get_db())
    return LoanRepository(db=db)

def get_amortization_repository(db: Session = None) -> AmortizationRepository:
    if db is None:
        db = next(get_db())
    return AmortizationRepository(db=db)

def get_calculation_service() -> CalculationService:
    return CalculationService()

def get_loan_service(db: Session = None) -> LoanService:
    if db is None:
        db = next(get_db())
    
    loan_repo = get_loan_repository(db)
    amortization_repo = get_amortization_repository(db)
    calc_service = get_calculation_service()
    
    return LoanService(
        loan_repository=loan_repo,
        amortization_repository=amortization_repo,
        calculation_service=calc_service
    )

def get_current_user():
    class DummyUser:
        id = 1
        email = "test@example.com"
    return DummyUser()