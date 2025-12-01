from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class LoanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str
    
    total_amount: Decimal = Field(..., gt=0)
    down_payment: Decimal = Field(default=Decimal("0"), ge=0)
    principal: Decimal = Field(..., gt=0)
    
    annual_rate: Decimal = Field(..., gt=0, le=100)
    months: int = Field(..., gt=0, le=600)
    
    start_date: Optional[date] = None
    payment_day: int = Field(default=1, ge=1, le=31)
    payment_frequency: str = Field(default="monthly")
    
    origination_fee: Decimal = Field(default=Decimal("0"), ge=0)
    insurance_monthly: Decimal = Field(default=Decimal("0"), ge=0)
    
    rate_type: str = Field(default="fixed")
    interest_calculation_method: str = Field(default="30/360")
    grace_period_months: int = Field(default=0, ge=0)
    late_payment_penalty_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = ["mortgage", "auto", "personal"]
        if v not in allowed:
            raise ValueError(f"Loan type must be one of: {allowed}")
        return v
    
    @field_validator("payment_frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        allowed = ["monthly", "biweekly", "weekly"]
        if v not in allowed:
            raise ValueError(f"Payment frequency must be one of: {allowed}")
        return v
    
    @field_validator("rate_type")
    @classmethod
    def validate_rate_type(cls, v: str) -> str:
        allowed = ["fixed", "variable"]
        if v not in allowed:
            raise ValueError(f"Rate type must be one of: {allowed}")
        return v
    
    @field_validator("interest_calculation_method")
    @classmethod
    def validate_interest_method(cls, v: str) -> str:
        allowed = ["30/360", "actual/365", "actual/360"]
        if v not in allowed:
            raise ValueError(f"Interest calculation method must be one of: {allowed}")
        return v
    
    @field_validator("grace_period_months")
    @classmethod
    def validate_grace_period(cls, v: int, info) -> int:
        if "months" in info.data and v >= info.data["months"]:
            raise ValueError("Grace period cannot be greater than or equal to the total term")
        return v
    
    @field_validator("principal")
    @classmethod
    def validate_principal(cls, v: Decimal, info) -> Decimal:
        if "total_amount" in info.data and "down_payment" in info.data:
            expected = info.data["total_amount"] - info.data["down_payment"]
            if abs(v - expected) > Decimal("0.01"):
                raise ValueError(f"Principal must be total_amount - down_payment")
        return v

class LoanCreate(LoanBase):
    status: str = Field(default="simulation")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["simulation", "active"]
        if v not in allowed:
            raise ValueError(f"Initial status must be one of: {allowed}")
        return v

class LoanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = None
    status: Optional[str] = None
    total_amount: Optional[Decimal] = Field(None, gt=0)
    down_payment: Optional[Decimal] = Field(None, ge=0)
    principal: Optional[Decimal] = Field(None, gt=0)
    annual_rate: Optional[Decimal] = Field(None, gt=0, le=100)
    months: Optional[int] = Field(None, gt=0, le=600)
    
    start_date: Optional[date] = None
    payment_day: Optional[int] = Field(None, ge=1, le=31)
    payment_frequency: Optional[str] = None
    origination_fee: Optional[Decimal] = Field(None, ge=0)
    insurance_monthly: Optional[Decimal] = Field(None, ge=0)
    
    rate_type: Optional[str] = None
    interest_calculation_method: Optional[str] = None
    grace_period_months: Optional[int] = Field(None, ge=0)
    late_payment_penalty_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["mortgage", "auto", "personal"]
            if v not in allowed:
                raise ValueError(f"Type must be one of: {allowed}")
        return v
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["simulation", "active", "paid_off", "cancelled"]
            if v not in allowed:
                raise ValueError(f"Status must be one of: {allowed}")
        return v
    
    @field_validator("payment_frequency")
    @classmethod
    def validate_frequency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["monthly", "biweekly", "weekly"]
            if v not in allowed:
                raise ValueError(f"Payment frequency must be one of: {allowed}")
        return v
    
    @field_validator("rate_type")
    @classmethod
    def validate_rate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["fixed", "variable"]
            if v not in allowed:
                raise ValueError(f"Rate type must be one of: {allowed}")
        return v
    
    @field_validator("interest_calculation_method")
    @classmethod
    def validate_interest_method(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["30/360", "actual/365", "actual/360"]
            if v not in allowed:
                raise ValueError(f"Interest calculation method must be one of: {allowed}")
        return v

class LoanResponse(LoanBase):
    id: int
    user_id: int
    status: str
    start_date: Optional[date] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    monthly_payment: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)

class LoanListResponse(BaseModel):
    items: list[LoanResponse]
    total: int
    skip: int
    limit: int

class LoanSummary(BaseModel):
    id: int
    name: str
    type: str
    status: str
    principal: Decimal
    annual_rate: Decimal
    months: int
    start_date: Optional[date] = None
    rate_type: str
    monthly_payment: Optional[Decimal] = None
    created_at: datetime
    is_deleted: bool
    
    model_config = ConfigDict(from_attributes=True)