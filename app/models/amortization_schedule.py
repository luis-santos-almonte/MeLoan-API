from sqlalchemy import Column, Integer, Date, Numeric, String, DateTime, ForeignKey
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
    
    remaining_balance = Column(Numeric(19, 2), nullable=False)
    
    status = Column(String(50), default="pending", nullable=False)
    
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
    
    @property
    def accrued_interest_to_date(self) -> Decimal:
        from datetime import date as date_type
        
        if self.status == "paid":
            return Decimal(str(self.scheduled_interest))
        
        today = date_type.today()
        
        if today < self.due_date:
            return Decimal("0")
        
        return Decimal(str(self.scheduled_interest))