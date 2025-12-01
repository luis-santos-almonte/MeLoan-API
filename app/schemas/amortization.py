from pydantic import BaseModel, ConfigDict
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
    is_overdue: bool
    days_overdue: int
    accrued_interest_to_date: Decimal
    
    model_config = ConfigDict(from_attributes=True)

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