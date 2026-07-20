import React, { useState, useEffect } from 'react';
import { loanService } from '../services';

export default function Member({ token, refreshTrigger }) {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [returnLoading, setReturnLoading] = useState(null);

  const fetchLoans = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await loanService.list();
      setLoans(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLoans();
  }, [refreshTrigger]);

  const handleReturn = async (loanId) => {
    setReturnLoading(loanId);
    setError('');
    try {
      await loanService.returnBook(loanId);
      
      // Refresh loans
      fetchLoans();
    } catch (err) {
      setError(err.message);
    } finally {
      setReturnLoading(null);
    }
  };

  // Separate active and returned loans
  const activeLoans = loans.filter(l => !l.is_returned);
  const historyLoans = loans.filter(l => l.is_returned);

  return (
    <div>
      <h2 className="page-title">My Dashboard</h2>
      <p className="page-subtitle">Manage your borrowed books, active loans, and borrowing history</p>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span> {error}
        </div>
      )}

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
          <div className="spinner"></div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
          {/* Active Loans */}
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              Active Loans
              <span style={{ fontSize: '0.8rem', background: 'var(--primary)', color: 'var(--text-primary)', padding: '0.1rem 0.5rem', borderRadius: '10px' }}>
                {activeLoans.length}
              </span>
            </h3>

            {activeLoans.length === 0 ? (
              <div style={{ background: 'var(--card-dark)', border: '1px dashed var(--border-color)', padding: '2.5rem', borderRadius: '12px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                <p style={{ fontSize: '1.05rem', marginBottom: '0.25rem' }}>No active loans</p>
                <p style={{ fontSize: '0.85rem' }}>Search the catalog to borrow some books!</p>
              </div>
            ) : (
              <div className="grid">
                {activeLoans.map((loan) => (
                  <div className="card" key={loan.id} style={{ display: 'flex', flexDirection: 'column' }}>
                    <h4 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                      {loan.book.title}
                    </h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                      by {loan.book.author}
                    </p>

                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      <div>
                        Borrowed: <span style={{ color: 'var(--text-primary)' }}>{new Date(loan.borrowed_at).toLocaleDateString()}</span>
                      </div>
                      <div>
                        ISBN: <span style={{ color: 'var(--text-primary)', fontFamily: 'monospace' }}>{loan.book.isbn}</span>
                      </div>
                    </div>

                    <button
                      className="btn btn-secondary"
                      style={{ width: '100%', marginTop: 'auto' }}
                      onClick={() => handleReturn(loan.id)}
                      disabled={returnLoading === loan.id}
                    >
                      {returnLoading === loan.id ? <div className="spinner"></div> : ' Return Book'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Borrowing History */}
          {historyLoans.length > 0 && (
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                 Borrowing History
              </h3>

              <div style={{ overflowX: 'auto', background: 'var(--card-dark)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', background: 'rgba(255,255,255,0.02)', color: 'var(--text-secondary)' }}>
                      <th style={{ padding: '1rem' }}>Book Title</th>
                      <th style={{ padding: '1rem' }}>Author</th>
                      <th style={{ padding: '1rem' }}>Borrowed At</th>
                      <th style={{ padding: '1rem' }}>Returned At</th>
                      <th style={{ padding: '1rem' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyLoans.map((loan) => (
                      <tr key={loan.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                        <td style={{ padding: '1rem', fontWeight: 500 }}>{loan.book.title}</td>
                        <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{loan.book.author}</td>
                        <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                          {new Date(loan.borrowed_at).toLocaleDateString()}
                        </td>
                        <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                          {loan.returned_at ? new Date(loan.returned_at).toLocaleDateString() : '-'}
                        </td>
                        <td style={{ padding: '1rem' }}>
                          <span style={{ fontSize: '0.75rem', padding: '0.1rem 0.4rem', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
                            Returned
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
