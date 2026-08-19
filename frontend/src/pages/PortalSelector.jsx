import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Video, Briefcase, ArrowRight, Sparkles, Users, FileText, Shield, MessageCircle,
  Hash, Globe, Download, Radio, Calendar, Search, CheckCircle2, Languages, Captions
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import GlobalLanguageSelector from '@/components/GlobalLanguageSelector';
import { useTranslation } from "@/utils/i18n";

const API = process.env.REACT_APP_BACKEND_URL;

const APPS = [
  {
    id: 'karau', name: 'AI KARAU', tagline: 'Meetings & Webinars',
    description: 'HD video meetings with AI transcription, screen sharing, and real-time collaboration.',
    companion: 'ENZI Messenger included', route: '/karau-meet', icon: Video,
    gradient: 'from-violet-500 to-indigo-600', badgeStyle: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
    logo: 'https://customer-assets.emergentagent.com/job_1fba32e3-e5a1-4174-b642-d1cd092309b3/artifacts/a7nojb8x_IMG_8477.jpeg',
    domains: ['connect.aikarau.com', 'meet.aikarau.com'],
    features: [
      { icon: Video, text: 'HD Video & Audio' },
      { icon: Captions, text: 'Live captions in 60 languages' },
      { icon: MessageCircle, text: 'Auto-includes ENZI Messenger' },
    ],
  },
  {
    id: 'enzi', name: 'ENZI', tagline: 'Actionable Intelligence Messenger',
    description: 'Team messaging with channels, bots, an @AI assistant, and end-to-end encryption.',
    companion: 'AI KARAU Meetings included', route: '/lumi', icon: MessageCircle,
    gradient: 'from-teal-400 to-cyan-500', badgeStyle: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
    lumiIcon: true, domains: ['enzi.aikarau.com', 'enzilink.com'],
    features: [
      { icon: Hash, text: 'Channels, DMs & Bots' },
      { icon: Sparkles, text: '@AI summaries & task nudges' },
      { icon: Video, text: 'Auto-includes AI KARAU' },
    ],
  },
  {
    id: 'medmatch', name: 'MedMatch AI', tagline: 'Career Intelligence Toolkit',
    description: 'AI-powered job search, resume builder, and interview preparation — your complete career toolkit.',
    companion: null, route: '/login', icon: Briefcase,
    gradient: 'from-emerald-400 to-teal-500', badgeStyle: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    logo: 'https://customer-assets.emergentagent.com/job_f139deea-35f2-4b55-91b9-9aab4dc4c84b/artifacts/9uzkkm0w_MedMatch%20Logo%20-%201MB.png',
    domains: ['medmatch.aikarau.com', 'careers.aikarau.com'],
    features: [
      { icon: FileText, text: 'AI Resume Parser' },
      { icon: Sparkles, text: 'Smart Job Matching' },
      { icon: Users, text: 'Recruiter Network' },
    ],
  },
];

const CAPTION_SAMPLES = {
  English: 'Welcome everyone — our revenue target for Q3 is ten million.',
  Français: 'Bienvenue à tous — notre objectif de revenus pour le T3 est de dix millions.',
  Español: 'Bienvenidos todos — nuestra meta de ingresos para el Q3 es de diez millones.',
  Kiswahili: 'Karibuni nyote — lengo letu la mapato kwa robo ya tatu ni milioni kumi.',
  中文: '欢迎大家 — 我们第三季度的收入目标是一千万。',
  العربية: 'مرحباً بالجميع — هدف إيراداتنا للربع الثالث هو عشرة ملايين.',
};

const TRANSCRIPT_DEMO = [
  { t: '10:02', s: 'Amina', x: 'Welcome to the quarterly webinar kickoff.' },
  { t: '10:05', s: 'David', x: 'Our revenue target for Q3 is ten million.' },
  { t: '10:09', s: 'Amina', x: 'Sarah will send the compound dataset by Monday.' },
  { t: '10:14', s: 'Mark', x: 'I will review the toxicity model results before Friday.' },
];

const fmtDate = (iso) => {
  if (!iso) return 'Date TBA';
  const d = new Date(iso);
  return isNaN(d) ? iso : d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const SectionHeading = ({ kicker, title, id }) => (
  <div className="mb-10" id={id}>
    <p className="text-xs font-mono uppercase tracking-[0.25em] text-teal-400 mb-3">{kicker}</p>
    <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight" style={{ fontFamily: "'Manrope', sans-serif" }}>{title}</h2>
  </div>
);

const WebinarCard = ({ w, navigate }) => (
  <Card className="bg-[#111827] border-[#1F2937] p-5 flex flex-col hover:border-violet-500/40 hover:-translate-y-1 transition-[transform,border-color] duration-200" data-testid={`upcoming-webinar-card-${w.webinar_id}`}>
    <div className="flex items-center justify-between mb-3">
      {w.status === 'live' ? (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-red-500/20 text-red-300 border border-red-500/30">
          <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" /><span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" /></span>
          LIVE NOW
        </span>
      ) : (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-violet-500/15 text-violet-300 border border-violet-500/25">
          <Calendar className="w-3 h-3" /> {fmtDate(w.scheduled_time)}
        </span>
      )}
      <span className="text-[11px] font-mono text-slate-500">{w.registered_count} registered</span>
    </div>
    <h3 className="text-lg font-bold text-white mb-1.5" style={{ fontFamily: "'Manrope', sans-serif" }}>{w.title}</h3>
    {w.description && <p className="text-sm text-slate-400 mb-3 leading-relaxed line-clamp-2">{w.description}</p>}
    <p className="text-xs text-slate-500 mb-4">Hosted by {w.host_name || 'AI KARAU'}</p>
    <button
      onClick={() => navigate(w.is_demo ? '/karau-meet' : `/karau-meet/webinar/${w.webinar_id}/register`)}
      data-testid={`webinar-register-btn-${w.webinar_id}`}
      className="mt-auto w-full py-2.5 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-violet-500 to-indigo-600 hover:shadow-lg hover:shadow-violet-500/20 flex items-center justify-center gap-2 transition-[box-shadow] duration-200"
    >
      {w.status === 'live' ? 'Join live' : 'Register free'} <ArrowRight className="w-4 h-4" />
    </button>
  </Card>
);

const CaptionsDemo = () => {
  const [lang, setLang] = useState('English');
  return (
    <Card className="bg-[#111827] border-[#1F2937] p-6 md:col-span-2">
      <div className="flex items-center gap-2 mb-4">
        <Languages className="w-5 h-5 text-teal-400" />
        <h3 className="text-lg font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>Live captions in 60 languages</h3>
      </div>
      <div className="flex flex-wrap gap-2 mb-4" data-testid="live-caption-language-selector">
        {Object.keys(CAPTION_SAMPLES).map((l) => (
          <button key={l} onClick={() => setLang(l)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors duration-150 ${lang === l ? 'bg-teal-500/20 text-teal-300 border-teal-500/40' : 'bg-white/[0.03] text-slate-400 border-white/[0.08] hover:text-white'}`}>
            {l}
          </button>
        ))}
      </div>
      <div className="rounded-xl bg-black/50 border border-white/[0.06] p-4" data-testid="live-caption-preview-box">
        <p className="text-[11px] font-mono text-teal-400 mb-1.5">SPEAKER · translated live</p>
        <p className="text-white text-base leading-relaxed">{CAPTION_SAMPLES[lang]}</p>
      </div>
      <p className="text-xs text-slate-500 mt-3">Every attendee picks their own language while the speaker talks — powered by Whisper + our translation engine.</p>
    </Card>
  );
};

const TranscriptDemo = () => {
  const [q, setQ] = useState('');
  const lines = TRANSCRIPT_DEMO.filter((l) => l.x.toLowerCase().includes(q.toLowerCase()));
  return (
    <Card className="bg-[#111827] border-[#1F2937] p-6">
      <div className="flex items-center gap-2 mb-4">
        <Search className="w-5 h-5 text-violet-400" />
        <h3 className="text-lg font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>Searchable transcripts</h3>
      </div>
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Try “revenue”…"
        data-testid="transcript-search-input"
        className="w-full mb-3 px-3 py-2 rounded-lg bg-black/40 border border-white/[0.08] text-sm text-white placeholder:text-slate-600 outline-none focus:border-violet-500/50" />
      <div className="space-y-2">
        {lines.map((l, i) => (
          <div key={i} className="flex gap-2 text-sm">
            <span className="font-mono text-[11px] text-slate-600 pt-0.5">{l.t}</span>
            <p className="text-slate-300"><span className="text-teal-400 font-semibold">{l.s}:</span> {l.x}</p>
          </div>
        ))}
        {lines.length === 0 && <p className="text-xs text-slate-600">No lines match — the real thing searches your whole meeting.</p>}
      </div>
    </Card>
  );
};

const PortalSelector = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [webinars, setWebinars] = useState([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/karau/webinar/public/upcoming`)
      .then((r) => (r.ok ? r.json() : { webinars: [] }))
      .then((d) => setWebinars(d.webinars || []))
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  const displayWebinars = webinars.length > 0 ? webinars : (loaded ? [
    { webinar_id: 'demo-1', title: 'Host your first AI webinar', description: 'Spin up a webinar with live multilingual captions, AI summaries and a raise-hand speaker queue in under a minute.', host_name: 'AI KARAU team', status: 'scheduled', registered_count: 0, is_demo: true },
  ] : []);
  const spotlight = displayWebinars[0];

  const scrollTo = (id) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });

  return (
    <div className="min-h-screen text-white" style={{ backgroundColor: '#0B0F19' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-slate-900/80 border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">
          <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="flex items-center gap-2.5" data-testid="landing-brand">
            <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-400 via-violet-500 to-pink-500 flex items-center justify-center"><Sparkles className="w-4 h-4 text-white" /></span>
            <span className="font-bold tracking-tight" style={{ fontFamily: "'Manrope', sans-serif" }}>aikarau<span className="text-teal-400">.com</span></span>
          </button>
          <nav className="hidden md:flex items-center gap-6 text-sm text-slate-400">
            <button onClick={() => scrollTo('webinars')} className="hover:text-white transition-colors duration-150" data-testid="nav-webinars-link">Webinars</button>
            <button onClick={() => scrollTo('features')} className="hover:text-white transition-colors duration-150" data-testid="nav-features-link">Features</button>
            <button onClick={() => scrollTo('portals')} className="hover:text-white transition-colors duration-150" data-testid="nav-portals-link">Apps</button>
            <button onClick={() => navigate('/downloads')} className="hover:text-white transition-colors duration-150" data-testid="nav-downloads-link">Downloads</button>
          </nav>
          <div className="flex items-center gap-2.5">
            <div data-testid="global-language-selector"><GlobalLanguageSelector compact /></div>
            <button onClick={() => navigate('/login')} data-testid="nav-sign-in-btn"
              className="px-4 py-2 rounded-full text-sm font-semibold bg-white/[0.06] border border-white/[0.1] hover:bg-white/[0.12] transition-colors duration-150">
              Sign in
            </button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute -top-24 left-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl" />
          <div className="absolute top-40 right-1/5 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 pt-16 lg:pt-24 pb-16 grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <p className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono bg-white/[0.04] border border-white/[0.08] text-teal-300 mb-6">
              <Radio className="w-3.5 h-3.5" /> Webinars people actually understand — in 60 languages
            </p>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.05] mb-6" style={{ fontFamily: "'Manrope', sans-serif" }} data-testid="landing-hero-heading">
              Run webinars that<br />
              <span className="text-transparent bg-clip-text" style={{ backgroundImage: 'linear-gradient(135deg, #00CEC9 0%, #6C5CE7 50%, #E84393 100%)' }}>speak every language</span>
            </h1>
            <p className="text-base text-slate-400 max-w-lg mb-8 leading-relaxed">
              Live multilingual captions, AI summaries with action items, searchable transcripts and attendee emails — all automatic, from your first webinar.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <button onClick={() => spotlight && !spotlight.is_demo ? navigate(`/karau-meet/webinar/${spotlight.webinar_id}/register`) : scrollTo('webinars')}
                data-testid="primary-webinar-signup-btn"
                className="px-7 py-3.5 rounded-full font-semibold text-sm bg-gradient-to-r from-violet-500 to-indigo-600 hover:shadow-xl hover:shadow-violet-500/25 flex items-center gap-2 transition-[box-shadow] duration-200">
                Save my webinar seat <ArrowRight className="w-4 h-4" />
              </button>
              <button onClick={() => navigate('/karau-meet')} data-testid="hero-host-btn"
                className="px-6 py-3.5 rounded-full font-semibold text-sm bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.1] transition-colors duration-150">
                Host your own
              </button>
            </div>
            <div className="flex flex-wrap gap-x-6 gap-y-2 mt-8 text-xs text-slate-500 font-mono">
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-teal-400" /> 60-language live captions</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-teal-400" /> AI summaries & tasks</span>
              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-teal-400" /> Free to attend</span>
            </div>
          </div>
          {/* Spotlight webinar */}
          {spotlight && (
            <Card className="bg-[#111827]/90 border-[#1F2937] p-7 backdrop-blur-xl relative" data-testid="spotlight-webinar-card">
              <p className="text-[11px] font-mono uppercase tracking-[0.2em] text-violet-400 mb-3">Next webinar</p>
              <h3 className="text-xl sm:text-2xl font-bold mb-2 text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>{spotlight.title}</h3>
              {spotlight.description && <p className="text-sm text-slate-400 mb-4 leading-relaxed">{spotlight.description}</p>}
              <div className="flex items-center gap-4 text-xs text-slate-500 mb-6 font-mono">
                <span className="flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5" />{spotlight.status === 'live' ? 'Live now' : fmtDate(spotlight.scheduled_time)}</span>
                <span className="flex items-center gap-1.5"><Users className="w-3.5 h-3.5" />{spotlight.registered_count} registered</span>
              </div>
              <button onClick={() => navigate(spotlight.is_demo ? '/karau-meet' : `/karau-meet/webinar/${spotlight.webinar_id}/register`)}
                data-testid="spotlight-register-btn"
                className="w-full py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-teal-400 to-cyan-500 text-slate-900 hover:shadow-lg hover:shadow-teal-500/25 flex items-center justify-center gap-2 transition-[box-shadow] duration-200">
                {spotlight.is_demo ? 'Create it now' : 'Register free'} <ArrowRight className="w-4 h-4" />
              </button>
            </Card>
          )}
        </div>
      </section>

      {/* Upcoming webinars */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 lg:py-24">
        <SectionHeading kicker="Reserve a seat" title="Upcoming & live webinars" id="webinars" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="upcoming-webinars-grid">
          {displayWebinars.map((w) => <WebinarCard key={w.webinar_id} w={w} navigate={navigate} />)}
        </div>
      </section>

      {/* Feature bento */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 lg:py-24">
        <SectionHeading kicker="Why attendees love it" title="AI that works the room for you" id="features" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CaptionsDemo />
          <TranscriptDemo />
          <Card className="bg-[#111827] border-[#1F2937] p-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-pink-400" />
              <h3 className="text-lg font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>AI summaries & action items</h3>
            </div>
            <div className="rounded-xl bg-black/40 border border-white/[0.06] p-4 text-sm space-y-2">
              <p className="text-slate-300 font-semibold">Key decisions</p>
              <p className="text-slate-400">• Q3 revenue target set at ten million</p>
              <p className="text-slate-300 font-semibold pt-1">Action items</p>
              <p className="text-slate-400">☐ Send compound dataset — <span className="text-teal-400">@Sarah</span></p>
              <p className="text-slate-400">☐ Review toxicity results — <span className="text-teal-400">@Mark</span></p>
            </div>
            <p className="text-xs text-slate-500 mt-3">Emailed to every attendee with the transcript PDF the moment the webinar ends.</p>
          </Card>
          <Card className="bg-[#111827] border-[#1F2937] p-6 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <MessageCircle className="w-5 h-5 text-teal-400" />
              <h3 className="text-lg font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>ENZI — the messenger with an @AI teammate</h3>
            </div>
            <div className="rounded-xl bg-black/40 border border-white/[0.06] p-4 space-y-3 text-sm">
              <p><span className="text-slate-500 font-mono text-xs mr-2">you</span><span className="text-slate-300">@AI summarize this conversation</span></p>
              <p><span className="text-teal-400 font-mono text-xs mr-2">ENZI AI</span><span className="text-slate-400">Key topics: Q3 launch scope agreed. Open question: pricing tier for EDU. 2 action items assigned.</span></p>
              <p><span className="text-slate-500 font-mono text-xs mr-2">you</span><span className="text-slate-300">done 2</span></p>
              <p><span className="text-teal-400 font-mono text-xs mr-2">ENZI AI</span><span className="text-slate-400">✅ Marked “Review pricing tier” done. 1 task still open.</span></p>
            </div>
          </Card>
        </div>
      </section>

      {/* Portals */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-16 lg:py-24">
        <SectionHeading kicker="One account, three apps" title="The AI KARAU suite" id="portals" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {APPS.map((app) => (
            <Card key={app.id} data-testid={`portal-card-${app.id}`} onClick={() => navigate(app.route)}
              className="relative overflow-hidden cursor-pointer bg-[#111827] border-[#1F2937] hover:border-slate-500/50 hover:-translate-y-1.5 transition-[transform,border-color] duration-200 group">
              {app.companion && (
                <span className={`absolute top-4 right-4 z-10 inline-flex px-2.5 py-1 rounded-full text-[10px] font-semibold border ${app.badgeStyle}`}>Auto-bundled</span>
              )}
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden ring-2 ring-white/10" style={{ backgroundColor: app.lumiIcon ? '#0B0F1A' : undefined }}>
                    {app.lumiIcon ? <img src="/enzi-logo-icon.png" alt="ENZI" className="w-9 h-9 object-contain" />
                      : app.logo ? <img src={app.logo} alt={app.name} className="w-full h-full object-cover" />
                      : <app.icon className="w-6 h-6 text-white" />}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white" style={{ fontFamily: "'Manrope', sans-serif" }}>{app.name}</h3>
                    <p className={`text-xs font-medium bg-gradient-to-r ${app.gradient} bg-clip-text text-transparent`}>{app.tagline}</p>
                  </div>
                </div>
                <p className="text-sm text-slate-400 mb-4 leading-relaxed min-h-[44px]">{app.description}</p>
                <div className="space-y-2 mb-5">
                  {app.features.map((f, i) => (
                    <div key={i} className="flex items-center gap-2.5 text-sm text-slate-300">
                      <f.icon className="w-4 h-4 text-slate-500" /><span>{f.text}</span>
                    </div>
                  ))}
                </div>
                <div className="flex flex-wrap gap-1.5 mb-5">
                  {app.domains.map((d) => (
                    <span key={d} className="text-[10px] text-slate-500 bg-white/[0.04] px-2 py-0.5 rounded-md font-mono" data-testid={`domain-${d.replace(/\./g, '-')}`}>{d}</span>
                  ))}
                </div>
                <button data-testid={`open-${app.id}-btn`}
                  className={`w-full py-3 rounded-xl font-semibold text-sm text-white bg-gradient-to-r ${app.gradient} flex items-center justify-center gap-2 group-hover:gap-3 transition-[gap,box-shadow] duration-200 hover:shadow-lg`}>
                  Open {app.name} <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Downloads banner */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pb-16">
        <Card className="bg-gradient-to-r from-violet-600/20 to-teal-500/15 border-white/[0.08] p-8 flex flex-col sm:flex-row items-center justify-between gap-5">
          <div>
            <h3 className="text-xl font-bold text-white mb-1" style={{ fontFamily: "'Manrope', sans-serif" }}>Take the suite with you</h3>
            <p className="text-sm text-slate-400">Desktop apps for macOS & Windows, mobile for iOS & Android.</p>
          </div>
          <button onClick={() => navigate('/downloads')} data-testid="downloads-banner-link"
            className="px-6 py-3 rounded-full font-semibold text-sm bg-white text-slate-900 hover:bg-slate-200 flex items-center gap-2 transition-colors duration-150 flex-shrink-0">
            <Download className="w-4 h-4" /> Get the apps
          </button>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-500">© {new Date().getFullYear()} AI KARAU · {t('pages.portalSelector.poweredByAI')}</p>
          <div className="flex items-center gap-5 text-xs text-slate-400">
            <button onClick={() => navigate('/legal/privacy')} className="hover:text-white transition-colors duration-150" data-testid="footer-privacy-link">Privacy</button>
            <button onClick={() => navigate('/legal/terms')} className="hover:text-white transition-colors duration-150" data-testid="footer-terms-link">Terms</button>
            <button onClick={() => navigate('/downloads')} className="hover:text-white transition-colors duration-150" data-testid="footer-downloads-link">Downloads</button>
            <span className="flex items-center gap-1.5 text-emerald-400"><span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> All systems live</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PortalSelector;
