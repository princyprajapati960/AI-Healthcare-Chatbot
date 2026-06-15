import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Activity,
  HeartPulse,
  MessageSquare,
  Mic,
  Stethoscope,
  Users,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api, type ChatSession, type PatientProfile } from '../services/api';
import { LANGUAGES, t } from '../i18n/strings';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<PatientProfile | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);

  useEffect(() => {
    if (!user) return;
    if (!user.onboarding_complete) {
      navigate('/onboarding');
      return;
    }
    api.getProfile().then(setProfile);
    api.listSessions().then(setSessions).catch(() => {});
  }, [user, navigate]);

  const lang = profile?.language || 'en';
  const langName = LANGUAGES.find((l) => l.code === lang)?.native || 'English';

  const startConsultation = () => navigate('/chat');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/40 to-cyan-50/30">
      <header className="border-b border-blue-100 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 text-white">
              <Activity className="h-5 w-5" />
            </div>
            <span className="font-bold text-slate-900">MediVoice Dashboard</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700 sm:inline">
              {langName}
            </span>
            <span className="text-sm text-slate-600">{user?.name}</span>
            <button onClick={logout} className="rounded-lg px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100">
              {t('logout', lang)}
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">
            Welcome, {profile?.full_name || user?.name}!
          </h1>
          <p className="mt-2 text-slate-600">Your AI healthcare assistant is ready.</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="grid gap-4 sm:grid-cols-2">
              {[
                { icon: Stethoscope, title: 'AI Triage', desc: 'Smart department prediction from symptoms', color: 'blue' },
                { icon: Mic, title: 'Voice Assistant', desc: 'Speak and listen in your language', color: 'cyan' },
                { icon: HeartPulse, title: 'Health Guidance', desc: 'Empathetic follow-up questions', color: 'rose' },
                { icon: Users, title: 'Patient Care', desc: 'Doctors & patients connected via AI', color: 'emerald' },
              ].map((card) => (
                <div
                  key={card.title}
                  className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md"
                >
                  <card.icon className={`h-8 w-8 text-${card.color}-600 mb-3`} style={{ color: card.color === 'blue' ? '#2563eb' : card.color === 'cyan' ? '#0891b2' : card.color === 'rose' ? '#e11d48' : '#059669' }} />
                  <h3 className="font-semibold text-slate-900">{card.title}</h3>
                  <p className="mt-1 text-sm text-slate-600">{card.desc}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 overflow-hidden rounded-2xl border border-blue-100 bg-gradient-to-r from-blue-600 to-cyan-500 p-8 text-white shadow-xl">
              <h2 className="text-2xl font-bold">Start Your Consultation</h2>
              <p className="mt-2 max-w-lg text-blue-100">
                Chat with MediVoice AI in {langName}. Same language throughout — text and voice.
              </p>
              <button
                onClick={startConsultation}
                className="mt-6 rounded-full bg-white px-8 py-3 font-semibold text-blue-700 shadow-lg hover:bg-blue-50"
              >
                {t('startConsultation', lang)}
              </button>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-semibold text-slate-900">Your Profile</h3>
              {profile && (
                <dl className="mt-4 space-y-2 text-sm">
                  <div><dt className="text-slate-500">Age</dt><dd className="font-medium">{profile.age}</dd></div>
                  <div><dt className="text-slate-500">Gender</dt><dd className="font-medium">{profile.gender}</dd></div>
                  <div><dt className="text-slate-500">Language</dt><dd className="font-medium">{langName}</dd></div>
                  <div><dt className="text-slate-500">Phone</dt><dd className="font-medium">{profile.phone}</dd></div>
                </dl>
              )}
              <Link to="/onboarding" className="mt-4 inline-block text-sm text-blue-600 hover:underline">
                Edit profile
              </Link>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-slate-900">Recent Sessions</h3>
              </div>
              {sessions.length === 0 ? (
                <p className="mt-3 text-sm text-slate-500">No consultations yet.</p>
              ) : (
                <ul className="mt-3 space-y-2">
                  {sessions.slice(0, 5).map((s) => (
                    <li key={s.id} className="rounded-lg bg-slate-50 px-3 py-2 text-sm">
                      Session #{s.id} — {s.message_count} messages
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
