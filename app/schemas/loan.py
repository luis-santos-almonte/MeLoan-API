from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import date, datetime
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
    organization_fee: Decimal = Field(default=Decimal("0"), ge=0)
    insurance_monthly: Decimal = Field(default=Decimal("0"), ge=0)
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = ["mortgage", "auto", "personal"]
        if v not in allowed:
            raise ValueError(f"Loan type must be one of: {allowed}")
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
    organization_fee: Optional[Decimal] = Field(None, ge=0)
    insurance_monthly: Optional[Decimal] = Field(None, ge=0)
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["mortgage", "auto", "personal"]
            if v not in allowed:
                raise ValueError(f"Loan type must be one of: {allowed}")
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
    def validate_payment_frequency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["monthly", "biweekly", "weekly"]
            if v not in allowed:
                raise ValueError(f"Payment frequency must be one of: {allowed}")
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
    monthly_payment: Optional[Decimal] = None
    created_at: datetime
    is_deleted: bool
    
    model_config = ConfigDict(from_attributes=True)