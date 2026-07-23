const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function registerBiometrics() {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Not authenticated');

  const { startRegistration } = await import('@simplewebauthn/browser');

  // 1. Get registration options from server
  const resp = await fetch(`${API_URL}/auth/register/options`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || 'Failed to get registration options');
  }
  const options = await resp.json();

  // 2. Trigger device biometric prompt
  const regResp = await startRegistration(options);

  // 3. Verify with server
  const verifyResp = await fetch(`${API_URL}/auth/register/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ username: '', response: regResp }),
  });

  const verification = await verifyResp.json();
  if (verification.status !== 'ok') {
    throw new Error('Biometric registration failed');
  }
  return true;
}

export async function loginWithBiometrics(username) {
  const { startAuthentication } = await import('@simplewebauthn/browser');

  // 1. Get challenge from server
  const resp = await fetch(`${API_URL}/auth/login/biometric/options?username=${encodeURIComponent(username)}`);
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || 'Failed to get biometric login options');
  }
  const options = await resp.json();

  // 2. Trigger device biometric prompt
  const authResp = await startAuthentication(options);

  // 3. Verify with server and get JWT
  const verifyResp = await fetch(`${API_URL}/auth/login/biometric/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, response: authResp }),
  });

  const data = await verifyResp.json();
  if (!verifyResp.ok) {
    throw new Error(data.detail || 'Biometric login failed');
  }

  localStorage.setItem('token', data.access_token);
  return data;
}
