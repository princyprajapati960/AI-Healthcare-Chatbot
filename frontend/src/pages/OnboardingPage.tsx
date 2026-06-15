import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Globe } from 'lucide-react';
import { LANGUAGES } from '../i18n/strings';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [form, setForm] = useState({
    full_name: '',
    age: '',
    gender: '',
    address: '',
    phone: '',
    medical_history: '',
    language: 'en',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getProfile().then((p) => {
      if (p?.onboarding_complete) navigate('/dashboard');
      if (p) {
        setForm({
          full_name: p.full_name,
          age: String(p.age),
          gender: p.gender,
          address: p.address,
          phone: p.phone,
          medical_history: p.medical_history || '',
          language: p.language,
        });
      }
    }).catch(() => {});
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.saveProfile({
        full_name: form.full_name,
        age: parseInt(form.age, 10),
        gender: form.gender,
        address: form.address,
        phone: form.phone,
        medical_history: form.medical_history || null,
        language: form.language,
      });
      await refreshUser();
      navigate('/chat');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50 px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 text-white">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Patient Information</h1>
            <p className="text-sm text-slate-500">Tell us about yourself before starting consultation</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl border border-blue-100 bg-white p-6 shadow-xl sm:p-8">
          {error && <div className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600">{error}</div>}

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Full Name *</label>
              <input
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
                className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Age *</label>
              <input
                type="number"
                min={1}
                max={150}
                value={form.age}
                onChange={(e) => setForm({ ...form, age: e.target.value })}
                required
                className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Gender *</label>
              <select
                value={form.gender}
                onChange={(e) => setForm({ ...form, gender: e.target.value })}
                required
                className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-500"
              >
                <option value="">Select</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Address *</label>
              <input
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                required
                className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Phone Number *</label>
              <input
                type="tel"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                required
                className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-500"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Medical History (optional)</label>
              <textarea
                value={form.medical_history}
                onChange={(e) => setForm({ ...form, medical_history: e.target.value })}
                rows={3}
                className="w-full rounded-xl border border-slate-200 px-4 py-3 outline-none focus:border-blue-500"
                placeholder="Allergies, chronic conditions, medications..."
              />
            </div>
          </div>

          <div className="rounded-xl border-2 border-blue-200 bg-blue-50/50 p-5">
            <div className="mb-3 flex items-center gap-2">
              <Globe className="h-5 w-5 text-blue-600" />
              <h2 className="font-semibold text-slate-900">Select your preferred language *</h2>
            </div>
            <p className="mb-4 text-sm text-blue-700">
              This language will remain constant throughout your entire conversation — including voice output.
            </p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => setForm({ ...form, language: lang.code })}
                  className={`rounded-xl border-2 px-4 py-3 text-center transition ${
                    form.language === lang.code
                      ? 'border-blue-600 bg-blue-600 text-white shadow-lg'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                  }`}
                >
                  <div className="font-semibold">{lang.native}</div>
                  <div className="text-xs opacity-80">{lang.name}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 py-3.5 font-semibold text-white shadow-lg hover:opacity-95 disabled:opacity-60"
          >
            {loading ? 'Saving...' : 'Continue to Consultation'}
          </button>
        </form>
      </div>
    </div>
  );
}
