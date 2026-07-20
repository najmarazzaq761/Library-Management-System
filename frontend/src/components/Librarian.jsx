import React, { useState, useEffect } from 'react';
import { authService, bookService, notificationService } from '../services';

export default function Librarian({ token }) {
  const [activeTab, setActiveTab] = useState('add-book'); // 'add-book', 'members', 'overdue'
  
  // Add Book state
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [isbn, setIsbn] = useState('');
  const [copies, setCopies] = useState(1);
  const [addLoading, setAddLoading] = useState(false);
  const [addMessage, setAddMessage] = useState({ text: '', type: '' });

  // Members state
  const [members, setMembers] = useState([]);
  const [membersLoading, setMembersLoading] = useState(false);
  const [membersError, setMembersError] = useState('');

  // Overdue notification state
  const [notifyLoading, setNotifyLoading] = useState(false);
  const [notifyMessage, setNotifyMessage] = useState({ text: '', type: '' });

  // Fetch registered members
  const fetchMembers = async () => {
    setMembersLoading(true);
    setMembersError('');
    try {
      const data = await authService.listMembers();
      setMembers(data);
    } catch (err) {
      setMembersError(err.message);
    } finally {
      setMembersLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'members') {
      fetchMembers();
    }
  }, [activeTab]);

  const handleAddBook = async (e) => {
    e.preventDefault();
    setAddLoading(true);
    setAddMessage({ text: '', type: '' });

    try {
      await bookService.add(title, author, isbn, parseInt(copies, 10));
      
      setAddMessage({ text: `Successfully added "${title}"!`, type: 'success' });
      setTitle('');
      setAuthor('');
      setIsbn('');
      setCopies(1);
    } catch (err) {
      setAddMessage({ text: err.message, type: 'error' });
    } finally {
      setAddLoading(false);
    }
  };

  const handleTriggerNotify = async () => {
    setNotifyLoading(true);
    setNotifyMessage({ text: '', type: '' });

    try {
      const data = await notificationService.triggerOverdueJob();
      setNotifyMessage({
        text: `Success! Checked active loans. Status: ${data.status}. Count: ${data.active_loans_count || 0} loan warning jobs scheduled.`,
        type: 'success'
      });
    } catch (err) {
      setNotifyMessage({ text: err.message, type: 'error' });
    } finally {
      setNotifyLoading(false);
    }
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar Navigation */}
      <div className="sidebar">
        <h3 style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'rgba(255,255,255,0.3)', marginBottom: '0.75rem', paddingLeft: '1rem', letterSpacing: '1px' }}>
          Librarian Console
        </h3>
        <button
          className={`sidebar-tab ${activeTab === 'add-book' ? 'active' : ''}`}
          onClick={() => setActiveTab('add-book')}
        >
          ➕ Add New Book
        </button>
        <button
          className={`sidebar-tab ${activeTab === 'members' ? 'active' : ''}`}
          onClick={() => setActiveTab('members')}
        >
          👥 View Members
        </button>
        <button
          className={`sidebar-tab ${activeTab === 'overdue' ? 'active' : ''}`}
          onClick={() => setActiveTab('overdue')}
        >
          📧 Overdue Notifications
        </button>
      </div>

      {/* Main Panel Content */}
      <div style={{ flex: 1 }}>
        {activeTab === 'add-book' && (
          <div style={{ maxWidth: '600px', background: 'var(--card-dark)', border: '1px solid var(--border-color)', padding: '2rem', borderRadius: '12px' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Add Book to Catalog</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>Register a new physical book volume in the library database</p>
            
            {addMessage.text && (
              <div className={`alert ${addMessage.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                {addMessage.text}
              </div>
            )}

            <form onSubmit={handleAddBook}>
              <div className="form-group">
                <label htmlFor="title-field">Book Title</label>
                <input
                  id="title-field"
                  type="text"
                  className="input-field"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. The Great Gatsby"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="author-field">Author Name</label>
                <input
                  id="author-field"
                  type="text"
                  className="input-field"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  placeholder="e.g. F. Scott Fitzgerald"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="isbn-field">ISBN Code</label>
                <input
                  id="isbn-field"
                  type="text"
                  className="input-field"
                  value={isbn}
                  onChange={(e) => setIsbn(e.target.value)}
                  placeholder="e.g. 9780743273565"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="copies-field">Number of Copies</label>
                <input
                  id="copies-field"
                  type="number"
                  className="input-field"
                  value={copies}
                  onChange={(e) => setCopies(e.target.value)}
                  min="1"
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={addLoading}>
                {addLoading ? <div className="spinner" style={{ margin: '0 auto' }}></div> : 'Save Book'}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'members' && (
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Registered Members</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>Overview of all registered librarians and standard users</p>

            {membersError && (
              <div className="alert alert-error">{membersError}</div>
            )}

            {membersLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
                <div className="spinner"></div>
              </div>
            ) : members.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>No registered members found.</p>
            ) : (
              <div style={{ overflowX: 'auto', background: 'var(--card-dark)', border: '1px solid var(--border-color)', borderRadius: '12px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.95rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', background: 'rgba(255,255,255,0.02)' }}>
                      <th style={{ padding: '1rem' }}>ID</th>
                      <th style={{ padding: '1rem' }}>Name</th>
                      <th style={{ padding: '1rem' }}>Email</th>
                      <th style={{ padding: '1rem' }}>Role</th>
                      <th style={{ padding: '1rem' }}>Registered At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {members.map((member) => (
                      <tr key={member.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                        <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>{member.id}</td>
                        <td style={{ padding: '1rem', fontWeight: 600 }}>{member.name}</td>
                        <td style={{ padding: '1rem' }}>{member.email}</td>
                        <td style={{ padding: '1rem' }}>
                          <span className={`role-tag ${member.role}`}>
                            {member.role}
                          </span>
                        </td>
                        <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                          {new Date(member.registered_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'overdue' && (
          <div style={{ maxWidth: '600px', background: 'var(--card-dark)', border: '1px solid var(--border-color)', padding: '2rem', borderRadius: '12px' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>Send Overdue Warnings</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
              Triggers a background task checking for active, non-returned loans and prints simulated notification alerts to the console.
            </p>

            {notifyMessage.text && (
              <div className={`alert ${notifyMessage.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                {notifyMessage.text}
              </div>
            )}

            <div style={{ border: '1px dashed var(--border-color)', padding: '1.5rem', borderRadius: '8px', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.01)' }}>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>Asynchronous Background Job</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                FastAPI triggers this task asynchronously. The endpoint will respond instantly, and the email simulation outputs (latency, log summaries) will print to the container terminal server console one-by-one.
              </p>
            </div>

            <button onClick={handleTriggerNotify} className="btn btn-primary" style={{ width: '100%' }} disabled={notifyLoading}>
              {notifyLoading ? <div className="spinner" style={{ margin: '0 auto' }}></div> : '🚀 Dispatch Overdue Notices'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
