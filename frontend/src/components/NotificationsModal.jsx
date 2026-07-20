import React from 'react';

export default function NotificationsModal({ notifications, onClose }) {
  if (!notifications || notifications.length === 0) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
        <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
          Overdue Book Notifications
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
          Our records show you have pending actions. Please return the following book(s) as soon as possible:
        </p>

        <div style={{
          maxHeight: '180px',
          overflowY: 'auto',
          background: 'rgba(0, 0, 0, 0.2)',
          padding: '1rem',
          borderRadius: '8px',
          textAlign: 'left',
          marginBottom: '1.5rem',
          border: '1px solid var(--border-color)'
        }}>
          {notifications.map((notif) => (
            <div key={notif.id} style={{
              fontSize: '0.85rem',
              lineHeight: '1.4',
              paddingBottom: '0.75rem',
              marginBottom: '0.75rem',
              borderBottom: '1px solid rgba(255,255,255,0.05)',
              color: 'var(--text-primary)'
            }}>
              • {notif.message}
            </div>
          ))}
        </div>

        <button className="btn btn-primary" style={{ width: '100%' }} onClick={onClose}>
          I Understand, Close
        </button>
      </div>
    </div>
  );
}
