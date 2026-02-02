import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { useTranslation } from "@/utils/i18n";
import { 
  Mic, MicOff, Loader2, Sparkles, X, Volume2, Send,
  FileText, Search, Briefcase, PenTool, Target, Calendar,
  Globe, ChevronRight, Zap, Brain, MessageSquare
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent } from "@/components/ui/dialog";

const API = process.env.REACT_APP_BACKEND_URL;

// Dragon AI Action Types - labels are translation keys
const DRAGON_ACTIONS = {
  COVER_LETTER: { icon: PenTool, labelKey: "nav.coverLetter", path: "/cover-letter", color: "#10B981" },
  JOB_SEARCH: { icon: Search, labelKey: "nav.jobSearch", path: "/search", color: "#3B82F6" },
  INTERVIEW_PREP: { icon: MessageSquare, labelKey: "nav.interviewPrep", path: "/interview", color: "#8B5CF6" },
  RESUME: { icon: FileText, labelKey: "nav.myResume", path: "/resume", color: "#F59E0B" },
  PREDICTOR: { icon: Target, labelKey: "nav.successPredictor", path: "/predictor", color: "#EF4444" },
  COMPANIES: { icon: Briefcase, labelKey: "nav.companies", path: "/companies", color: "#06B6D4" },
  SCHEDULE: { icon: Calendar, labelKey: "nav.myInterviews", path: "/interviews", color: "#EC4899" },
  WEB_SEARCH: { icon: Globe, labelKey: "dragon.webSearch", path: null, color: "#6366F1" },
};

const KarauDragonAI = ({ user, isOpen, onClose }) => {
  const navigate = useNavigate();
  const { isDark } = useTheme();
  const { t, detectAndSwitchLanguage, getLanguageInfo } = useTranslation();
  
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [textInput, setTextInput] = useState("");
  const [processing, setProcessing] = useState(false);
  const [response, setResponse] = useState(null);
  const [actionHistory, setActionHistory] = useState([]);
  const [webResults, setWebResults] = useState([]);
  
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const current = event.resultIndex;
        const result = event.results[current];
        setTranscript(result[0].transcript);
        
        if (result.isFinal) {
          handleDragonCommand(result[0].transcript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error === 'not-allowed') {
          toast.error("Microphone access denied. Please enable it in your browser settings.");
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    // Initialize Speech Synthesis
    synthesisRef.current = window.speechSynthesis;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current) {
      setTranscript("");
      setIsListening(true);
      recognitionRef.current.start();
    } else {
      toast.error("Speech recognition not supported in this browser");
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const speak = (text) => {
    if (synthesisRef.current) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      synthesisRef.current.speak(utterance);
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (textInput.trim()) {
      // Detect language from user input and auto-switch if different
      const detectedLang = detectAndSwitchLanguage(textInput, true);
      if (detectedLang) {
        toast.info(t("language.autoDetected") || `Language detected: ${getLanguageInfo(detectedLang).name}`, {
          description: t("language.switchedTo") || "App language has been updated",
          duration: 3000,
        });
      }
      handleDragonCommand(textInput);
      setTextInput("");
    }
  };

  const handleDragonCommand = async (command) => {
    setProcessing(true);
    setResponse(null);
    setWebResults([]);

    try {
      // Determine context based on command keywords
      let context = "general";
      const lowerCommand = command.toLowerCase();
      if (lowerCommand.includes("job") || lowerCommand.includes("search") || lowerCommand.includes("find")) {
        context = "job_search";
      } else if (lowerCommand.includes("resume") || lowerCommand.includes("cv")) {
        context = "resume";
      } else if (lowerCommand.includes("interview") || lowerCommand.includes("question")) {
        context = "interview";
      } else if (lowerCommand.includes("career") || lowerCommand.includes("advice")) {
        context = "career";
      }
      
      // Use the new AI assistant endpoint
      const result = await axios.post(`${API}/api/assistant`, {
        message: command,
        context: context
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      const aiResponse = {
        text: result.data.response,
        speech: result.data.response.substring(0, 200), // Limit speech length
        context: result.data.context,
        assistant: result.data.assistant
      };
      
      setResponse(aiResponse);

      // Add to history
      setActionHistory(prev => [{
        command,
        response: aiResponse,
        timestamp: new Date().toISOString()
      }, ...prev.slice(0, 9)]);

      // Speak the response (first part only)
      if (aiResponse.speech) {
        speak(aiResponse.speech);
      }

    } catch (error) {
      console.error("Dragon AI error:", error);
      
      // Fallback response
      const fallbackResponse = {
        text: "I'm here to help with your job search! You can ask me about interview tips, resume advice, job searching strategies, or career guidance. What would you like to know?",
        speech: "I'm here to help with your job search!"
      };
      setResponse(fallbackResponse);
      speak(fallbackResponse.speech);
    }

    setProcessing(false);
  };

  const detectLocalIntent = (command) => {
    const cmd = command.toLowerCase();
    
    // Cover letter intents
    if (cmd.includes("cover letter") || cmd.includes("write a letter")) {
      const companyMatch = cmd.match(/for\s+(\w+(?:\s+\w+)?)/i);
      const roleMatch = cmd.match(/(supplier quality|quality engineer|engineer|manager|developer)/i);
      
      return {
        intent: "cover_letter",
        action: DRAGON_ACTIONS.COVER_LETTER,
        speech: `I'll help you create a cover letter${roleMatch ? ` for ${roleMatch[1]}` : ''}${companyMatch ? ` at ${companyMatch[1]}` : ''}. Taking you to the cover letter generator.`,
        params: {
          company: companyMatch?.[1] || "",
          role: roleMatch?.[1] || ""
        }
      };
    }
    
    // Job search intents
    if (cmd.includes("find job") || cmd.includes("search job") || cmd.includes("look for") || cmd.includes("job search")) {
      const roleMatch = cmd.match(/(supplier quality|quality engineer|engineer|developer|manager|analyst)/i);
      
      return {
        intent: "job_search",
        action: DRAGON_ACTIONS.JOB_SEARCH,
        speech: `Searching for ${roleMatch?.[1] || 'jobs'} matching your profile. Let me find the best opportunities.`,
        params: { query: roleMatch?.[1] || "" }
      };
    }
    
    // Interview prep intents
    if (cmd.includes("interview") && (cmd.includes("prep") || cmd.includes("practice") || cmd.includes("prepare"))) {
      return {
        intent: "interview_prep",
        action: DRAGON_ACTIONS.INTERVIEW_PREP,
        speech: "Let's prepare you for your interview. I'll generate relevant questions based on your target role.",
        params: {}
      };
    }
    
    // Success prediction
    if (cmd.includes("predict") || cmd.includes("chance") || cmd.includes("probability")) {
      return {
        intent: "prediction",
        action: DRAGON_ACTIONS.PREDICTOR,
        speech: "I'll analyze your profile against the job requirements to predict your success rate.",
        params: {}
      };
    }
    
    // Resume
    if (cmd.includes("resume") || cmd.includes("cv") || cmd.includes("profile")) {
      return {
        intent: "resume",
        action: DRAGON_ACTIONS.RESUME,
        speech: "Taking you to your resume. You can upload, view, or edit your professional profile.",
        params: {}
      };
    }
    
    // Company research
    if (cmd.includes("company") || cmd.includes("companies") || cmd.includes("research")) {
      const companyMatch = cmd.match(/about\s+(\w+(?:\s+\w+)?)/i);
      
      return {
        intent: "companies",
        action: DRAGON_ACTIONS.COMPANIES,
        speech: companyMatch 
          ? `Let me find information about ${companyMatch[1]}.`
          : "Opening the companies directory for you to explore.",
        params: { company: companyMatch?.[1] || "" }
      };
    }
    
    // Web search fallback
    if (cmd.includes("search") || cmd.includes("find") || cmd.includes("what is") || cmd.includes("who is")) {
      return {
        intent: "web_search",
        action: DRAGON_ACTIONS.WEB_SEARCH,
        speech: "Let me search the web for that information.",
        params: { query: command },
        requires_web: true
      };
    }
    
    // Default
    return {
      intent: "unknown",
      speech: "I can help you with cover letters, job searches, interview prep, resume management, and company research. What would you like to do?",
      suggestions: [
        "Generate a cover letter for [Company]",
        "Find quality engineer jobs",
        "Prepare for my interview",
        "Show my resume"
      ]
    };
  };

  const executeAction = async (aiResponse) => {
    const { action, params, requires_web } = aiResponse;
    
    if (!action) return;

    // Handle web search
    if (requires_web && params?.query) {
      try {
        const webResponse = await axios.post(`${API}/api/dragon/web-search`, {
          query: params.query
        });
        setWebResults(webResponse.data.results || []);
      } catch (e) {
        console.error("Web search failed:", e);
      }
      return;
    }

    // Navigate to the appropriate page
    if (action.path) {
      setTimeout(() => {
        // Build URL with params if needed
        let url = action.path;
        if (params) {
          const searchParams = new URLSearchParams();
          Object.entries(params).forEach(([key, value]) => {
            if (value) searchParams.set(key, value);
          });
          if (searchParams.toString()) {
            url += `?${searchParams.toString()}`;
          }
        }
        
        navigate(url);
        onClose();
      }, 1500);
    }
  };

  const quickActions = [
    { label: "Write cover letter", icon: PenTool, cmd: "Help me write a cover letter" },
    { label: "Find jobs", icon: Search, cmd: "Find quality engineer jobs" },
    { label: "Interview prep", icon: MessageSquare, cmd: "Prepare me for an interview" },
    { label: "My resume", icon: FileText, cmd: "Show my resume" },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`max-w-2xl p-0 overflow-hidden ${isDark ? 'bg-slate-900 border-slate-700' : 'bg-white'}`}>
        {/* Dragon Header */}
        <div className="relative bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 p-6 text-white">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,...')] opacity-10"></div>
          
          <div className="relative flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2">
                KARAU DRAGON AI
                <Sparkles className="w-5 h-5 text-yellow-300" />
              </h2>
              <p className="text-white/80 text-sm">Your AI-powered job search assistant</p>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="absolute top-4 right-4 p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Main Content */}
        <div className="p-6 space-y-6">
          {/* Voice Input Area */}
          <div className="flex flex-col items-center gap-4">
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={processing}
              className={`
                w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300
                ${isListening 
                  ? 'bg-red-500 animate-pulse shadow-lg shadow-red-500/50' 
                  : 'bg-gradient-to-r from-purple-500 to-indigo-500 hover:shadow-lg hover:shadow-purple-500/30'
                }
                ${processing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              {processing ? (
                <Loader2 className="w-10 h-10 text-white animate-spin" />
              ) : isListening ? (
                <MicOff className="w-10 h-10 text-white" />
              ) : (
                <Mic className="w-10 h-10 text-white" />
              )}
            </button>
            
            <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              {isListening ? "Listening... Click to stop" : "Click to speak or type below"}
            </p>

            {/* Transcript Display */}
            {transcript && (
              <div className={`w-full p-3 rounded-lg ${isDark ? 'bg-slate-800' : 'bg-slate-100'}`}>
                <p className="text-center italic">"{transcript}"</p>
              </div>
            )}
          </div>

          {/* Text Input */}
          <form onSubmit={handleTextSubmit} className="flex gap-2">
            <Input
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Or type your request..."
              className="flex-1"
              disabled={processing}
            />
            <Button type="submit" disabled={processing || !textInput.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </form>

          {/* Response Area */}
          {response && (
            <Card className={`${isDark ? 'bg-slate-800 border-slate-700' : 'bg-slate-50'}`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  {response.action && (
                    <div 
                      className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: response.action.color + '20' }}
                    >
                      {response.action.icon && <response.action.icon className="w-5 h-5" style={{ color: response.action.color }} />}
                    </div>
                  )}
                  <div className="flex-1">
                    <p className={`${isDark ? 'text-slate-200' : 'text-slate-700'}`}>
                      {response.speech}
                    </p>
                    
                    {response.action?.path && (
                      <div className="flex items-center gap-1 mt-2 text-sm text-purple-500">
                        <ChevronRight className="w-4 h-4" />
                        Navigating to {response.action.label}...
                      </div>
                    )}

                    {response.suggestions && (
                      <div className="mt-3 space-y-2">
                        <p className="text-sm text-slate-500">Try saying:</p>
                        <div className="flex flex-wrap gap-2">
                          {response.suggestions.map((s, i) => (
                            <button
                              key={i}
                              onClick={() => handleDragonCommand(s)}
                              className="text-xs px-3 py-1.5 rounded-full bg-purple-100 text-purple-700 hover:bg-purple-200 transition-colors"
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Web Results */}
          {webResults.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-medium flex items-center gap-2">
                <Globe className="w-4 h-4 text-indigo-500" />
                Web Results
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {webResults.map((result, i) => (
                  <a
                    key={i}
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`block p-3 rounded-lg transition-colors ${
                      isDark ? 'bg-slate-800 hover:bg-slate-700' : 'bg-slate-50 hover:bg-slate-100'
                    }`}
                  >
                    <p className="font-medium text-sm text-purple-600">{result.title}</p>
                    <p className="text-xs text-slate-500 truncate">{result.snippet}</p>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          {!response && (
            <div className="space-y-3">
              <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                Quick actions:
              </p>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => handleDragonCommand(action.cmd)}
                    disabled={processing}
                    className={`
                      flex items-center gap-3 p-3 rounded-lg text-left transition-all
                      ${isDark 
                        ? 'bg-slate-800 hover:bg-slate-700 text-slate-200' 
                        : 'bg-slate-50 hover:bg-slate-100 text-slate-700'
                      }
                      ${processing ? 'opacity-50' : ''}
                    `}
                  >
                    <action.icon className="w-5 h-5 text-purple-500" />
                    <span className="text-sm font-medium">{action.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className={`px-6 py-3 border-t ${isDark ? 'border-slate-700 bg-slate-800/50' : 'border-slate-100 bg-slate-50'}`}>
          <p className="text-xs text-center text-slate-500">
            Powered by AI • Speak naturally or type your request
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Floating Dragon Button Component
export const DragonButton = ({ onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        fixed bottom-6 right-6 z-50
        w-16 h-16 rounded-full
        bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600
        shadow-lg shadow-purple-500/30
        flex items-center justify-center
        transition-all duration-300
        hover:scale-110 hover:shadow-xl hover:shadow-purple-500/40
        ${isHovered ? 'animate-none' : 'animate-pulse'}
      `}
      data-testid="dragon-ai-button"
      title="KARAU DRAGON AI"
    >
      <div className="relative">
        <Brain className="w-8 h-8 text-white" />
        <Sparkles className="w-4 h-4 text-yellow-300 absolute -top-1 -right-1" />
      </div>
      
      {isHovered && (
        <div className="absolute bottom-full right-0 mb-2 px-3 py-1.5 bg-slate-900 text-white text-sm rounded-lg whitespace-nowrap">
          KARAU DRAGON AI
        </div>
      )}
    </button>
  );
};

export default KarauDragonAI;
