from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, Query, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db, init_db, seed_data
from app import models, schemas
from app.auth import verify_password, create_access_token, require_role, hash_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run migrations and seed data on startup
    try:
        init_db()
        seed_data()
    except Exception as e:
        print(f"Error during database initialization/seeding: {e}")
    yield

app = FastAPI(title="Library Management API", lifespan=lifespan)

# --- PUBLIC AUTH ENDPOINTS ---

@app.post("/signup", response_model=schemas.MemberSchema, status_code=201)
def signup(member_in: schemas.MemberCreate, db: Session = Depends(get_db)):
    """Register a new member (Public)."""
    existing = db.query(models.Member).filter(models.Member.email == member_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Member with email {member_in.email} already exists."
        )
    db_member = models.Member(
        name=member_in.name,
        email=member_in.email,
        hashed_password=hash_password(member_in.password),
        role=member_in.role
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login to obtain a JWT access token (Public)."""
    member = db.query(models.Member).filter(models.Member.email == form_data.username).first()
    if not member or not verify_password(form_data.password, member.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": member.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- PUBLIC BOOK ENDPOINTS ---

@app.get("/books", response_model=list[schemas.BookSchema])
def list_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a list of books with pagination (Public)."""
    return db.query(models.Book).offset(skip).limit(limit).all()

@app.get("/books/search", response_model=list[schemas.BookSchema])
def search_books(
    title: str | None = Query(None, description="Search by book title (case-insensitive)"),
    author: str | None = Query(None, description="Search by book author (case-insensitive)"),
    db: Session = Depends(get_db)
):
    """Search books by title and/or author (Public)."""
    query = db.query(models.Book)
    if title:
        query = query.filter(models.Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(models.Book.author.ilike(f"%{author}%"))
    return query.all()

# --- PROTECTED LIBRARIAN ENDPOINTS ---

@app.post("/books", response_model=schemas.BookSchema, status_code=201)
def add_book(
    book_in: schemas.BookCreate, 
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["librarian"]))
):
    """Add a new book to the library (Librarian only)."""
    existing_book = db.query(models.Book).filter(models.Book.isbn == book_in.isbn).first()
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book with ISBN '{book_in.isbn}' already exists."
        )
    db_book = models.Book(
        title=book_in.title,
        author=book_in.author,
        isbn=book_in.isbn,
        available_copies=book_in.available_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", status_code=204)
def remove_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["librarian"]))
):
    """Remove a book from the library by its ID (Librarian only)."""
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    
    # Check if book is currently on loan
    active_loan = db.query(models.Loan).filter(
        models.Loan.book_id == book_id,
        models.Loan.is_returned.is_(False)
    ).first()
    if active_loan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot remove '{db_book.title}' - it is currently on loan!"
        )
    
    # Clean up loan history for this book to prevent foreign key errors
    db.query(models.Loan).filter(models.Loan.book_id == book_id).delete()
    
    db.delete(db_book)
    db.commit()
    return None

@app.get("/members", response_model=list[schemas.MemberSchema])
def list_members(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["librarian"]))
):
    """Retrieve a list of members with pagination (Librarian only)."""
    return db.query(models.Member).offset(skip).limit(limit).all()

# --- PROTECTED MEMBER ENDPOINTS ---

@app.post("/books/loan", response_model=schemas.LoanSchema, status_code=201)
def loan_book(
    loan_in: schemas.LoanCreate,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["member", "librarian"]))
):
    """Loan a book to a member (Member or Librarian)."""
    # If member_id is not specified, default to the logged-in member
    target_member_id = loan_in.member_id if loan_in.member_id is not None else current_user.id
    
    # Regular members can only loan books for themselves
    if current_user.role != "librarian" and target_member_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to loan books for other members."
        )
        
    book = db.query(models.Book).filter(models.Book.id == loan_in.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Book with ID {loan_in.book_id} not found."
        )
        
    member = db.query(models.Member).filter(models.Member.id == target_member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Member with ID {target_member_id} not found."
        )
        
    if book.available_copies < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"'{book.title}' has no available copies."
        )
        
    loan = models.Loan(book_id=book.id, member_id=member.id)
    book.available_copies -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

@app.post("/loans/{loan_id}/return", response_model=schemas.LoanSchema)
def return_book(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["member", "librarian"]))
):
    """Return a loaned book (Member or Librarian)."""
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Loan with ID {loan_id} not found."
        )
        
    if loan.is_returned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Loan ID {loan_id} is already returned."
        )
        
    # Regular members can only return their own loaned books
    if current_user.role != "librarian" and loan.member_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to return books for other members."
        )
        
    loan.is_returned = True
    loan.returned_at = datetime.utcnow()
    
    book = db.query(models.Book).filter(models.Book.id == loan.book_id).first()
    if book:
        book.available_copies += 1
        
    db.commit()
    db.refresh(loan)
    return loan

@app.post("/loans/overdue/notify", status_code=202)
def notify_overdue_loans(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.Member = Depends(require_role(["librarian"]))
):
    """Trigger background overdue book notifications for all active loans (Librarian only)."""
    from app.notifications import send_overdue_email
    
    active_loans = db.query(models.Loan).filter(models.Loan.is_returned.is_(False)).all()
    if not active_loans:
        return {"message": "No active loans found to notify."}
        
    for loan in active_loans:
        book = db.query(models.Book).filter(models.Book.id == loan.book_id).first()
        member = db.query(models.Member).filter(models.Member.id == loan.member_id).first()
        
        if member and book:
            # Format date for cleaner display
            borrowed_date_str = loan.borrowed_at.strftime("%Y-%m-%d %H:%M:%S")
            background_tasks.add_task(
                send_overdue_email,
                member_email=member.email,
                member_name=member.name,
                book_title=book.title,
                borrowed_at=borrowed_date_str,
                days_overdue=5  # Static default requested by user
            )
            
    return {
        "status": "Notification jobs scheduled",
        "active_loans_count": len(active_loans),
        "message": "Emails are being sent asynchronously in the background."
    }

