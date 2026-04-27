import React, { useState } from 'react';
import { loginWithBiometrics } from '../utils/webauthn_client';

const API_URL = 'http://localhost:8000';

interface AuthProps {
  onLogin: (token: string) => void;
}

const Auth: React.FC<AuthProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Authentication failed');

      if (isLogin) {
        localStorage.setItem('token', data.access_token);
        onLogin(data.access_token);
      } else {
        setIsLogin(true);
        setError('Signup successful! Please log in.');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBiometricLogin = async () => {
    if (!username) {
      setError('Please enter your username first');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const data = await loginWithBiometrics(username);
      onLogin(data.access_token);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card glass">
        <div className="auth-header">
          <div className="auth-logo">🔍</div>
          <h2>{isLogin ? 'Forensic Login' : 'Agent Signup'}</h2>
          <p>{isLogin ? 'Enter your credentials to access the laboratory' : 'Register your agent profile'}</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label htmlFor="username">Agent Identifier</label>
            <input
              id="username"
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Access Code</label>
            <input
              id="password"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Authenticate' : 'Register')}
          </button>
        </form>

        {isLogin && (
          <div className="auth-divider">
            <span>OR</span>
          </div>
        )}

        {isLogin && (
          <button 
            type="button" 
            className="auth-biometric" 
            onClick={handleBiometricLogin}
            disabled={loading}
          >
            <span className="biometric-icon">👆</span>
            Sign in with Biometrics
          </button>
        )}

        <div className="auth-footer">
          <button onClick={() => setIsLogin(!isLogin)} className="text-btn">
            {isLogin ? "New Agent? Create Profile" : "Already Registered? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Auth;
