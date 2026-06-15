import { Link } from 'react-router-dom';
import {
  Activity,
  Brain,
  Globe,
  HeartPulse,
  Mic,
  Shield,
  Sparkles,
  Stethoscope,
  Users,
} from 'lucide-react';
import Navbar from '../components/Navbar';

const features = [
  {
    icon: Globe,
    title: 'Same-Language Continuity',
    desc: 'Hindi, Marathi, Gujarati, or English — the assistant stays in your language for the entire session.',
  },
  {
    icon: Brain,
    title: 'ML Medical Triage',
    desc: 'TF-IDF + Logistic Regression predicts the right department from your symptoms.',
  },
  {
    icon: Mic,
    title: 'Voice Assistant',
    desc: 'Speak naturally and hear responses aloud — Copilot-style voice interaction.',
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    desc: 'Your profile, language preference, and chat history stored securely.',
  },
];

const services = [
  { title: 'Symptom Assessment', desc: 'Intelligent follow-up questions to understand your condition.' },
  { title: 'Department Routing', desc: 'Cardiology, Neurology, Dermatology, and more.' },
  { title: 'Multilingual Support', desc: 'Full conversation in English, Hindi, Marathi, Gujarati.' },
  { title: 'Voice Consultation', desc: 'Hands-free healthcare guidance with TTS playback.' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-blue-50/30 to-cyan-50/20">
      <Navbar />

      {/* Hero */}
      <section className="relative overflow-hidden px-4 pb-20 pt-28 sm:px-6 lg:pt-32">
        <div className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="pointer-events-none absolute -left-32 top-64 h-80 w-80 rounded-full bg-blue-400/20 blur-3xl" />

        <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-2">
          <div className="animate-fade-in-up">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-700">
              <Sparkles className="h-4 w-4" />
              AI Healthcare Innovation
            </div>
            <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Your Multilingual{' '}
              <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
                Medical Triage
              </span>{' '}
              Agent
            </h1>
            <p className="mt-6 max-w-xl text-lg text-slate-600">
              MediVoice AI is a professional healthcare assistant with voice support, intelligent triage,
              and same-language conversation — like Microsoft Copilot for healthcare.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/register"
                className="rounded-full bg-gradient-to-r from-blue-600 to-cyan-500 px-8 py-3.5 text-base font-semibold text-white shadow-xl shadow-blue-500/30 transition hover:scale-[1.02]"
              >
                Get Started Free
              </Link>
              <a
                href="#features"
                className="rounded-full border border-slate-200 bg-white px-8 py-3.5 text-base font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
              >
                Learn More
              </a>
            </div>
          </div>

          <div className="relative animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
            <div className="rounded-3xl border border-blue-100 bg-white/70 p-6 shadow-2xl shadow-blue-500/10 backdrop-blur">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 text-white">
                  <Stethoscope className="h-6 w-6" />
                </div>
                <div>
                  <p className="font-semibold text-slate-900">MediVoice Assistant</p>
                  <p className="text-sm text-emerald-600">● Online — Hindi session</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="ml-auto max-w-[85%] rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-3 text-sm text-white">
                  मुझे सीने में दर्द हो रहा है
                </div>
                <div className="max-w-[90%] rounded-2xl rounded-tl-sm bg-slate-100 px-4 py-3 text-sm text-slate-800">
                  नमस्ते! मैं समझता/समझती हूँ। क्या दर्द अचानक शुरू हुआ? सांस लेने में परेशानी भी है?
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <HeartPulse className="h-4 w-4 text-red-500" />
                  Suggested: हृदय रोग विभाग (Cardiology)
                </div>
              </div>
            </div>
            <div className="absolute -bottom-4 -left-4 rounded-2xl border border-white bg-white p-4 shadow-lg">
              <Users className="h-8 w-8 text-blue-600" />
              <p className="mt-1 text-xs font-medium text-slate-600">Doctors & Patients</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="px-4 py-20 sm:px-6">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-slate-900 sm:text-4xl">Powerful Features</h2>
            <p className="mt-3 text-slate-600">Built for real healthcare conversations, not simple FAQ bots.</p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-2xl border border-blue-100 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-500/10"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 transition group-hover:bg-blue-600 group-hover:text-white">
                  <f.icon className="h-6 w-6" />
                </div>
                <h3 className="font-semibold text-slate-900">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About */}
      <section id="about" className="bg-white px-4 py-20 sm:px-6">
        <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-2">
          <div className="rounded-3xl bg-gradient-to-br from-blue-600 to-cyan-500 p-8 text-white shadow-xl">
            <Activity className="h-12 w-12 opacity-90" />
            <h2 className="mt-4 text-3xl font-bold">About MediVoice AI</h2>
            <p className="mt-4 leading-relaxed text-blue-100">
              We combine NLP, machine learning triage, and voice AI to deliver a Copilot-style healthcare
              experience. Our core innovation: every reply stays in your chosen language — greetings,
              medical terms, suggestions, and voice output included.
            </p>
          </div>
          <div>
            <h3 className="text-2xl font-bold text-slate-900">Why Same-Language Matters</h3>
            <ul className="mt-6 space-y-4">
              {[
                'Patients express symptoms more clearly in their native language',
                'Medical guidance is easier to understand without English mixing',
                'Voice assistant speaks naturally in Hindi, Marathi, or Gujarati',
                'Trust and comfort increase with culturally appropriate responses',
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-slate-600">
                  <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-cyan-500" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Services */}
      <section id="services" className="px-4 py-20 sm:px-6">
        <div className="mx-auto max-w-7xl">
          <h2 className="text-center text-3xl font-bold text-slate-900">Our Services</h2>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {services.map((s) => (
              <div key={s.title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h3 className="font-semibold text-blue-700">{s.title}</h3>
                <p className="mt-2 text-sm text-slate-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact */}
      <section id="contact" className="bg-gradient-to-r from-blue-600 to-cyan-500 px-4 py-20 sm:px-6">
        <div className="mx-auto max-w-3xl text-center text-white">
          <h2 className="text-3xl font-bold">Ready to Start?</h2>
          <p className="mt-4 text-blue-100">Create an account and begin your multilingual healthcare consultation today.</p>
          <Link
            to="/register"
            className="mt-8 inline-block rounded-full bg-white px-8 py-3.5 font-semibold text-blue-700 shadow-lg hover:bg-blue-50"
          >
            Start Free Consultation
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white px-4 py-10 sm:px-6">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-slate-500">© 2026 MediVoice AI. AI guidance only — not a substitute for professional medical care.</p>
          <div className="flex gap-6 text-sm text-slate-500">
            <a href="#features" className="hover:text-blue-600">Features</a>
            <a href="#about" className="hover:text-blue-600">About</a>
            <a href="#contact" className="hover:text-blue-600">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
