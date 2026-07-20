import React, { useState, useEffect } from 'react';
import { bookService, loanService } from '../services';

export default function Catalog({ userRole, token, onActionSuccess }) {
  const [books, setBooks] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(null);

  const fetchBooks = async (query = '') => {
    setLoading(true);
    setError('');
    try {
      let data;
      if (query.trim()) {
        data = await bookService.search(query);
      } else {
        data = await bookService.list();
      }
      setBooks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchBooks(searchQuery);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    fetchBooks('');
  };

  const handleLoan = async (bookId) => {
    setActionLoading(bookId);
    setError('');
    try {
      await loanService.borrow(bookId);
      // Refresh list
      fetchBooks(searchQuery);
      if (onActionSuccess) onActionSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <h2 className="page-title">Library Book Catalog</h2>
          <p className="page-subtitle">Browse and search for available titles in our database</p>
        </div>

        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', width: '100%', maxWidth: '400px' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <input
              type="text"
              className="input-field"
              placeholder="Search by title or author..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={handleClearSearch}
                style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  fontSize: '1.1rem'
                }}
              >
                &times;
              </button>
            )}
          </div>
          <button type="submit" className="btn btn-primary">Search</button>
        </form>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span> {error}
        </div>
      )}

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
          <div className="spinner" style={{ width: '40px', height: '40px' }}></div>
        </div>
      ) : books.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
          <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>No books found</p>
          <p style={{ fontSize: '0.95rem' }}>Try refining your search query or clear it to view the whole catalog.</p>
        </div>
      ) : (
        <div className="grid">
          {books.map((book) => {
            const isAvailable = book.available_copies > 0;
            return (
              <div className="card" key={book.id}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-primary)' }}>
                  {book.title}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '0.75rem' }}>
                  by {book.author}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                  <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.4)', fontFamily: 'monospace' }}>
                    ISBN: {book.isbn}
                  </span>
                  <span className={`status-badge ${isAvailable ? 'available' : 'unavailable'}`}>
                    {isAvailable ? `${book.available_copies} Available` : 'Out of stock'}
                  </span>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem', marginTop: 'auto' }}>
                  {userRole && (
                    <button
                      className="btn btn-primary"
                      style={{ flex: 1 }}
                      onClick={() => handleLoan(book.id)}
                      disabled={!isAvailable || actionLoading === book.id}
                    >
                      {actionLoading === book.id ? <div className="spinner"></div> : 'Borrow Book'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
