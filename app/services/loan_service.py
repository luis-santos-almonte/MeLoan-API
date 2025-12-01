from typing import Optional, List
from decimal import Decimal
from datetime import date

from app.models.loan import Loan
from app.models.amortization_schedule import AmortizationSchedule
from app.schemas.loan import LoanCreate, LoanUpdate, LoanResponse, LoanListResponse, LoanSummary
from app.repositories.loan_repository import LoanRepository
from app.repositories.amortization_repository import AmortizationRepository
from app.services.calculation_service import CalculationService

class LoanService:
    def __init__(
        self, 
        loan_repository: LoanRepository,
        amortization_repository: AmortizationRepository,
        calculation_service: CalculationService
    ):
        self.loan_repo = loan_repository
        self.amortization_repo = amortization_repository
        self.calc_service = calculation_service
    
    def create_loan(self, loan_data: LoanCreate, user_id: int) -> LoanResponse:
        loan = Loan(
            user_id=user_id,
            name=loan_data.name,
            type=loan_data.type,
            status=loan_data.status,
            total_amount=loan_data.total_amount,
            down_payment=loan_data.down_payment,
            principal=loan_data.principal,
            annual_rate=loan_data.annual_rate,
            months=loan_data.months,
            start_date=loan_data.start_date,
            payment_day=loan_data.payment_day,
            payment_frequency=loan_data.payment_frequency,
            origination_fee=loan_data.origination_fee,
            insurance_monthly=loan_data.insurance_monthly,
            rate_type=loan_data.rate_type,
            interest_calculation_method=loan_data.interest_calculation_method,
            grace_period_months=loan_data.grace_period_months,
            late_payment_penalty_rate=loan_data.late_payment_penalty_rate
        )
        
        created_loan = self.loan_repo.create(loan)
        
        if created_loan.start_date:
            schedule_data = self.calc_service.generate_amortization_schedule(
                principal=Decimal(str(created_loan.principal)),
                annual_rate=Decimal(str(created_loan.annual_rate)),
                months=created_loan.months,
                start_date=created_loan.start_date,
                payment_day=created_loan.payment_day,
                payment_frequency=created_loan.payment_frequency,
                insurance_monthly=Decimal(str(created_loan.insurance_monthly)),
                grace_period_months=created_loan.grace_period_months,
                interest_calculation_method=created_loan.interest_calculation_method
            )
            
            schedules = [
                AmortizationSchedule(
                    loan_id=created_loan.id,
                    payment_number=item["payment_number"],
                    due_date=item["due_date"],
                    scheduled_payment=item["scheduled_payment"],
                    scheduled_principal=item["scheduled_principal"],
                    scheduled_interest=item["scheduled_interest"],
                    insurance_amount=item["insurance_amount"],
                    remaining_balance=item["remaining_balance"],
                    is_grace_period=item["is_grace_period"],
                    status="pending"
                )
                for item in schedule_data
            ]
            
            self.amortization_repo.create_batch(schedules)
        
        return self._to_response(created_loan)
    
    def get_loan_by_id(self, loan_id: int, user_id: Optional[int] = None) -> Optional[LoanResponse]:
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            return None
        if user_id is not None and loan.user_id != user_id:
            return None
        return self._to_response(loan)
    
    def get_all_loans(self, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> LoanListResponse:
        if user_id:
            loans = self.loan_repo.get_by_user(user_id)
            total = self.loan_repo.count_by_user(user_id)
        else:
            loans = self.loan_repo.get_all(skip=skip, limit=limit)
            total = self.loan_repo.count_total()
        if user_id:
            loans = loans[skip:skip + limit]
        return LoanListResponse(items=[self._to_response(loan) for loan in loans], total=total, skip=skip, limit=limit)
    
    def update_loan(self, loan_id: int, loan_data: LoanUpdate, user_id: Optional[int] = None) -> Optional[LoanResponse]:
        existing_loan = self.loan_repo.get_by_id(loan_id)
        if not existing_loan:
            return None
        if user_id is not None and existing_loan.user_id != user_id:
            return None
        update_data = loan_data.model_dump(exclude_unset=True)
        updated_loan = self.loan_repo.update(loan_id, update_data)
        if not updated_loan:
            return None
        return self._to_response(updated_loan)
    
    def delete_loan(self, loan_id: int, user_id: Optional[int] = None, hard: bool = False) -> bool:
        loan = self.loan_repo.get_by_id(loan_id, include_deleted=True)
        if not loan:
            return False
        if user_id is not None and loan.user_id != user_id:
            return False
        if hard:
            return self.loan_repo.delete(loan_id)
        else:
            return self.loan_repo.soft_delete(loan_id)
    
    def restore_loan(self, loan_id: int, user_id: Optional[int] = None) -> bool:
        loan = self.loan_repo.get_by_id(loan_id, include_deleted=True)
        if not loan:
            return False
        if user_id is not None and loan.user_id != user_id:
            return False
        return self.loan_repo.restore(loan_id)
    
    def get_user_loans(self, user_id: int, include_deleted: bool = False) -> List[LoanSummary]:
        loans = self.loan_repo.get_by_user(user_id, include_deleted)
        return [self._to_summary(loan) for loan in loans]
    
    def get_active_user_loans(self, user_id: int) -> List[LoanSummary]:
        loans = self.loan_repo.get_active_by_user(user_id)
        return [self._to_summary(loan) for loan in loans]
    
    def _to_response(self, loan: Loan) -> LoanResponse:
        return LoanResponse(
            id=loan.id,
            user_id=loan.user_id,
            name=loan.name,
            type=loan.type,
            status=loan.status,
            total_amount=loan.total_amount,
            down_payment=loan.down_payment,
            principal=loan.principal,
            annual_rate=loan.annual_rate,
            months=loan.months,
            start_date=loan.start_date,
            payment_day=loan.payment_day,
            payment_frequency=loan.payment_frequency,
            origination_fee=loan.origination_fee,
            insurance_monthly=loan.insurance_monthly,
            rate_type=loan.rate_type,
            interest_calculation_method=loan.interest_calculation_method,
            grace_period_months=loan.grace_period_months,
            late_payment_penalty_rate=loan.late_payment_penalty_rate,
            is_deleted=loan.is_deleted,
            deleted_at=loan.deleted_at,
            created_at=loan.created_at,
            updated_at=loan.updated_at,
            monthly_payment=Decimal(str(loan.monthly_payment))
        )
    
    def _to_summary(self, loan: Loan) -> LoanSummary:
        return LoanSummary(
            id=loan.id,
            name=loan.name,
            type=loan.type,
            status=loan.status,
            principal=loan.principal,
            annual_rate=loan.annual_rate,
            months=loan.months,
            start_date=loan.start_date,
            rate_type=loan.rate_type,
            monthly_payment=Decimal(str(loan.monthly_payment)),
            created_at=loan.created_at,
            is_deleted=loan.is_deleted
        )