from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.schemas.loan import LoanCreate, LoanUpdate, LoanResponse, LoanListResponse, LoanSummary
from app.services.loan_service import LoanService
from app.dependencies import get_db, get_loan_service, get_current_user

router = APIRouter(prefix="/api/loans", tags=["loans"])

@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(loan_data: LoanCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> LoanResponse:
    service = get_loan_service(db)
    try:
        return service.create_loan(loan_data, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al crear préstamo: {str(e)}")

@router.get("/", response_model=LoanListResponse)
async def get_loans(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), 
                    current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> LoanListResponse:
    service = get_loan_service(db)
    return service.get_all_loans(skip=skip, limit=limit, user_id=current_user.id)

@router.get("/active", response_model=list[LoanSummary])
async def get_active_loans(current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> list[LoanSummary]:
    service = get_loan_service(db)
    return service.get_active_user_loans(user_id=current_user.id)

@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> LoanResponse:
    service = get_loan_service(db)
    loan = service.get_loan_by_id(loan_id, user_id=current_user.id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Préstamo {loan_id} no encontrado")
    return loan

@router.patch("/{loan_id}", response_model=LoanResponse)
async def update_loan(loan_id: int, loan_data: LoanUpdate, current_user = Depends(get_current_user), 
                      db: Session = Depends(get_db)) -> LoanResponse:
    service = get_loan_service(db)
    updated_loan = service.update_loan(loan_id, loan_data, user_id=current_user.id)
    if not updated_loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Préstamo {loan_id} no encontrado")
    return updated_loan

@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(loan_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    service = get_loan_service(db)
    success = service.delete_loan(loan_id, user_id=current_user.id, hard=False)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Préstamo {loan_id} no encontrado")
    return None

@router.delete("/{loan_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_loan(loan_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    service = get_loan_service(db)
    success = service.delete_loan(loan_id, user_id=current_user.id, hard=True)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Préstamo {loan_id} no encontrado")
    return None

@router.post("/{loan_id}/restore", response_model=LoanResponse)
async def restore_loan(loan_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> LoanResponse:
    service = get_loan_service(db)
    success = service.restore_loan(loan_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Préstamo {loan_id} no encontrado o no está eliminado")
    loan = service.get_loan_by_id(loan_id, user_id=current_user.id)
    return loan