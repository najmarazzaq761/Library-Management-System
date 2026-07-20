from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app import schemas, models
from app.services import loans as loans_service

router = APIRouter(tags=["Loans"])


@router.get("/loans", response_model=list[schemas.LoanDetailSchema])
def list_loans(
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(
        require_role(["member", "librarian"])
    )
):
    """Retrieve a list of loans. Members see their own; Librarians see all."""
    return loans_service.get_loans(db, current_user)


@router.post("/books/loan", response_model=schemas.LoanSchema, status_code=201)
def loan_book(
    loan_in: schemas.LoanCreate,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(
        require_role(["member", "librarian"])
    )
):
    """Borrow a book copy."""
    return loans_service.create_loan(db, loan_in, current_user)


@router.post("/loans/{loan_id}/return", response_model=schemas.LoanSchema)
def return_book(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(
        require_role(["member", "librarian"])
    )
):
    """Return a borrowed book."""
    return loans_service.return_book(db, loan_id, current_user)
