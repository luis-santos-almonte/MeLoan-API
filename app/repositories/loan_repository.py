from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.loan import Loan

class LoanRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[Loan]:
        query = self.db.query(Loan).filter(Loan.id == id)
        if not include_deleted:
            query = query.filter(Loan.is_deleted == False)
        return query.first()
    
    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[Loan]:
        query = self.db.query(Loan)
        if not include_deleted:
            query = query.filter(Loan.is_deleted == False)
        return query.offset(skip).limit(limit).all()
    
    def create(self, loan: Loan) -> Loan:
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan
    
    def update(self, id: int, loan_data: dict) -> Optional[Loan]:
        loan = self.get_by_id(id)
        if not loan:
            return None
        for key, value in loan_data.items():
            if value is not None and hasattr(loan, key):
                setattr(loan, key, value)
        loan.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(loan)
        return loan
    
    def delete(self, id: int) -> bool:
        loan = self.db.query(Loan).filter(Loan.id == id).first()
        if not loan:
            return False
        self.db.delete(loan)
        self.db.commit()
        return True
    
    def soft_delete(self, id: int) -> bool:
        loan = self.get_by_id(id)
        if not loan:
            return False
        loan.is_deleted = True
        loan.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def restore(self, id: int) -> bool:
        loan = self.get_by_id(id, include_deleted=True)
        if not loan or not loan.is_deleted:
            return False
        loan.is_deleted = False
        loan.deleted_at = None
        self.db.commit()
        return True
    
    def get_active(self, skip: int = 0, limit: int = 100) -> List[Loan]:
        return self.db.query(Loan).filter(Loan.is_deleted == False).offset(skip).limit(limit).all()
    
    def get_deleted(self, skip: int = 0, limit: int = 100) -> List[Loan]:
        return self.db.query(Loan).filter(Loan.is_deleted == True).offset(skip).limit(limit).all()
    
    def get_by_user(self, user_id: int, include_deleted: bool = False) -> List[Loan]:
        query = self.db.query(Loan).filter(Loan.user_id == user_id)
        if not include_deleted:
            query = query.filter(Loan.is_deleted == False)
        return query.all()
    
    def get_active_by_user(self, user_id: int) -> List[Loan]:
        return self.db.query(Loan).filter(
            and_(Loan.user_id == user_id, Loan.is_deleted == False, Loan.status.in_(["simulation", "active"]))
        ).all()
    
    def count_total(self, include_deleted: bool = False) -> int:
        query = self.db.query(Loan)
        if not include_deleted:
            query = query.filter(Loan.is_deleted == False)
        return query.count()
    
    def count_by_user(self, user_id: int, include_deleted: bool = False) -> int:
        query = self.db.query(Loan).filter(Loan.user_id == user_id)
        if not include_deleted:
            query = query.filter(Loan.is_deleted == False)
        return query.count()