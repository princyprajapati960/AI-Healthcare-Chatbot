import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  ArrowLeft,
  Mic,
  MicOff,
  Send,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api, type ChatMessage } from '../services/api';
import { LANGUAGES, t } from '../i18n/strings';
import { useVoice } from '../hooks/useVoice';

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <span className="typing-dot h-2 w-2 rounded-full bg-slate-400" />
      <span className="typing-dot h-2 w-2 rounded-full bg-slate-400" />
      <span className="typing-dot h-2 w-2 rounded-full bg-slate-400" />
    </div>
  );
}

export default function ChatPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [language, setLanguage] = useState('en');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  const { listening, transcript, setTranscript, startListening, stopListening, playAudio } = useVoice(language);

  useEffect(() => {
    if (!user?.onboarding_complete) {
      navigate('/onboarding');
      return;
    }

    const init = async () => {
      const profile = await api.getProfile();
      if (!profile) {
        navigate('/onboarding');
        return;
      }
      setLanguage(profile.language);
      const session = await api.createSession();
      setSessionId(session.id);
      const msgs = await api.getMessages(session.id);
      setMessages(msgs);
      const greeting = msgs.find((m) => m.role === 'assistant');
      if (greeting) {
        api.tts(greeting.content, profile.language).then(playAudio).catch(() => {});
      }
    };
    init();
  }, [user, navigate]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typing]);

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
      setTranscript('');
    }
  }, [transcript, setTranscript]);

  const speak = useCallback(
    async (text: string) => {
      try {
        const blob = await api.tts(text, language);
        playAudio(blob);
      } catch {
        /* browser may block or gTTS unavailable */
      }
    },
    [language, playAudio],
  );

  const sendMessage = async () => {
    if (!input.trim() || !sessionId || loading) return;
    const content = input.trim();
    setInput('');
    setLoading(true);
    setTyping(true);

    const tempUser: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUser]);

    try {
      const reply = await api.sendMessage(content, sessionId);
      setMessages((prev) => [...prev, reply]);
      if (autoSpeak) await speak(reply.content);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: t('errorGeneric', language),
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
      setTyping(false);
    }
  };

  const endSession = async () => {
    if (!sessionId) return;
    const res = await api.endSession(sessionId);
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: 'assistant',
        content: res.message,
        created_at: new Date().toISOString(),
      },
    ]);
    if (autoSpeak) await speak(res.message);
    setTimeout(() => navigate('/dashboard'), 3000);
  };

  const langName = LANGUAGES.find((l) => l.code === language)?.native || 'English';

  return (
    <div className="flex h-screen flex-col bg-gradient-to-b from-slate-50 to-blue-50/30">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-blue-100 bg-white/90 px-4 py-3 backdrop-blur">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/dashboard')} className="rounded-lg p-2 hover:bg-slate-100">
            <ArrowLeft className="h-5 w-5 text-slate-600" />
          </button>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 text-white">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold text-slate-900">MediVoice Assistant</p>
            <p className="text-xs text-emerald-600">● Active — {langName}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoSpeak(!autoSpeak)}
            className={`rounded-lg p-2 ${autoSpeak ? 'bg-blue-100 text-blue-700' : 'text-slate-500 hover:bg-slate-100'}`}
            title={t('autoSpeak', language)}
          >
            {autoSpeak ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
          </button>
          <button
            onClick={endSession}
            className="rounded-lg bg-red-50 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-100"
          >
            {t('endSession', language)}
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="mx-auto max-w-3xl space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
            >
              <div
                className={`group relative max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                  msg.role === 'user'
                    ? 'rounded-tr-sm bg-gradient-to-r from-blue-600 to-blue-500 text-white'
                    : 'rounded-tl-sm border border-slate-200 bg-white text-slate-800'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                {msg.triage_department && msg.role === 'assistant' && (
                  <p className="mt-2 text-xs opacity-70">
                    Triage: {msg.triage_department}
                    {msg.triage_confidence ? ` (${Math.round(msg.triage_confidence * 100)}%)` : ''}
                  </p>
                )}
                {msg.role === 'assistant' && (
                  <button
                    onClick={() => speak(msg.content)}
                    className="absolute -right-2 -bottom-2 rounded-full border border-slate-200 bg-white p-1.5 text-blue-600 opacity-0 shadow transition group-hover:opacity-100"
                  >
                    <Volume2 className="h-3.5 w-3.5" />
                  </button>
                )}
                <p className={`mt-1 text-[10px] ${msg.role === 'user' ? 'text-blue-200' : 'text-slate-400'}`}>
                  {new Date(msg.created_at).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          {typing && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-tl-sm border border-slate-200 bg-white shadow-sm">
                <TypingIndicator />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input bar — Copilot style */}
      <div className="border-t border-blue-100 bg-white/90 px-4 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-end gap-2">
          <button
            onClick={listening ? stopListening : startListening}
            className={`relative flex h-12 w-12 shrink-0 items-center justify-center rounded-full transition ${
              listening
                ? 'mic-pulse bg-blue-600 text-white'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
            title={listening ? t('listening', language) : 'Voice input'}
          >
            {listening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </button>

          <div className="flex flex-1 items-end rounded-2xl border border-slate-200 bg-white shadow-sm focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-500/20">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder={t('typeMessage', language)}
              rows={1}
              className="max-h-32 flex-1 resize-none bg-transparent px-4 py-3 outline-none"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="m-2 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white disabled:opacity-40"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
        {listening && (
          <p className="mx-auto mt-2 max-w-3xl text-center text-sm text-blue-600 animate-pulse">
            {t('listening', language)}
          </p>
        )}
      </div>
    </div>
  );
}
