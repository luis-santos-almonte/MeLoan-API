from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(50), default="simulation")
    
    total_amount = Column(Numeric(19, 2), nullable=False)
    down_payment = Column(Numeric(19, 2), default=0)
    principal = Column(Numeric(19, 2), nullable=False)
    annual_rate = Column(Numeric(8, 4), nullable=False)
    months = Column(Integer, nullable=False)
    
    start_date = Column(Date, nullable=True)
    payment_day = Column(Integer, default=1, nullable=False)
    payment_frequency = Column(String(50), default="monthly", nullable=False)
    organization_fee = Column(Numeric(19, 2), default=0, nullable=False)
    insurance_monthly = Column(Numeric(19, 2), default=0, nullable=False)
    
    rate_type = Column(String(50), default="fixed", nullable=False) 
    interest_calculation_method = Column(String(50), default="30/360", nullable=False)
    grace_period_months = Column(Integer, default=0, nullable=False)
    late_payment_penalty_rate = Column(Numeric(8, 4), default=0, nullable=False)
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    amortization_schedule = relationship("AmortizationSchedule", back_populates="loan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Loan(id={self.id}, name='{self.name}', principal={self.principal})>"
    
    @property
    def monthly_payment(self) -> float:
        from decimal import Decimal, ROUND_HALF_UP
        P = Decimal(str(self.principal))
        r = Decimal(str(self.annual_rate)) / 100 / 12
        n = self.months
        insurance = Decimal(str(self.insurance_monthly))
        
        if r == 0:
            base_payment = P / n
        else:
            base_payment = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        
        total = (base_payment + insurance).quantize(Decimal('0.01'), ROUND_HALF_UP)
        return float(total)