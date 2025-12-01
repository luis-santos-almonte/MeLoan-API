from typing import Optional, List
from decimal import Decimal

from app.models.loan import Loan
from app.schemas.loan import LoanCreate, LoanUpdate, LoanResponse, LoanListResponse, LoanSummary
from app.repositories.loan_repository import LoanRepository

class LoanService:
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repo = loan_repository
    
    def create_loan(self, loan_data: LoanCreate, user_id: int) -> LoanResponse:
        loan = Loan(
            user_id=user_id, name=loan_data.name, type=loan_data.type, status=loan_data.status,
            total_amount=loan_data.total_amount, down_payment=loan_data.down_payment,
            principal=loan_data.principal, annual_rate=loan_data.annual_rate, months=loan_data.months
        )
        created_loan = self.loan_repo.create(loan)
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
            id=loan.id, user_id=loan.user_id, name=loan.name, type=loan.type, status=loan.status,
            total_amount=loan.total_amount, down_payment=loan.down_payment, principal=loan.principal,
            annual_rate=loan.annual_rate, months=loan.months, is_deleted=loan.is_deleted,
            deleted_at=loan.deleted_at, created_at=loan.created_at, updated_at=loan.updated_at,
            monthly_payment=Decimal(str(loan.monthly_payment))
        )
    
    def _to_summary(self, loan: Loan) -> LoanSummary:
        return LoanSummary(
            id=loan.id, name=loan.name, type=loan.type, status=loan.status, principal=loan.principal,
            annual_rate=loan.annual_rate, months=loan.months, monthly_payment=Decimal(str(loan.monthly_payment)),
            created_at=loan.created_at, is_deleted=loan.is_deleted
        )