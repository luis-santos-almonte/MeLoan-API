from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.schemas.amortization import (
    AmortizationScheduleResponse,
    AmortizationScheduleListResponse,
    AmortizationSummary
)
from app.repositories.amortization_repository import AmortizationRepository
from app.repositories.loan_repository import LoanRepository
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/api/loans/{loan_id}/amortization", tags=["amortization"])


@router.get("/", response_model=AmortizationScheduleListResponse)
async def get_amortization_schedule(
    loan_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AmortizationScheduleListResponse:
    loan_repo = LoanRepository(db)
    loan = loan_repo.get_by_id(loan_id)
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo {loan_id} no encontrado"
        )
    
    if loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este préstamo"
        )
    
    amortization_repo = AmortizationRepository(db)
    schedules = amortization_repo.get_by_loan(loan_id)
    
    return AmortizationScheduleListResponse(
        items=[AmortizationScheduleResponse.model_validate(s) for s in schedules],
        total=len(schedules),
        loan_id=loan_id
    )


@router.get("/summary", response_model=AmortizationSummary)
async def get_amortization_summary(
    loan_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AmortizationSummary:
    loan_repo = LoanRepository(db)
    loan = loan_repo.get_by_id(loan_id)
    
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo {loan_id} no encontrado"
        )
    
    amortization_repo = AmortizationRepository(db)
    schedules = amortization_repo.get_by_loan(loan_id)
    
    total_payments = len(schedules)
    total_to_pay = sum(Decimal(str(s.scheduled_payment)) for s in schedules)
    total_interest = sum(Decimal(str(s.scheduled_interest)) for s in schedules)
    total_principal = sum(Decimal(str(s.scheduled_principal)) for s in schedules)
    
    paid_schedules = [s for s in schedules if s.status == "paid"]
    payments_made = len(paid_schedules)
    amount_paid = sum(Decimal(str(s.scheduled_payment)) for s in paid_schedules)
    
    pending_schedules = [s for s in schedules if s.status in ["pending", "partial", "overdue"]]
    payments_pending = len(pending_schedules)
    amount_pending = sum(Decimal(str(s.scheduled_payment)) for s in pending_schedules)
    
    return AmortizationSummary(
        total_payments=total_payments,
        total_to_pay=total_to_pay,
        total_interest=total_interest,
        total_principal=total_principal,
        payments_made=payments_made,
        payments_pending=payments_pending,
        amount_paid=amount_paid,
        amount_pending=amount_pending
    )


@router.get("/pending", response_model=List[AmortizationScheduleResponse])
async def get_pending_payments(
    loan_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[AmortizationScheduleResponse]:
    loan_repo = LoanRepository(db)
    loan = loan_repo.get_by_id(loan_id)
    
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo {loan_id} no encontrado"
        )
    
    amortization_repo = AmortizationRepository(db)
    schedules = amortization_repo.get_pending(loan_id)
    
    return [AmortizationScheduleResponse.model_validate(s) for s in schedules]


@router.get("/overdue", response_model=List[AmortizationScheduleResponse])
async def get_overdue_payments(
    loan_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[AmortizationScheduleResponse]:
    loan_repo = LoanRepository(db)
    loan = loan_repo.get_by_id(loan_id)
    
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo {loan_id} no encontrado"
        )
    
    amortization_repo = AmortizationRepository(db)
    schedules = amortization_repo.get_overdue(loan_id)
    
    return [AmortizationScheduleResponse.model_validate(s) for s in schedules]


@router.get("/{payment_number}", response_model=AmortizationScheduleResponse)
async def get_payment_by_number(
    loan_id: int,
    payment_number: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AmortizationScheduleResponse:
    loan_repo = LoanRepository(db)
    loan = loan_repo.get_by_id(loan_id)
    
    if not loan or loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo {loan_id} no encontrado"
        )
    
    amortization_repo = AmortizationRepository(db)
    schedule = amortization_repo.get_by_payment_number(loan_id, payment_number)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuota #{payment_number} no encontrada"
        )
    
    return AmortizationScheduleResponse.model_validate(schedule)