import { useState } from 'react';
import { loginWithBiometrics } from '../utils/webauthn_client';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Auth = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [justSignedUp, setJustSignedUp] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [linkingBiometrics, setLinkingBiometrics] = useState(false);
  const [tempToken, setTempToken] = useState(null);

  const [awaiting2FA, setAwaiting2FA] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!password) {
      setError('Please enter the password');
      return;
    }

    setError('');
    setSuccess('');
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
        // Password is correct, now strictly enforce Biometrics (2FA)
        setAwaiting2FA(true);
        try {
          const bioData = await loginWithBiometrics(username);
          localStorage.setItem('token', bioData.access_token);
          onLogin(bioData.access_token);
        } catch (bioErr) {
          setError('Biometric verification failed. Both password and biometrics are required.');
          setAwaiting2FA(false);
        }
      } else {
        // After signup, auto-login to get token, then prompt for biometrics
        setSuccess('Account created! Please link your biometrics...');
        const loginResp = await fetch(`${API_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });
        const loginData = await loginResp.json();
        if (loginResp.ok) {
          setTempToken(loginData.access_token);
          setJustSignedUp(true);
          setSuccess('');
        } else {
          setIsLogin(true);
          setSuccess('Signup successful! Please log in.');
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      if (!awaiting2FA) {
        setLoading(false);
      }
    }
  };

  const handleLinkBiometrics = async () => {
    setLinkingBiometrics(true);
    setError('');
    try {
      // Temporarily store token so registerBiometrics() can read it
      localStorage.setItem('token', tempToken);

      const { startRegistration } = await import('@simplewebauthn/browser');

      const resp = await fetch(`${API_URL}/auth/register/options`, {
        headers: { 'Authorization': `Bearer ${tempToken}` }
      });
      const options = await resp.json();
      const regResp = await startRegistration({ optionsJSON: options });

      const verifyResp = await fetch(`${API_URL}/auth/register/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tempToken}`
        },
        body: JSON.stringify({ username, response: regResp }),
      });
      const result = await verifyResp.json();

      if (result.status === 'ok') {
        onLogin(tempToken);
      } else {
        throw new Error('Biometric registration failed');
      }
    } catch (err) {
      setError('Biometric setup failed: ' + err.message + '. You cannot login without it.');
    } finally {
      setLinkingBiometrics(false);
    }
  };

  // --- 2FA Loading Screen ---
  if (awaiting2FA) {
    return (
      <div className="auth-container">
        <div className="auth-card glass">
          <div className="auth-header">
            <div className="auth-logo">👆</div>
            <h2>Verify Biometrics</h2>
            <p>Please complete the biometric prompt to finish logging in.</p>
          </div>
          {error && <div className="auth-error">{error}</div>}
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div className="spinner"></div>
          </div>
        </div>
      </div>
    );
  }

  // --- Biometric linking prompt shown right after signup ---
  if (justSignedUp) {
    return (
      <div className="auth-container">
        <div className="auth-card glass">
          <div className="auth-header">
            <div className="auth-logo">👆</div>
            <h2>Link Your Biometrics</h2>
            <p>
              You must link your device fingerprint or iris to complete registration.
              Works with Windows Hello, Touch ID, Face ID, and fingerprint sensors.
            </p>
          </div>

          {error && <div className="auth-error" style={{ marginBottom: '1rem' }}>{error}</div>}

          <button
            className="auth-submit"
            onClick={handleLinkBiometrics}
            disabled={linkingBiometrics}
            style={{ marginBottom: '1rem' }}
          >
            {linkingBiometrics ? '🔒 Registering biometric...' : '👆 Link Fingerprint / Iris'}
          </button>
        </div>
      </div>
    );
  }

  // --- Main login/signup form ---
  return (
    <div className="auth-container">
      <div className="auth-brand-banner">
        <div className="auth-brand-icon">🔬</div>
        <h1 className="auth-brand-title">Welcome to <span className="brand-highlight">ForensiX AI</span></h1>
        <p className="auth-brand-quote">"Your lens into forensic truth, frame by frame"</p>
      </div>

      <div className="auth-card">
        <div className="auth-form-wrapper glass">
          <div className="auth-header">
            <div className="auth-logo">🔍</div>
            <h2>{isLogin ? 'Forensic Login' : 'Agent Signup'}</h2>
            <p>{isLogin ? 'Enter your credentials to access the laboratory' : 'Create your forensic agent profile'}</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
          <div className="input-group">
            <label htmlFor="auth-username">Agent Identifier</label>
            <input
              id="auth-username"
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
            />
          </div>
          <div className="input-group">
            <label htmlFor="auth-password">Access Code</label>
            <input
              id="auth-password"
              type="password"
              placeholder={isLogin ? 'Password' : 'Password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required={!isLogin}
              autoComplete={isLogin ? 'current-password' : 'new-password'}
            />
          </div>

          {error && <div className="auth-error">{error}</div>}
          {success && <div style={{ color: 'var(--color-success)', fontSize: 'var(--font-size-sm)', padding: '0.5rem', borderRadius: 'var(--radius-sm)', background: 'rgba(34,197,94,0.1)', borderLeft: '3px solid var(--color-success)' }}>{success}</div>}

          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Authenticate' : 'Create Account')}
          </button>
        </form>

          <div className="auth-footer">
            <button onClick={() => { setIsLogin(!isLogin); setError(''); setSuccess(''); }} className="text-btn">
              {isLogin ? 'New Agent? Create Profile →' : '← Already Registered? Login'}
            </button>
          </div>
        </div>{/* end auth-form-wrapper */}
      </div>{/* end auth-card */}
    </div>
  );
};

export default Auth;
