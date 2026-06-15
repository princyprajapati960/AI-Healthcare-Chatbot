import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function AuthCallbackPage() {
  const [params] = useSearchParams();
  const { handleGoogleToken, refreshUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const token = params.get('token');
    if (token) {
      handleGoogleToken(token)
        .then(() => refreshUser())
        .then(() => api.me())
        .then((u) => navigate(u.onboarding_complete ? '/dashboard' : '/onboarding'))
        .catch(() => navigate('/login'));
    } else {
      navigate('/login');
    }
  }, [params, handleGoogleToken, refreshUser, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <p className="text-slate-600">Signing you in...</p>
    </div>
  );
}
