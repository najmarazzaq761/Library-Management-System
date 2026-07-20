import React, { useState, useEffect } from 'react';
import Auth from './components/Auth';
import Catalog from './components/Catalog';
import Librarian from './components/Librarian';
import Member from './components/Member';
import NotificationsModal from './components/NotificationsModal';
import { notificationService } from './services';

export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('catalog'); // 'catalog', 'dashboard', 'librarian', 'auth'
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Notifications State
  const [notifications, setNotifications] = useState([]);
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [hasPromptedModal, setHasPromptedModal] = useState(false);

  // Check for stored credentials on load
  useEffect(() => {
    const token = localStorage.getItem('token');
    const email = localStorage.getItem('userEmail');
    const role = localStorage.getItem('userRole');

    if (token && email && role) {
      setUser({ token, email, role });
    }
  }, []);

  const fetchNotifications = async () => {
    try {
      const data = await notificationService.list();
      setNotifications(data);
      
      // Show popup modal alert if overdue warnings exist and user has not been alerted in this session
      if (data.length > 0 && !hasPromptedModal) {
        setShowModal(true);
        setHasPromptedModal(true);
      }
    } catch (err) {
      console.error("Error fetching notifications:", err);
    }
  };

  // Sync notifications periodically or upon action refresh
  useEffect(() => {
    if (user) {
      fetchNotifications();
    } else {
      setNotifications([]);
      setShowModal(false);
      setHasPromptedModal(false);
    }
  }, [user, refreshTrigger]);

  const dismissNotification = async (notifId) => {
    try {
      await notificationService.read(notifId);
      setNotifications(prev => prev.filter(n => n.id !== notifId));
    } catch (err) {
      console.error("Error clearing notification:", err);
    }
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    if (userData.role === 'librarian') {
      setActiveTab('catalog');
    } else {
      setActiveTab('dashboard');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userRole');
    setUser(null);
    setActiveTab('catalog');
  };

  const triggerRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="app-container">
      {/* Pop-up modal warnings on login */}
      {showModal && (
        <NotificationsModal
          notifications={notifications}
          onClose={() => setShowModal(false)}
        />
      )}

      {/* Dynamic Header */}
      <header>
        <div className="nav-content">
          <div className="brand">
            📚 <span>LMS Portal</span>
          </div>

          <div className="nav-links">
            <button
              className={`nav-button ${activeTab === 'catalog' ? 'active' : ''}`}
              onClick={() => setActiveTab('catalog')}
            >
              📖 Book Catalog
            </button>

            {user && (
              <button
                className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('dashboard')}
              >
                👤 My Dashboard
              </button>
            )}

            {user && user.role === 'librarian' && (
              <button
                className={`nav-button ${activeTab === 'librarian' ? 'active' : ''}`}
                onClick={() => setActiveTab('librarian')}
              >
                ⚙️ Librarian Panel
              </button>
            )}

            {user ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                {/* Notification Icon Bell with Dropdown */}
                <div className="notif-bell-container">
                  <button
                    className="nav-button"
                    style={{ fontSize: '1.2rem', padding: '0.4rem 0.6rem', position: 'relative' }}
                    onClick={() => setShowNotifDropdown(!showNotifDropdown)}
                  >
                    🔔
                    {notifications.length > 0 && (
                      <span className="notif-badge">{notifications.length}</span>
                    )}
                  </button>

                  {showNotifDropdown && (
                    <div className="notif-dropdown">
                      <div className="notif-dropdown-header">
                        <span>New Alerts</span>
                        {notifications.length > 0 && (
                          <span style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.05)', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                            {notifications.length} Active
                          </span>
                        )}
                      </div>
                      <div className="notif-dropdown-content">
                        {notifications.length === 0 ? (
                          <div style={{ padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem', textAlign: 'center' }}>
                            No new notifications.
                          </div>
                        ) : (
                          notifications.map((notif) => (
                            <div className="notif-dropdown-item" key={notif.id}>
                              <span>{notif.message}</span>
                              <button
                                className="notif-dismiss-btn"
                                onClick={() => dismissNotification(notif.id)}
                                title="Mark read"
                              >
                                &times;
                              </button>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="user-badge">
                  <span>{user.email}</span>
                  <span className={`role-tag ${user.role}`}>
                    {user.role}
                  </span>
                </div>
                <button onClick={handleLogout} className="nav-button btn-secondary">
                  Log Out
                </button>
              </div>
            ) : (
              <button
                className={`nav-button primary ${activeTab === 'auth' ? 'active' : ''}`}
                onClick={() => setActiveTab('auth')}
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main>
        {activeTab === 'catalog' && (
          <Catalog
            userRole={user ? user.role : null}
            token={user ? user.token : null}
            onActionSuccess={triggerRefresh}
          />
        )}

        {activeTab === 'dashboard' && user && (
          <Member
            token={user.token}
            refreshTrigger={refreshTrigger}
          />
        )}

        {activeTab === 'librarian' && user && user.role === 'librarian' && (
          <Librarian
            token={user.token}
          />
        )}

        {activeTab === 'auth' && !user && (
          <Auth
            onLoginSuccess={handleLoginSuccess}
          />
        )}
      </main>
    </div>
  );
}
