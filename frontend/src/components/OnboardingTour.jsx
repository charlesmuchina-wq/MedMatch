import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  X, ChevronRight, ChevronLeft, Search, FileText, Target,
  Mic, PenTool, BarChart3, Sparkles, CheckCircle2, Upload,
  Users, Briefcase, Shield, Globe, Video, Zap
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useTranslation } from "@/utils/i18n";

const API = process.env.REACT_APP_BACKEND_URL;

const OnboardingTour = ({ onComplete, user }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [selectedRole, setSelectedRole] = useState('');

  const INTERESTS = [
    { id: 'biotech', label: 'Biotechnology', icon: '🧬' },
    { id: 'pharma', label: 'Pharmaceuticals', icon: '💊' },
    { id: 'medical', label: 'Medical Devices', icon: '🩺' },
    { id: 'research', label: 'Clinical Research', icon: '🔬' },
    { id: 'data', label: 'Data Science', icon: '📊' },
    { id: 'engineering', label: 'Engineering', icon: '⚙️' },
    { id: 'regulatory', label: 'Regulatory Affairs', icon: '📋' },
    { id: 'quality', label: 'Quality Assurance', icon: '✅' },
  ];

  const ROLES = [
    { id: 'candidate', label: 'Job Seeker', desc: 'Find your next role' },
    { id: 'recruiter', label: 'Recruiter', desc: 'Source top talent' },
    { id: 'manager', label: 'Hiring Manager', desc: 'Build your team' },
  ];

  const tourSteps = [
    {
      id: "welcome",
      title: "Welcome to MedMatch",
      description: "Your AI-powered life sciences career platform. Let's get you set up in under a minute.",
      icon: Sparkles,
      content: 'welcome'
    },
    {
      id: "role",
      title: "What's your role?",
      description: "This helps us personalize your experience and show you the right tools.",
      icon: Users,
      content: 'role'
    },
    {
      id: "interests",
      title: "Select your interests",
      description: "Choose areas you're interested in to get personalized recommendations.",
      icon: Target,
      content: 'interests'
    },
    {
      id: "features",
      title: "Your Toolkit",
      description: "Here's what you can do with MedMatch. Click any feature to explore.",
      icon: Zap,
      content: 'features'
    },
    {
      id: "complete",
      title: "You're all set!",
      description: "Your profile is configured. Jump right into the platform.",
      icon: CheckCircle2,
      content: 'complete'
    }
  ];

  const step = tourSteps[currentStep];
  const isLastStep = currentStep === tourSteps.length - 1;
  const isFirstStep = currentStep === 0;
  const progress = ((currentStep + 1) / tourSteps.length) * 100;

  const handleNext = () => {
    if (isLastStep) handleComplete();
    else setCurrentStep(currentStep + 1);
  };

  const handlePrev = () => { if (!isFirstStep) setCurrentStep(currentStep - 1); };

  const handleComplete = async () => {
    // Save preferences
    try {
      await fetch(`${API}/api/profile/preferences`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: selectedRole, interests: selectedInterests })
      });
    } catch {}
    localStorage.setItem("medmatch-tour-completed", "true");
    localStorage.setItem("medmatch_tour_completed", "true");
    setIsVisible(false);
    if (onComplete) onComplete();
  };

  if (!isVisible) return null;

  const FEATURE_CARDS = [
    { icon: Search, title: "Smart Job Search", desc: "AI-powered matching", path: "/search", color: "from-blue-500/20 to-cyan-500/20 text-blue-400" },
    { icon: FileText, title: "Resume Builder", desc: "ATS-optimized format", path: "/resume", color: "from-teal-500/20 to-emerald-500/20 text-teal-400" },
    { icon: Mic, title: "Interview Prep", desc: "AI mock interviews", path: "/interview", color: "from-violet-500/20 to-pink-500/20 text-violet-400" },
    { icon: BarChart3, title: "Career Analytics", desc: "Track your progress", path: "/analytics", color: "from-amber-500/20 to-orange-500/20 text-amber-400" },
    { icon: Video, title: "AI KARAU Meet", desc: "Smart video meetings", path: "/", color: "from-red-500/20 to-pink-500/20 text-red-400" },
    { icon: Shield, title: "Blind Screening", desc: "Fair hiring tools", path: "/predictor", color: "from-emerald-500/20 to-teal-500/20 text-emerald-400" },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" data-testid="onboarding-tour">
      <Card className="w-full max-w-xl shadow-2xl border border-slate-700/60 bg-slate-900 overflow-hidden">
        <CardContent className="p-0">
          {/* Progress bar */}
          <div className="h-1.5 bg-slate-800">
            <div className="h-full bg-gradient-to-r from-teal-500 to-cyan-400 transition-all duration-500 ease-out rounded-r-full"
              style={{ width: `${progress}%` }} />
          </div>

          <div className="p-5 md:p-6">
            {/* Header */}
            <div className="flex items-start justify-between mb-5">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-teal-500/30 to-cyan-500/30 flex items-center justify-center">
                  <step.icon className="w-5 h-5 text-teal-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                  <p className="text-xs text-slate-400">Step {currentStep + 1} of {tourSteps.length}</p>
                </div>
              </div>
              <button onClick={handleComplete} className="p-1 text-slate-500 hover:text-slate-300 transition-colors"
                data-testid="onboarding-skip" aria-label="Skip tour">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-sm text-slate-300 mb-5 leading-relaxed">{step.description}</p>

            {/* Step Content */}
            {step.content === 'welcome' && (
              <div className="space-y-3 mb-5">
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { icon: Search, label: "AI Matching", val: "95%" },
                    { icon: Users, label: "Talent Pool", val: "10K+" },
                    { icon: Globe, label: "Languages", val: "50+" },
                  ].map(s => (
                    <div key={s.label} className="p-3 rounded-lg bg-slate-800/60 border border-slate-700/40 text-center">
                      <s.icon className="w-4 h-4 text-teal-400 mx-auto mb-1" />
                      <p className="text-sm font-bold text-white">{s.val}</p>
                      <p className="text-[10px] text-slate-500">{s.label}</p>
                    </div>
                  ))}
                </div>
                {user?.name && (
                  <p className="text-sm text-teal-400 bg-teal-500/10 rounded-lg p-2.5 border border-teal-500/20">
                    <Sparkles className="w-3.5 h-3.5 inline mr-1.5" /> Welcome, {user.name}! Let's personalize your experience.
                  </p>
                )}
              </div>
            )}

            {step.content === 'role' && (
              <div className="space-y-2 mb-5">
                {ROLES.map(r => (
                  <button key={r.id} onClick={() => setSelectedRole(r.id)}
                    className={`w-full p-3 rounded-lg border text-left flex items-center gap-3 transition-all ${selectedRole === r.id ? 'border-teal-500 bg-teal-500/10' : 'border-slate-700 bg-slate-800/40 hover:border-slate-600'}`}
                    data-testid={`role-${r.id}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${selectedRole === r.id ? 'bg-teal-500/20' : 'bg-slate-700/50'}`}>
                      {selectedRole === r.id ? <CheckCircle2 className="w-4 h-4 text-teal-400" /> : <Users className="w-4 h-4 text-slate-500" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{r.label}</p>
                      <p className="text-[10px] text-slate-400">{r.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {step.content === 'interests' && (
              <div className="grid grid-cols-2 gap-2 mb-5">
                {INTERESTS.map(i => (
                  <button key={i.id} onClick={() => setSelectedInterests(prev => prev.includes(i.id) ? prev.filter(x => x !== i.id) : [...prev, i.id])}
                    className={`p-2.5 rounded-lg border text-left flex items-center gap-2 transition-all ${selectedInterests.includes(i.id) ? 'border-teal-500 bg-teal-500/10' : 'border-slate-700 bg-slate-800/40 hover:border-slate-600'}`}
                    data-testid={`interest-${i.id}`}>
                    <span className="text-sm">{i.icon}</span>
                    <span className="text-xs text-white">{i.label}</span>
                  </button>
                ))}
              </div>
            )}

            {step.content === 'features' && (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-5">
                {FEATURE_CARDS.map(f => (
                  <button key={f.title} onClick={() => { handleComplete(); navigate(f.path); }}
                    className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/40 hover:border-teal-500/30 transition-all text-left group"
                    data-testid={`feature-${f.title.toLowerCase().replace(/\s/g, '-')}`}>
                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${f.color} flex items-center justify-center mb-2`}>
                      <f.icon className="w-4 h-4" />
                    </div>
                    <p className="text-xs font-medium text-white">{f.title}</p>
                    <p className="text-[10px] text-slate-500">{f.desc}</p>
                  </button>
                ))}
              </div>
            )}

            {step.content === 'complete' && (
              <div className="text-center py-4 mb-5">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-teal-500/30 to-emerald-500/30 flex items-center justify-center mx-auto mb-3">
                  <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                </div>
                <p className="text-sm text-slate-300 mb-4">
                  {selectedRole && <span>Role: <Badge className="bg-teal-500/20 text-teal-400 text-[10px]">{selectedRole}</Badge> </span>}
                  {selectedInterests.length > 0 && <span>| {selectedInterests.length} interests selected</span>}
                </p>
                <div className="flex gap-2 justify-center">
                  <Button size="sm" className="bg-teal-600 hover:bg-teal-500 text-xs" onClick={() => { handleComplete(); navigate('/search'); }} data-testid="goto-search">
                    <Search className="w-3 h-3 mr-1" /> Search Jobs
                  </Button>
                  <Button size="sm" variant="outline" className="border-slate-600 text-slate-300 text-xs" onClick={() => { handleComplete(); navigate('/resume'); }}>
                    <Upload className="w-3 h-3 mr-1" /> Upload Resume
                  </Button>
                </div>
              </div>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
              <Button variant="ghost" size="sm" onClick={handlePrev} disabled={isFirstStep} className="text-slate-400">
                <ChevronLeft className="w-4 h-4 mr-1" /> Back
              </Button>
              <div className="flex items-center gap-1.5">
                {tourSteps.map((_, idx) => (
                  <div key={idx}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${idx === currentStep ? 'bg-teal-400 w-4' : idx < currentStep ? 'bg-teal-500/50' : 'bg-slate-600'}`} />
                ))}
              </div>
              <Button size="sm" onClick={handleNext} className="bg-teal-600 hover:bg-teal-500" data-testid="onboarding-next">
                {isLastStep ? 'Get Started' : 'Next'} {!isLastStep && <ChevronRight className="w-4 h-4 ml-1" />}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export const useOnboardingTour = () => {
  const [showTour, setShowTour] = useState(false);
  useEffect(() => {
    const done = localStorage.getItem("medmatch-tour-completed") === "true"
      || localStorage.getItem("medmatch_tour_completed") === "true"
      || localStorage.getItem("medmatch_tour_skipped") === "true";
    if (!done) { const t = setTimeout(() => setShowTour(true), 1000); return () => clearTimeout(t); }
  }, []);
  const completeTour = () => { localStorage.setItem("medmatch-tour-completed", "true"); localStorage.setItem("medmatch_tour_completed", "true"); setShowTour(false); };
  const resetTour = () => { localStorage.removeItem("medmatch-tour-completed"); localStorage.removeItem("medmatch_tour_completed"); localStorage.removeItem("medmatch_tour_skipped"); setShowTour(true); };
  return { showTour, completeTour, resetTour };
};

export const WelcomeTooltip = ({ feature, children, position = "bottom" }) => {
  const [dismissed, setDismissed] = useState(false);
  const storageKey = `medmatch-tooltip-${feature}`;
  useEffect(() => { if (localStorage.getItem(storageKey)) setDismissed(true); }, [storageKey]);
  const handleDismiss = () => { localStorage.setItem(storageKey, "true"); setDismissed(true); };
  if (dismissed) return null;
  const posClasses = { top: "bottom-full mb-2", bottom: "top-full mt-2", left: "right-full mr-2", right: "left-full ml-2" };
  return (
    <div className="relative inline-block">
      <div className={`absolute ${posClasses[position]} z-50 w-64`}>
        <div className="bg-slate-900 text-white p-3 rounded-lg shadow-lg text-sm">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2"><Sparkles className="w-4 h-4 text-teal-400 flex-shrink-0" /><span>{children}</span></div>
            <button onClick={handleDismiss} className="text-slate-400 hover:text-white"><X className="w-4 h-4" /></button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingTour;
