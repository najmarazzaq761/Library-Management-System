"""CLI commands for Library Management System."""

import click
from datetime import datetime
from app.database import SessionLocal
from app.models import Book, Member, Loan


@click.group()
def cli():
    """Library Management System CLI."""
    pass


@cli.command()
def init_db():
    """Initialize database and seed with sample data."""
    from app.database import init_db, seed_data
    try:
        init_db()
        click.echo("Database tables created successfully!")
        seed_data()
        click.echo("Sample data seeded successfully!")
    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.option("--title", required=True, help="Book title")
@click.option("--author", required=True, help="Book author")
@click.option("--isbn", required=True, help="Book ISBN")
def add_book(title, author, isbn):
    """Add a new book to the library."""
    db = SessionLocal()
    try:
        # Check if book already exists
        existing = db.query(Book).filter(Book.isbn == isbn).first()
        if existing:
            click.echo(f"Book with ISBN {isbn} already exists!")
            return

        book = Book(title=title, author=author, isbn=isbn)
        db.add(book)
        db.commit()
        click.echo(f"Book added successfully: '{title}' by {author}")
    finally:
        db.close()


@cli.command()
def list_books():
    """List all books in the library."""
    db = SessionLocal()
    try:
        books = db.query(Book).all()
        if not books:
            click.echo("No books found in the library.")
            return

        click.echo(f"\nTotal Books: {len(books)}\n")
        click.echo("-" * 80)
        for book in books:
            status = (
                f"Available: {book.available_copies}"
                if book.available_copies > 0
                else "Out of stock"
            )
            click.echo(
                f"ID: {book.id} | {book.title} by {book.author} | "
                f"ISBN: {book.isbn} | {status}"
            )
        click.echo("-" * 80)
    finally:
        db.close()


@cli.command()
@click.option("--query", required=True, help="Search query (title or author)")
def search(query):
    """Search for books by title or author."""
    db = SessionLocal()
    try:
        books = db.query(Book).filter(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%"))
        ).all()

        if not books:
            click.echo(f"No books found matching '{query}'")
            return

        click.echo(f"\nFound {len(books)} book(s) matching '{query}':\n")
        click.echo("-" * 80)
        for book in books:
            click.echo(
                f"ID: {book.id} | {book.title} by {book.author} | "
                f"ISBN: {book.isbn}"
            )
        click.echo("-" * 80)
    finally:
        db.close()


@cli.command()
@click.option("--book_id", type=int, required=True, help="Book ID to remove")
def remove_book(book_id):
    """Remove a book from the library."""
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            click.echo(f"Book with ID {book_id} not found!")
            return

        # Check if book is on loan
        active_loan = db.query(Loan).filter(
            Loan.book_id == book_id,
            Loan.is_returned.is_(False)
        ).first()
        if active_loan:
            click.echo(
                f"Cannot remove '{book.title}' - it's currently on loan!"
            )
            return

        db.delete(book)
        db.commit()
        click.echo(f"Book '{book.title}' removed successfully!")
    finally:
        db.close()


@cli.command()
@click.option("--name", required=True, help="Member name")
@click.option("--email", required=True, help="Member email")
def register_member(name, email):
    """Register a new library member."""
    db = SessionLocal()
    try:
        existing = db.query(Member).filter(Member.email == email).first()
        if existing:
            click.echo(f"Member with email {email} already exists!")
            return

        member = Member(name=name, email=email)
        db.add(member)
        db.commit()
        click.echo(f"Member '{name}' registered successfully!")
    finally:
        db.close()


@cli.command()
@click.option("--book_id", type=int, required=True, help="Book ID")
@click.option("--member_id", type=int, required=True, help="Member ID")
def loan_book(book_id, member_id):
    """Loan a book to a member."""
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            click.echo(f"Book with ID {book_id} not found!")
            return

        member = db.query(Member).filter(Member.id == member_id).first()
        if not member:
            click.echo(f"Member with ID {member_id} not found!")
            return

        if book.available_copies < 1:
            click.echo(f" '{book.title}' has no available copies!")
            return

        # Create loan
        loan = Loan(book_id=book_id, member_id=member_id)
        book.available_copies -= 1
        db.add(loan)
        db.commit()
        click.echo(f" '{book.title}' loaned to {member.name} successfully!")
    finally:
        db.close()


@cli.command()
@click.option("--loan_id", type=int, required=True, help="Loan ID")
def return_book(loan_id):
    """Return a loaned book."""
    db = SessionLocal()
    try:
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            click.echo(f"Loan with ID {loan_id} not found!")
            return

        if loan.is_returned:
            click.echo(f"Loan ID {loan_id} is already returned!")
            return

        loan.is_returned = True
        loan.returned_at = datetime.utcnow()

        # Increase available copies
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        if book:
            book.available_copies += 1

        db.commit()
        click.echo(f"Book '{book.title}' returned successfully!")
    finally:
        db.close()


@cli.command()
def list_members():
    """List all registered members."""
    db = SessionLocal()
    try:
        members = db.query(Member).all()
        if not members:
            click.echo("No members registered.")
            return

        click.echo(f"\nTotal Members: {len(members)}\n")
        click.echo("-" * 80)
        for member in members:
            click.echo(f"ID: {member.id} | {member.name} | {member.email}")
        click.echo("-" * 80)
    finally:
        db.close()


if __name__ == "__main__":
    cli()