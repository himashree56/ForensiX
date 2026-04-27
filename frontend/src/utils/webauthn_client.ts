import { 
  startRegistration, 
  startAuthentication 
} from '@simplewebauthn/browser';

const API_URL = 'http://localhost:8000';

export async function registerBiometrics() {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('Not authenticated');

  // 1. Get registration options from server
  const resp = await fetch(`${API_URL}/auth/register/options`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const options = await resp.json();

  // 2. Start biometric registration
  const regResp = await startRegistration(options);

  // 3. Verify registration with server
  const verifyResp = await fetch(`${API_URL}/auth/register/verify`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ 
      username: '', // Server knows from token
      response: regResp 
    }),
  });

  const verification = await verifyResp.json();
  if (verification.status !== 'ok') {
    throw new Error('Biometric registration failed');
  }

  return true;
}

export async function loginWithBiometrics(username: string) {
  // 1. Get login options from server
  const resp = await fetch(`${API_URL}/auth/login/biometric/options?username=${username}`);
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || 'Failed to get login options');
  }
  
  const options = await resp.json();

  // 2. Start biometric authentication
  const authResp = await startAuthentication(options);

  // 3. Verify authentication with server
  const verifyResp = await fetch(`${API_URL}/auth/login/biometric/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      username, 
      response: authResp 
    }),
  });

  const data = await verifyResp.json();
  if (!verifyResp.ok) {
    throw new Error(data.detail || 'Biometric login failed');
  }

  // Store JWT
  localStorage.setItem('token', data.access_token);
  return data;
}
