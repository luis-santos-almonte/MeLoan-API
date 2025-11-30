from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
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
    
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Loan(id={self.id}, name='{self.name}', principal={self.principal})>"
    
    @property
    def monthly_payment(self) -> float:
        from decimal import Decimal, ROUND_HALF_UP
        P = Decimal(str(self.principal))
        r = Decimal(str(self.annual_rate)) / 100 / 12
        n = self.months
        if r == 0:
            return float(P / n)
        payment = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return float(payment.quantize(Decimal('0.01'), ROUND_HALF_UP))