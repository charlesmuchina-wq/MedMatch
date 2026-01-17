import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Mic, MicOff, Play, Pause, Square, Send, Sparkles, Loader2,
  MessageSquare, Target, Users, Lightbulb, Building2, CheckCircle2,
  AlertCircle, RefreshCw, Copy, ChevronRight, Star, Award, TrendingUp,
  FileText, Volume2, Trash2, History, Plus, ArrowRight, Upload, Download, FileAudio
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import TranslationWidget from "@/components/TranslationWidget";
import jsPDF from "jspdf";
import "jspdf-autotable";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Supported audio formats
const SUPPORTED_AUDIO_FORMATS = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'];

// Question type options
const QUESTION_TYPES = [
  { id: "behavioral", name: "Behavioral", icon: Users, color: "text-violet-500 bg-violet-50" },
  { id: "technical", name: "Technical", icon: Target, color: "text-sky-500 bg-sky-50" },
  { id: "situational", name: "Situational", icon: Lightbulb, color: "text-amber-500 bg-amber-50" },
  { id: "company-fit", name: "Company Fit", icon: Building2, color: "text-emerald-500 bg-emerald-50" },
];

// Voice Recording Component
const VoiceRecorder = ({ onTranscript, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [duration, setDuration] = useState(0);
  const [transcript, setTranscript] = useState("");
  const mediaRecorderRef = useRef(null);
  const recognitionRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    // Check for speech recognition support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + ' ';
          }
        }
        if (finalTranscript) {
          setTranscript(prev => prev + finalTranscript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error !== 'no-speech') {
          toast.error("Speech recognition error. Please try again.");
        }
      };
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, []);

  const startRecording = async () => {
    try {
      setTranscript("");
      setDuration(0);
      setIsRecording(true);
      
      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }
      
      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(d => d + 1);
      }, 1000);
      
    } catch (error) {
      console.error("Recording error:", error);
      toast.error("Could not start recording. Check microphone permissions.");
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    setIsPaused(false);
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    // Send transcript to parent
    if (transcript.trim()) {
      onTranscript(transcript.trim());
    }
  };

  const pauseRecording = () => {
    setIsPaused(!isPaused);
    if (recognitionRef.current) {
      if (isPaused) {
        recognitionRef.current.start();
      } else {
        recognitionRef.current.stop();
      }
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        {!isRecording ? (
          <Button 
            onClick={startRecording} 
            disabled={disabled}
            className="bg-red-500 hover:bg-red-600"
            data-testid="start-recording-btn"
          >
            <Mic className="w-4 h-4 mr-2" />
            Start Recording
          </Button>
        ) : (
          <>
            <Button 
              onClick={pauseRecording}
              variant="outline"
              className="border-amber-500 text-amber-600"
            >
              {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            </Button>
            <Button 
              onClick={stopRecording}
              variant="destructive"
              data-testid="stop-recording-btn"
            >
              <Square className="w-4 h-4 mr-2" />
              Stop
            </Button>
            <div className="flex items-center gap-2 px-3 py-1 bg-red-50 dark:bg-red-900/20 rounded-full">
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-red-600 dark:text-red-400">
                {formatTime(duration)}
              </span>
            </div>
          </>
        )}
      </div>
      
      {transcript && (
        <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
          <p className="text-xs text-slate-500 mb-1">Live Transcript:</p>
          <p className="text-sm text-slate-700 dark:text-slate-300">{transcript}</p>
        </div>
      )}
    </div>
  );
};

// Audio File Upload Component
const AudioFileUpload = ({ onTranscript, disabled }) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!SUPPORTED_AUDIO_FORMATS.includes(ext)) {
      toast.error(`Unsupported format. Use: ${SUPPORTED_AUDIO_FORMATS.join(', ')}`);
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      toast.error("File too large. Maximum 25MB.");
      return;
    }

    setUploading(true);
    setProgress(10);

    const formData = new FormData();
    formData.append('file', file);

    try {
      setProgress(30);
      const response = await axios.post(`${API}/qa-practice/transcribe-audio`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => setProgress(30 + (e.loaded / e.total) * 40)
      });
      setProgress(90);
      
      if (response.data.transcript) {
        onTranscript(response.data.transcript);
        toast.success("Audio transcribed successfully!");
      }
      setProgress(100);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Transcription failed");
    } finally {
      setUploading(false);
      setProgress(0);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-2">
      <input
        ref={fileInputRef}
        type="file"
        accept={SUPPORTED_AUDIO_FORMATS.join(',')}
        onChange={handleFileUpload}
        className="hidden"
        disabled={disabled || uploading}
      />
      <Button
        variant="outline"
        onClick={() => fileInputRef.current?.click()}
        disabled={disabled || uploading}
        className="w-full border-dashed"
        data-testid="upload-audio-btn"
      >
        {uploading ? (
          <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Transcribing {progress}%</>
        ) : (
          <><FileAudio className="w-4 h-4 mr-2" />Upload Audio File</>
        )}
      </Button>
      {uploading && <Progress value={progress} className="h-1" />}
      <p className="text-xs text-slate-400 text-center">MP3, WAV, M4A, WEBM (max 25MB)</p>
    </div>
  );
};

// PDF Export Function
const exportToPDF = (data) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  let y = 20;

  // Header
  doc.setFontSize(20);
  doc.setTextColor(0, 166, 153); // Turquoise
  doc.text("MedMatch Q&A Practice Session", pageWidth / 2, y, { align: "center" });
  y += 10;

  doc.setFontSize(10);
  doc.setTextColor(100);
  doc.text(`Generated: ${new Date().toLocaleString()}`, pageWidth / 2, y, { align: "center" });
  y += 15;

  // Job Context
  if (data.jobContext?.job_title) {
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("Job Context", 14, y);
    y += 8;
    doc.setFontSize(10);
    doc.setTextColor(60);
    if (data.jobContext.company_name) doc.text(`Company: ${data.jobContext.company_name}`, 14, y); y += 5;
    doc.text(`Position: ${data.jobContext.job_title}`, 14, y); y += 10;
  }

  // Match Analysis
  if (data.matchAnalysis) {
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("Resume Match Analysis", 14, y);
    y += 8;
    doc.setFontSize(12);
    doc.setTextColor(0, 166, 153);
    doc.text(`Match Score: ${data.matchAnalysis.match_score || 0}%`, 14, y);
    y += 10;
  }

  // Question & Answer
  doc.setFontSize(14);
  doc.setTextColor(0);
  doc.text("Interview Question", 14, y);
  y += 8;
  doc.setFontSize(10);
  doc.setTextColor(60);
  const questionLines = doc.splitTextToSize(data.question || "N/A", pageWidth - 28);
  doc.text(questionLines, 14, y);
  y += questionLines.length * 5 + 10;

  // AI Answer
  if (data.aiAnswer?.suggested_answer) {
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("AI-Generated Answer", 14, y);
    y += 8;
    doc.setFontSize(10);
    doc.setTextColor(60);
    const answerLines = doc.splitTextToSize(data.aiAnswer.suggested_answer, pageWidth - 28);
    
    // Check for page break
    if (y + answerLines.length * 5 > doc.internal.pageSize.getHeight() - 20) {
      doc.addPage();
      y = 20;
    }
    doc.text(answerLines, 14, y);
    y += answerLines.length * 5 + 10;

    // Key Points
    if (data.aiAnswer.key_points?.length > 0) {
      if (y > doc.internal.pageSize.getHeight() - 40) { doc.addPage(); y = 20; }
      doc.setFontSize(12);
      doc.setTextColor(0);
      doc.text("Key Points:", 14, y);
      y += 6;
      doc.setFontSize(10);
      doc.setTextColor(60);
      data.aiAnswer.key_points.forEach(point => {
        const lines = doc.splitTextToSize(`• ${point}`, pageWidth - 32);
        if (y + lines.length * 5 > doc.internal.pageSize.getHeight() - 20) { doc.addPage(); y = 20; }
        doc.text(lines, 18, y);
        y += lines.length * 5 + 2;
      });
      y += 5;
    }
  }

  // User Feedback
  if (data.feedback) {
    if (y > doc.internal.pageSize.getHeight() - 60) { doc.addPage(); y = 20; }
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text(`Your Answer Feedback - Score: ${data.feedback.overall_score}/10`, 14, y);
    y += 10;
    
    if (data.feedback.strengths?.length > 0) {
      doc.setFontSize(10);
      doc.setTextColor(0, 128, 0);
      doc.text("Strengths:", 14, y); y += 5;
      data.feedback.strengths.forEach(s => {
        doc.text(`✓ ${s}`, 18, y); y += 5;
      });
      y += 5;
    }
  }

  // Footer
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(150);
    doc.text(`Page ${i} of ${pageCount} | MedMatch Q&A Practice`, pageWidth / 2, doc.internal.pageSize.getHeight() - 10, { align: "center" });
  }

  doc.save(`medmatch-qa-${Date.now()}.pdf`);
  toast.success("PDF exported successfully!");
};

// Match Analysis Display
const MatchAnalysis = ({ analysis }) => {
  if (!analysis) return null;

  return (
    <Card className="bg-gradient-to-br from-turquoise/5 to-emerald-50 dark:from-turquoise/10 dark:to-emerald-900/20 border-turquoise/20">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Target className="w-5 h-5 text-turquoise" />
          Resume-Job Match Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Match Score */}
        <div className="flex items-center gap-4">
          <div className="text-3xl font-bold text-turquoise">{analysis.match_score || 0}%</div>
          <Progress value={analysis.match_score || 0} className="flex-1 h-3" />
        </div>

        {/* Direct Matches */}
        {analysis.direct_matches?.length > 0 && (
          <div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              <CheckCircle2 className="w-4 h-4 inline mr-1 text-emerald-500" />
              Direct Skill Matches
            </p>
            <div className="flex flex-wrap gap-2">
              {analysis.direct_matches.map((skill, i) => (
                <Badge key={i} className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Transferable Skills */}
        {analysis.transferable_skills?.length > 0 && (
          <div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              <TrendingUp className="w-4 h-4 inline mr-1 text-sky-500" />
              Transferable Skills
            </p>
            <div className="space-y-1">
              {analysis.transferable_skills.slice(0, 5).map((item, i) => (
                <div key={i} className="text-sm text-slate-600 dark:text-slate-400">
                  <span className="font-medium">{typeof item === 'string' ? item : item.skill}</span>
                  {item.relevance && <span className="text-slate-400"> - {item.relevance}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Gaps */}
        {analysis.gaps?.length > 0 && (
          <div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              <AlertCircle className="w-4 h-4 inline mr-1 text-amber-500" />
              Areas to Address
            </p>
            <div className="flex flex-wrap gap-2">
              {analysis.gaps.slice(0, 5).map((gap, i) => (
                <Badge key={i} variant="outline" className="border-amber-300 text-amber-700 dark:border-amber-600 dark:text-amber-300">
                  {gap}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Answer Feedback Display
const AnswerFeedback = ({ feedback }) => {
  if (!feedback) return null;

  const getScoreColor = (score) => {
    if (score >= 8) return "text-emerald-500";
    if (score >= 6) return "text-amber-500";
    return "text-red-500";
  };

  return (
    <Card className="border-violet-200 dark:border-violet-800">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Star className="w-5 h-5 text-violet-500" />
            Your Answer Feedback
          </span>
          <span className={`text-2xl font-bold ${getScoreColor(feedback.overall_score)}`}>
            {feedback.overall_score}/10
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Strengths */}
        {feedback.strengths?.length > 0 && (
          <div>
            <p className="text-sm font-medium text-emerald-600 mb-2">✓ What You Did Well</p>
            <ul className="space-y-1">
              {feedback.strengths.map((s, i) => (
                <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Improvements */}
        {feedback.areas_for_improvement?.length > 0 && (
          <div>
            <p className="text-sm font-medium text-amber-600 mb-2">→ Areas to Improve</p>
            <ul className="space-y-1">
              {feedback.areas_for_improvement.map((s, i) => (
                <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                  <ArrowRight className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                  {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Revised Answer */}
        {feedback.revised_answer && (
          <div className="p-3 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
            <p className="text-sm font-medium text-violet-700 dark:text-violet-300 mb-2">
              ✨ Suggested Improved Answer
            </p>
            <p className="text-sm text-slate-700 dark:text-slate-300">{feedback.revised_answer}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Main Q&A Practice Page
const QAPracticePage = ({ resume }) => {
  const [activeTab, setActiveTab] = useState("practice");
  
  // Job context
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  
  // Question input
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [questionType, setQuestionType] = useState("behavioral");
  const [userAnswer, setUserAnswer] = useState("");
  
  // Results
  const [matchAnalysis, setMatchAnalysis] = useState(null);
  const [aiAnswer, setAiAnswer] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [commonQuestions, setCommonQuestions] = useState(null);
  const [history, setHistory] = useState([]);
  
  // Loading states
  const [analyzing, setAnalyzing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(false);

  // Analyze job match
  const analyzeMatch = async () => {
    if (!jobTitle) {
      toast.error("Please enter a job title");
      return;
    }

    setAnalyzing(true);
    try {
      const response = await axios.post(`${API}/qa-practice/analyze-match`, {
        company_name: companyName,
        job_title: jobTitle,
        job_description: jobDescription
      });
      setMatchAnalysis(response.data.match_analysis);
      toast.success("Job match analyzed!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to analyze match");
    }
    setAnalyzing(false);
  };

  // Generate AI answer
  const generateAnswer = async () => {
    if (!currentQuestion.trim()) {
      toast.error("Please enter a question");
      return;
    }

    setGenerating(true);
    setAiAnswer(null);
    setFeedback(null);
    
    try {
      const response = await axios.post(`${API}/qa-practice/generate-answer`, {
        question: currentQuestion,
        question_type: questionType,
        job_context: {
          company_name: companyName,
          job_title: jobTitle,
          job_description: jobDescription
        },
        user_answer: userAnswer || null
      });
      
      setAiAnswer(response.data.ai_answer);
      setFeedback(response.data.user_feedback);
      if (response.data.match_analysis && !matchAnalysis) {
        setMatchAnalysis(response.data.match_analysis);
      }
      toast.success("Answer generated!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to generate answer");
    }
    setGenerating(false);
  };

  // Handle voice transcript
  const handleVoiceTranscript = async (transcript) => {
    setUserAnswer(transcript);
    toast.success("Recording captured! Click 'Get AI Feedback' to analyze.");
  };

  // Get common questions
  const fetchCommonQuestions = async () => {
    if (!jobTitle) {
      toast.error("Please enter a job title first");
      return;
    }

    setLoadingQuestions(true);
    try {
      const response = await axios.post(`${API}/qa-practice/common-questions`, {
        company_name: companyName,
        job_title: jobTitle,
        job_description: jobDescription
      });
      setCommonQuestions(response.data.questions);
    } catch (error) {
      toast.error("Failed to generate questions");
    }
    setLoadingQuestions(false);
  };

  // Load history
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${API}/qa-practice/history?limit=10`);
        setHistory([...response.data.text_answers, ...response.data.voice_recordings]);
      } catch (error) {
        console.error("Failed to load history:", error);
      }
    };
    fetchHistory();
  }, [aiAnswer]);

  // Copy answer to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white" style={{ fontFamily: 'IBM Plex Sans' }}>
            Q&A Interview Practice
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Practice interview questions with AI-driven feedback tailored to your resume
          </p>
        </div>
        <Badge className="bg-turquoise/20 text-turquoise border-turquoise/30">
          <Sparkles className="w-3 h-3 mr-1" />
          AI Powered
        </Badge>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid grid-cols-3 w-full max-w-md">
          <TabsTrigger value="practice" data-testid="tab-practice">
            <MessageSquare className="w-4 h-4 mr-2" />
            Practice
          </TabsTrigger>
          <TabsTrigger value="questions" data-testid="tab-questions">
            <FileText className="w-4 h-4 mr-2" />
            Questions
          </TabsTrigger>
          <TabsTrigger value="history" data-testid="tab-history">
            <History className="w-4 h-4 mr-2" />
            History
          </TabsTrigger>
        </TabsList>

        {/* Practice Tab */}
        <TabsContent value="practice" className="space-y-6">
          {/* Job Context Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-turquoise" />
                Job Context
              </CardTitle>
              <CardDescription>
                Enter job details for personalized answers based on your resume
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Company Name</label>
                  <Input 
                    placeholder="e.g., Google, Amazon, Medtronic"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="mt-1"
                    data-testid="company-input"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Job Title *</label>
                  <Input 
                    placeholder="e.g., Senior Quality Engineer"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    className="mt-1"
                    data-testid="job-title-input"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Job Description</label>
                <Textarea 
                  placeholder="Paste the job description here for more accurate answers..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="mt-1 min-h-[100px]"
                  data-testid="job-description-input"
                />
              </div>
              <Button 
                onClick={analyzeMatch} 
                disabled={analyzing || !jobTitle}
                className="bg-turquoise hover:bg-turquoise/90"
                data-testid="analyze-match-btn"
              >
                {analyzing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Target className="w-4 h-4 mr-2" />}
                Analyze Resume Match
              </Button>
            </CardContent>
          </Card>

          {/* Match Analysis */}
          {matchAnalysis && <MatchAnalysis analysis={matchAnalysis} />}

          {/* Question Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-violet-500" />
                Your Interview Question
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Question Type Selector */}
              <div className="flex flex-wrap gap-2">
                {QUESTION_TYPES.map((type) => {
                  const Icon = type.icon;
                  return (
                    <button
                      key={type.id}
                      onClick={() => setQuestionType(type.id)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        questionType === type.id 
                          ? `${type.color} ring-2 ring-offset-2 ring-current` 
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {type.name}
                    </button>
                  );
                })}
              </div>

              {/* Question Input */}
              <div>
                <Textarea 
                  placeholder="Enter an interview question (e.g., 'Tell me about a time when you had to deal with a difficult situation at work')"
                  value={currentQuestion}
                  onChange={(e) => setCurrentQuestion(e.target.value)}
                  className="min-h-[80px]"
                  data-testid="question-input"
                />
              </div>

              {/* Your Answer Section */}
              <div className="border-t pt-4 space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    Your Answer (Optional - for feedback)
                  </label>
                  <Badge variant="outline" className="text-xs">
                    Type or record your answer
                  </Badge>
                </div>
                
                {/* Voice Recorder */}
                <VoiceRecorder 
                  onTranscript={handleVoiceTranscript} 
                  disabled={generating}
                />
                
                {/* Audio File Upload */}
                <AudioFileUpload 
                  onTranscript={handleVoiceTranscript}
                  disabled={generating}
                />
                
                {/* Text Answer */}
                <Textarea 
                  placeholder="Type your answer here, or use voice recording above..."
                  value={userAnswer}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  className="min-h-[120px]"
                  data-testid="user-answer-input"
                />
              </div>

              {/* Generate Button */}
              <div className="flex gap-3">
                <Button 
                  onClick={generateAnswer}
                  disabled={generating || !currentQuestion.trim()}
                  className="flex-1 bg-violet-600 hover:bg-violet-700"
                  data-testid="generate-answer-btn"
                >
                  {generating ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4 mr-2" />
                  )}
                  {userAnswer ? "Get AI Feedback" : "Generate AI Answer"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* AI Generated Answer */}
          {aiAnswer && (
            <Card className="border-turquoise/30">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-turquoise" />
                    AI-Generated Answer
                  </span>
                  <div className="flex gap-2">
                    <TranslationWidget 
                      text={aiAnswer.suggested_answer} 
                      compact={true}
                      context="interview_answer"
                    />
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => copyToClipboard(aiAnswer.suggested_answer)}
                      title="Copy"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => exportToPDF({
                        question: currentQuestion,
                        aiAnswer,
                        feedback,
                        matchAnalysis,
                        jobContext: { company_name: companyName, job_title: jobTitle }
                      })}
                      title="Export PDF"
                      data-testid="export-pdf-btn"
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Main Answer */}
                <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                    {aiAnswer.suggested_answer}
                  </p>
                </div>

                {/* Key Points */}
                {aiAnswer.key_points?.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Key Points to Hit</p>
                    <ul className="space-y-1">
                      {aiAnswer.key_points.map((point, i) => (
                        <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                          <CheckCircle2 className="w-4 h-4 text-turquoise mt-0.5 shrink-0" />
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Skills Demonstrated */}
                {aiAnswer.skills_demonstrated?.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    <span className="text-sm text-slate-500">Skills shown:</span>
                    {aiAnswer.skills_demonstrated.map((skill, i) => (
                      <Badge key={i} className="bg-turquoise/20 text-turquoise">{skill}</Badge>
                    ))}
                  </div>
                )}

                {/* What to Avoid */}
                {aiAnswer.what_to_avoid?.length > 0 && (
                  <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                    <p className="text-sm font-medium text-amber-700 dark:text-amber-300 mb-1">⚠️ Avoid</p>
                    <ul className="text-sm text-amber-600 dark:text-amber-400 space-y-1">
                      {aiAnswer.what_to_avoid.map((item, i) => (
                        <li key={i}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* User Answer Feedback */}
          {feedback && <AnswerFeedback feedback={feedback} />}
        </TabsContent>

        {/* Common Questions Tab */}
        <TabsContent value="questions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Common Interview Questions</CardTitle>
              <CardDescription>
                Generate tailored questions based on the job role
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-3">
                <Input 
                  placeholder="Job Title (e.g., Quality Engineer)"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={fetchCommonQuestions}
                  disabled={loadingQuestions || !jobTitle}
                  className="bg-turquoise hover:bg-turquoise/90"
                >
                  {loadingQuestions ? <Loader2 className="w-4 h-4 animate-spin" /> : "Generate Questions"}
                </Button>
              </div>

              {commonQuestions && (
                <div className="space-y-6 pt-4">
                  {Object.entries(commonQuestions).map(([category, questions]) => (
                    <div key={category}>
                      <h3 className="font-medium text-slate-800 dark:text-slate-200 mb-3 capitalize">
                        {category.replace(/_/g, ' ')}
                      </h3>
                      <div className="space-y-2">
                        {questions?.map((q, i) => (
                          <button
                            key={i}
                            onClick={() => {
                              setCurrentQuestion(q);
                              setActiveTab("practice");
                            }}
                            className="w-full text-left p-3 bg-slate-50 dark:bg-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                          >
                            <span className="text-sm text-slate-700 dark:text-slate-300">{q}</span>
                            <ChevronRight className="w-4 h-4 text-slate-400 float-right mt-0.5" />
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5" />
                Practice History
              </CardTitle>
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <p className="text-center text-slate-500 py-8">
                  No practice sessions yet. Start practicing above!
                </p>
              ) : (
                <div className="space-y-3">
                  {history.slice(0, 10).map((item, i) => (
                    <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <p className="font-medium text-slate-800 dark:text-slate-200 text-sm">
                          {item.question}
                        </p>
                        <Badge variant="outline" className="text-xs shrink-0 ml-2">
                          {item.type === "voice_recording" ? "Voice" : "Text"}
                        </Badge>
                      </div>
                      {item.job_context?.job_title && (
                        <p className="text-xs text-slate-500 mb-2">
                          For: {item.job_context.job_title} {item.job_context.company_name && `at ${item.job_context.company_name}`}
                        </p>
                      )}
                      <p className="text-xs text-slate-400">
                        {new Date(item.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QAPracticePage;
