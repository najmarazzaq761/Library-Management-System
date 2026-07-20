"""Tests for book management functionality."""

import pytest


class Book:
    """Mock Book class for testing."""
    def __init__(self, title, author, isbn, available_copies=1):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.available_copies = available_copies


def create_book(title, author, isbn):
    """Create a book with validation."""
    # Simple ISBN validation (length 10 or 13, digits only)
    if not isbn.replace("-", "").isdigit():
        raise ValueError("Invalid ISBN: must contain only digits")
    return Book(title, author, isbn)


def test_create_book():
    """Test that creating a book works correctly."""
    book = create_book("1984", "George Orwell", "978-0451524935")

    assert book.title == "1984"
    assert book.author == "George Orwell"
    assert book.isbn == "978-0451524935"
    assert book.available_copies == 1


def test_create_book_with_invalid_isbn():
    """Test that invalid ISBN raises an error."""
    with pytest.raises(ValueError):
        create_book("1984", "George Orwell", "invalid-isbn")


def test_create_book_with_isbn_10():
    """Test creating a book with ISBN-10 format."""
    book = create_book("Dune", "Frank Herbert", "0441172717")
    assert book.isbn == "0441172717"


def test_create_book_with_isbn_containing_hyphens():
    """Test creating a book with hyphenated ISBN."""
    book = create_book("1984", "George Orwell", "978-0-451-52493-5")
    assert book.title == "1984"
