from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.amortization_schedule import AmortizationSchedule

class AmortizationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[AmortizationSchedule]:
        return self.db.query(AmortizationSchedule).filter(AmortizationSchedule.id == id).first()
    
    def get_by_loan(self, loan_id: int) -> List[AmortizationSchedule]:
        return (
            self.db.query(AmortizationSchedule)
            .filter(AmortizationSchedule.loan_id == loan_id)
            .order_by(AmortizationSchedule.payment_number)
            .all()
        )
    
    def get_by_payment_number(self, loan_id: int, payment_number: int) -> Optional[AmortizationSchedule]:
        return (
            self.db.query(AmortizationSchedule)
            .filter(
                AmortizationSchedule.loan_id == loan_id,
                AmortizationSchedule.payment_number == payment_number
            )
            .first()
        )
    
    def get_pending(self, loan_id: int) -> List[AmortizationSchedule]:
        return (
            self.db.query(AmortizationSchedule)
            .filter(
                AmortizationSchedule.loan_id == loan_id,
                AmortizationSchedule.status == "pending"
            )
            .order_by(AmortizationSchedule.payment_number)
            .all()
        )
    
    def get_overdue(self, loan_id: int) -> List[AmortizationSchedule]:
        from datetime import date
        return (
            self.db.query(AmortizationSchedule)
            .filter(
                AmortizationSchedule.loan_id == loan_id,
                AmortizationSchedule.status.in_(["pending", "partial"]),
                AmortizationSchedule.due_date < date.today()
            )
            .order_by(AmortizationSchedule.payment_number)
            .all()
        )
    
    def create(self, schedule: AmortizationSchedule) -> AmortizationSchedule:
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def create_batch(self, schedules: List[AmortizationSchedule]) -> List[AmortizationSchedule]:
        self.db.add_all(schedules)
        self.db.commit()
        for schedule in schedules:
            self.db.refresh(schedule)
        return schedules
    
    def update_status(self, id: int, status: str) -> Optional[AmortizationSchedule]:
        schedule = self.get_by_id(id)
        if not schedule:
            return None
        schedule.status = status
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def count_by_loan(self, loan_id: int) -> int:
        return self.db.query(AmortizationSchedule).filter(AmortizationSchedule.loan_id == loan_id).count()