import React, { useState } from 'react';
import { authService } from '../services';

export default function Auth({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('member');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        // Call authService login method
        const data = await authService.login(email, password);

        // Store JWT token
        localStorage.setItem('token', data.access_token);
        
        // Fetch current member details
        localStorage.setItem('userEmail', email);
        // Determine role based on email or search members list.
        const userRole = email === 'librarian@library.com' ? 'librarian' : 'member';
        localStorage.setItem('userRole', userRole);

        onLoginSuccess({
          email,
          role: userRole,
          token: data.access_token
        });
      } else {
        // Call authService signup method
        await authService.signup(name, email, password, role);

        // After signup, switch to login view
        setIsLogin(true);
        setName('');
        setError('Signup successful! Please log in.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Safe JSON utility
  function jsonStringify(obj) {
    return JSON.stringify(obj);
  }

  return (
    <div className="auth-container">
      <div className="auth-header">
        <h2>{isLogin ? 'Welcome Back' : 'Join the Library'}</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
          {isLogin ? 'Log in to manage your book loans' : 'Create an account to start borrowing'}
        </p>
      </div>

      {error && (
        <div className={`alert ${error.includes('successful') ? 'alert-success' : 'alert-error'}`}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <div className="form-group">
            <label htmlFor="name-input">Full Name</label>
            <input
              id="name-input"
              type="text"
              className="input-field"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. John Doe"
              required
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="email-input">Email Address</label>
          <input
            id="email-input"
            type="email"
            className="input-field"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="e.g. john@example.com"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password-input">Password</label>
          <input
            id="password-input"
            type="password"
            className="input-field"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </div>

        {!isLogin && (
          <div className="form-group">
            <label htmlFor="role-select">Account Type</label>
            <select
              id="role-select"
              className="input-field"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="member">Library Member</option>
              <option value="librarian">Librarian</option>
            </select>
          </div>
        )}

        <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
          {loading ? <div className="spinner" style={{ margin: '0 auto' }}></div> : (isLogin ? 'Log In' : 'Sign Up')}
        </button>
      </form>

      <div className="auth-toggle">
        {isLogin ? (
          <>
            Don't have an account? <span onClick={() => { setIsLogin(false); setError(''); }}>Sign up</span>
          </>
        ) : (
          <>
            Already have an account? <span onClick={() => { setIsLogin(true); setError(''); }}>Log in</span>
          </>
        )}
      </div>
    </div>
  );
}
