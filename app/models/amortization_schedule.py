from sqlalchemy import Column, Integer, Date, Numeric, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import date as date_type
from decimal import Decimal

class AmortizationSchedule(Base):
    __tablename__ = "amortization_schedule"
    
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False, index=True)
    
    payment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    
    scheduled_payment = Column(Numeric(19, 2), nullable=False)
    scheduled_principal = Column(Numeric(19, 2), nullable=False)
    scheduled_interest = Column(Numeric(19, 2), nullable=False)
    insurance_amount = Column(Numeric(19, 2), default=0, nullable=False)
    
    remaining_balance = Column(Numeric(19, 2), nullable=False)
    
    status = Column(String(50), default="pending", nullable=False)
    
    is_grace_period = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    loan = relationship("Loan", back_populates="amortization_schedule")
    payments = relationship("Payment", back_populates="payment_schedule")
    
    def __repr__(self):
        return f"<AmortizationSchedule(loan_id={self.loan_id}, #={self.payment_number}, status={self.status})>"
    
    @property
    def is_overdue(self) -> bool:
        if self.status in ["paid", "cancelled"]:
            return False
        return self.due_date < date_type.today()
    
    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        return (date_type.today() - self.due_date).days
    
    def calculate_penalty(self, penalty_rate: Decimal) -> Decimal:
        if not self.is_overdue or penalty_rate == 0:
            return Decimal("0")
        
        from app.services.calculation_service import CalculationService
        return CalculationService.calculate_late_payment_penalty(
            Decimal(str(self.scheduled_payment)),
            self.days_overdue,
            penalty_rate
        )