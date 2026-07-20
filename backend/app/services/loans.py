from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.loan import Loan
from app.models.member import Member
from app.schemas.loan import LoanCreate


def get_loans(db: Session, current_user: Member) -> list[Loan]:
    """Retrieve loans. Members see their own; Librarians see all."""
    if current_user.role == "librarian":
        return db.query(Loan).all()
    return db.query(Loan).filter(Loan.member_id == current_user.id).all()


def create_loan(
    db: Session, loan_in: LoanCreate, current_user: Member
) -> Loan:
    """Borrow a book copy."""
    # Check if target book exists
    book = db.query(Book).filter(Book.id == loan_in.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {loan_in.book_id} not found."
        )

    # Check copy availability
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book '{book.title}' is currently out of stock."
        )

    # Determine borrower ID
    target_member_id = current_user.id
    if current_user.role == "librarian" and loan_in.member_id is not None:
        target_member_id = loan_in.member_id

    # Verify borrower exists
    borrower = db.query(Member).filter(Member.id == target_member_id).first()
    if not borrower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {target_member_id} not found."
        )

    # Decrement catalog count
    book.available_copies -= 1

    db_loan = Loan(
        book_id=book.id,
        member_id=target_member_id,
        is_returned=False
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


def return_book(db: Session, loan_id: int, current_user: Member) -> Loan:
    """Return a borrowed book."""
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan record with ID {loan_id} not found."
        )

    if loan.is_returned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This loan has already been returned."
        )

    # Role checks: members can only return their own books
    if current_user.role != "librarian" and loan.member_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to return loans for other members."
        )

    # Increment catalog count
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if book:
        book.available_copies += 1

    loan.is_returned = True
    loan.returned_at = datetime.utcnow()
    db.commit()
    db.refresh(loan)
    return loan
