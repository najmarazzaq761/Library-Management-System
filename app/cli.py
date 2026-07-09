"""Interactive terminal menu for Library Management System."""

from datetime import datetime
from app.database import SessionLocal
from app.models import Book, Member, Loan


def add_book(title, author, isbn):
    """Add a new book to the library."""
    db = SessionLocal()
    try:
        existing = db.query(Book).filter(Book.isbn == isbn).first()
        if existing:
            print(f"Book with ISBN {isbn} already exists!")
            return

        book = Book(title=title, author=author, isbn=isbn)
        db.add(book)
        db.commit()
        print(f"Book added successfully: '{title}' by {author}")
    finally:
        db.close()


def list_books():
    """List all books in the library."""
    db = SessionLocal()
    try:
        books = db.query(Book).all()
        if not books:
            print("No books found in the library.")
            return

        print(f"\nTotal Books: {len(books)}\n")
        print("-" * 80)
        for book in books:
            status = (
                f"Available: {book.available_copies}"
                if book.available_copies > 0
                else "Out of stock"
            )
            print(
                f"ID: {book.id} | {book.title} by {book.author} | "
                f"ISBN: {book.isbn} | {status}"
            )
        print("-" * 80)
    finally:
        db.close()


def search_books(query):
    """Search for books by title or author."""
    db = SessionLocal()
    try:
        books = db.query(Book).filter(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%"))
        ).all()

        if not books:
            print(f"No books found matching '{query}'")
            return

        print(f"\nFound {len(books)} book(s) matching '{query}':\n")
        print("-" * 80)
        for book in books:
            print(
                f"ID: {book.id} | {book.title} by {book.author} | "
                f"ISBN: {book.isbn}"
            )
        print("-" * 80)
    finally:
        db.close()


def remove_book(book_id):
    """Remove a book from the library."""
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            print(f"Book with ID {book_id} not found!")
            return

        # Check if book is on loan
        active_loan = db.query(Loan).filter(
            Loan.book_id == book_id,
            Loan.is_returned.is_(False)
        ).first()
        if active_loan:
            print(f"Cannot remove '{book.title}' - it's currently on loan!")
            return

        # Clean up loan history for this book to prevent foreign key errors
        db.query(Loan).filter(Loan.book_id == book_id).delete()

        db.delete(book)
        db.commit()
        print(f"Book '{book.title}' removed successfully!")
    finally:
        db.close()


def register_member(name, email):
    """Register a new library member."""
    db = SessionLocal()
    try:
        existing = db.query(Member).filter(Member.email == email).first()
        if existing:
            print(f"Member with email {email} already exists!")
            return

        member = Member(name=name, email=email)
        db.add(member)
        db.commit()
        print(f"Member '{name}' registered successfully!")
    finally:
        db.close()


def list_members():
    """List all registered members."""
    db = SessionLocal()
    try:
        members = db.query(Member).all()
        if not members:
            print("No members registered.")
            return

        print(f"\nTotal Members: {len(members)}\n")
        print("-" * 80)
        for member in members:
            print(f"ID: {member.id} | {member.name} | {member.email}")
        print("-" * 80)
    finally:
        db.close()


def loan_book(book_id, member_id):
    """Loan a book to a member."""
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            print(f"Book with ID {book_id} not found!")
            return

        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            print(f"Member with ID {member_id} not found!")
            return

        if book.available_copies < 1:
            print(f"'{book.title}' has no available copies!")
            return

        # Create loan
        loan = Loan(book_id=book_id, member_id=member_id)
        book.available_copies -= 1
        db.add(loan)
        db.commit()
        print(f"'{book.title}' loaned to {member.name} successfully!")
    finally:
        db.close()


def return_book(loan_id):
    """Return a loaned book."""
    db = SessionLocal()
    try:
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            print(f"Loan with ID {loan_id} not found!")
            return

        if loan.is_returned:
            print(f"Loan ID {loan_id} is already returned!")
            return

        loan.is_returned = True
        loan.returned_at = datetime.utcnow()

        # Increase available copies
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        if book:
            book.available_copies += 1

        db.commit()
        print(f"Book '{book.title}' returned successfully!")
    finally:
        db.close()


def cli():
    """Main interactive menu loop."""
    # Ensure database is set up on run
    from app.database import init_db, seed_data
    try:
        init_db()
        seed_data()
    except Exception as e:
        print(f"Database initialization status: {e}")

    while True:
        print("\n========================================")
        print("     LIBRARY MANAGEMENT SYSTEM MENU     ")
        print("========================================")
        print("1. List all books")
        print("2. Search for books")
        print("3. Add a book")
        print("4. Remove a book")
        print("5. Register a member")
        print("6. List all members")
        print("7. Loan a book")
        print("8. Return a book")
        print("9. Exit")
        print("========================================")

        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            list_books()
        elif choice == "2":
            query = input("Enter search query (title or author): ").strip()
            if query:
                search_books(query)
            else:
                print("Search query cannot be empty.")
        elif choice == "3":
            title = input("Enter book title: ").strip()
            author = input("Enter book author: ").strip()
            isbn = input("Enter book ISBN: ").strip()
            if title and author and isbn:
                add_book(title, author, isbn)
            else:
                print("All fields (title, author, isbn) are required.")
        elif choice == "4":
            book_id_str = input("Enter Book ID to remove: ").strip()
            try:
                book_id = int(book_id_str)
                remove_book(book_id)
            except ValueError:
                print("Invalid Book ID. Please enter a number.")
        elif choice == "5":
            name = input("Enter member name: ").strip()
            email = input("Enter member email: ").strip()
            if name and email:
                register_member(name, email)
            else:
                print("Both name and email are required.")
        elif choice == "6":
            list_members()
        elif choice == "7":
            book_id_str = input("Enter Book ID: ").strip()
            member_id_str = input("Enter Member ID: ").strip()
            try:
                book_id = int(book_id_str)
                member_id = int(member_id_str)
                loan_book(book_id, member_id)
            except ValueError:
                print("Invalid IDs. Please enter numbers.")
        elif choice == "8":
            loan_id_str = input("Enter Loan ID to return: ").strip()
            try:
                loan_id = int(loan_id_str)
                return_book(loan_id)
            except ValueError:
                print("Invalid Loan ID. Please enter a number.")
        elif choice == "9":
            print("Exiting Library Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")


if __name__ == "__main__":
    cli()