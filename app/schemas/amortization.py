from pydantic import BaseModel, ConfigDict, computed_field
from datetime import date
from decimal import Decimal

class AmortizationScheduleBase(BaseModel):
    payment_number: int
    due_date: date
    scheduled_payment: Decimal
    scheduled_principal: Decimal
    scheduled_interest: Decimal
    remaining_balance: Decimal
    status: str

class AmortizationScheduleResponse(AmortizationScheduleBase):
    id: int
    loan_id: int
    
    model_config = ConfigDict(from_attributes=True)
    
    @computed_field
    @property
    def is_overdue(self) -> bool:
        if self.status in ["paid", "cancelled"]:
            return False
        return self.due_date < date.today()
    
    @computed_field
    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days
    
    @computed_field
    @property
    def accrued_interest_to_date(self) -> Decimal:
        if self.status == "paid":
            return self.scheduled_interest
        
        today = date.today()
        
        if today < self.due_date:
            return Decimal("0")
        
        return self.scheduled_interest

class AmortizationScheduleListResponse(BaseModel):
    items: list[AmortizationScheduleResponse]
    total: int
    loan_id: int
    
class AmortizationSummary(BaseModel):
    total_payments: int
    total_to_pay: Decimal
    total_interest: Decimal
    total_principal: Decimal
    payments_made: int
    payments_pending: int
    amount_paid: Decimal
    amount_pending: Decimal