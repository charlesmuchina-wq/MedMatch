import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Video, VideoOff, Mic, MicOff, Play, Pause, RotateCcw, 
  Sparkles, Loader2, Camera, Clock, CheckCircle2, AlertCircle,
  TrendingUp, Eye, User, Zap, Target, Award, RefreshCw, 
  ChevronRight, Download, Trash2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Circular Score Component
const CircularScore = ({ score, label, color }) => {
  const radius = 35;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-20 h-20">
        <svg className="transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50" cy="50" r={radius}
            fill="none" stroke="currentColor"
            className="text-slate-200 dark:text-slate-700"
            strokeWidth="8"
          />
          <circle
            cx="50" cy="50" r={radius}
            fill="none" stroke={color}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold" style={{ color }}>{score}</span>
        </div>
      </div>
      <span className="text-xs text-slate-500 dark:text-slate-400 mt-1 text-center">{label}</span>
    </div>
  );
};

const VideoInterviewPage = ({ resume }) => {
  const { isDark } = useTheme();
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  
  const [isRecording, setIsRecording] = useState(false);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [recordedVideoURL, setRecordedVideoURL] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [videoAnalysis, setVideoAnalysis] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [recordings, setRecordings] = useState([]);
  const [isSessionActive, setIsSessionActive] = useState(false);
  
  const timerRef = useRef(null);

  // Load questions on mount
  useEffect(() => {
    if (resume?.skills?.length > 0) {
      generateQuestions();
    }
    loadRecordings();
  }, [resume]);

  // Timer effect
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRecording]);

  const generateQuestions = async () => {
    try {
      const response = await axios.post(`${API}/interview/generate-questions`, {
        job_title: "Quality Manager",
        company: "",
        resume_skills: resume?.skills || []
      });
      setQuestions(response.data.questions || []);
      if (response.data.questions?.length > 0) {
        setCurrentQuestion(response.data.questions[0]);
      }
    } catch (e) {
      toast.error("Failed to load questions");
    }
  };

  const loadRecordings = async () => {
    try {
      const response = await axios.get(`${API}/interview/video-recordings`);
      setRecordings(response.data || []);
    } catch (e) {
      console.error("Failed to load recordings");
    }
  };

  const startPreview = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720, facingMode: "user" },
        audio: true 
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsPreviewing(true);
    } catch (err) {
      toast.error("Could not access camera. Please allow camera permissions.");
      console.error("Camera error:", err);
    }
  };

  const stopPreview = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsPreviewing(false);
  };

  const startRecording = () => {
    if (!streamRef.current) return;
    
    chunksRef.current = [];
    const mediaRecorder = new MediaRecorder(streamRef.current, {
      mimeType: 'video/webm;codecs=vp9'
    });
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };
    
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      setRecordedVideoURL(url);
    };
    
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);
    setElapsedTime(0);
    setVideoAnalysis(null);
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    
    // Capture frame for analysis
    if (videoRef.current && elapsedTime >= 3) {
      await analyzeVideoFrame();
    }
  };

  const analyzeVideoFrame = async () => {
    if (!videoRef.current) return;
    
    setIsAnalyzing(true);
    try {
      // Capture current frame as base64
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth || 640;
      canvas.height = videoRef.current.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0);
      const base64 = canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
      
      const response = await axios.post(`${API}/interview/analyze-video-frame`, {
        frame_base64: base64,
        question: currentQuestion?.text || currentQuestion || "",
        context: "behavioral interview"
      });
      
      setVideoAnalysis(response.data);
      toast.success("Video analysis complete!");
    } catch (e) {
      toast.error("Failed to analyze video");
      console.error(e);
    }
    setIsAnalyzing(false);
  };

  const startSession = () => {
    setIsSessionActive(true);
    setQuestionIndex(0);
    setVideoAnalysis(null);
    setRecordedVideoURL(null);
    if (questions.length > 0) {
      setCurrentQuestion(questions[0]);
    }
    startPreview();
  };

  const nextQuestion = () => {
    const newIndex = questionIndex + 1;
    if (newIndex < questions.length) {
      setQuestionIndex(newIndex);
      setCurrentQuestion(questions[newIndex]);
      setVideoAnalysis(null);
      setRecordedVideoURL(null);
      setElapsedTime(0);
    } else {
      toast.success("Practice session complete!");
      setIsSessionActive(false);
      stopPreview();
    }
  };

  const endSession = () => {
    setIsSessionActive(false);
    stopPreview();
    setVideoAnalysis(null);
    setRecordedVideoURL(null);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const deleteRecording = async (recordingId) => {
    try {
      await axios.delete(`${API}/interview/video-recordings/${recordingId}`);
      setRecordings(prev => prev.filter(r => r.id !== recordingId));
      toast.success("Recording deleted");
    } catch (e) {
      toast.error("Failed to delete recording");
    }
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="video-interview-page">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
          Video Interview Practice
        </h1>
        <p className="text-slate-500 dark:text-slate-400 mt-2">
          Practice on camera with AI-powered body language analysis
        </p>
      </div>

      {!isSessionActive ? (
        /* Start Session Card */
        <Card className="max-w-2xl mx-auto">
          <CardContent className="p-8 text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Video className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-3" style={{ fontFamily: 'IBM Plex Sans' }}>
              Video Interview Practice
            </h2>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              Record yourself answering interview questions and get AI feedback on your body language, eye contact, and overall presentation.
            </p>
            
            <div className="flex flex-wrap justify-center gap-3 mb-8">
              {[
                { icon: Eye, label: "Eye Contact Analysis" },
                { icon: User, label: "Posture Feedback" },
                { icon: Sparkles, label: "Confidence Score" },
                { icon: Target, label: "Improvement Tips" }
              ].map(({ icon: Icon, label }) => (
                <Badge key={label} variant="outline" className="px-3 py-1">
                  <Icon className="w-3 h-3 mr-1" /> {label}
                </Badge>
              ))}
            </div>

            <Button 
              size="lg" 
              onClick={startSession}
              className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
              data-testid="start-video-session"
            >
              <Camera className="w-5 h-5 mr-2" /> Start Practice Session
            </Button>
            
            {questions.length === 0 && (
              <p className="text-sm text-amber-600 mt-4">Loading interview questions...</p>
            )}
          </CardContent>
        </Card>
      ) : (
        /* Active Session */
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Video Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Question Card */}
            <Card className="border-2 border-violet-200 dark:border-violet-800">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <Badge variant="outline">{currentQuestion?.category || 'Question'}</Badge>
                  <Badge className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    {questionIndex + 1} / {questions.length}
                  </Badge>
                </div>
                <CardTitle className="text-lg mt-3" style={{ fontFamily: 'IBM Plex Sans' }}>
                  {currentQuestion?.text || currentQuestion}
                </CardTitle>
              </CardHeader>
            </Card>

            {/* Video Preview */}
            <Card>
              <CardContent className="p-0 relative">
                <div className="aspect-video bg-slate-900 rounded-lg overflow-hidden relative">
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    className="w-full h-full object-cover"
                  />
                  
                  {/* Recording Indicator */}
                  {isRecording && (
                    <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm">
                      <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
                      REC {formatTime(elapsedTime)}
                    </div>
                  )}
                  
                  {/* Analyzing Overlay */}
                  {isAnalyzing && (
                    <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                      <div className="text-center text-white">
                        <Loader2 className="w-12 h-12 animate-spin mx-auto mb-3" />
                        <p>Analyzing your presentation...</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Controls */}
                <div className="p-4 flex items-center justify-center gap-4">
                  {!isRecording ? (
                    <Button
                      size="lg"
                      onClick={startRecording}
                      className="w-16 h-16 rounded-full bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700"
                      disabled={!isPreviewing || isAnalyzing}
                      data-testid="start-recording"
                    >
                      <Video className="w-8 h-8" />
                    </Button>
                  ) : (
                    <Button
                      size="lg"
                      onClick={stopRecording}
                      className="w-16 h-16 rounded-full bg-slate-800 hover:bg-slate-700 animate-pulse"
                      data-testid="stop-recording"
                    >
                      <VideoOff className="w-8 h-8" />
                    </Button>
                  )}
                  
                  {recordedVideoURL && !isRecording && (
                    <Button
                      variant="outline"
                      onClick={analyzeVideoFrame}
                      disabled={isAnalyzing}
                      data-testid="analyze-video"
                    >
                      <Sparkles className="w-4 h-4 mr-2" />
                      {isAnalyzing ? "Analyzing..." : "Analyze Again"}
                    </Button>
                  )}
                </div>

                <p className="text-center text-sm text-slate-500 dark:text-slate-400 pb-4">
                  {isRecording ? "Recording... Click to stop" : "Click to start recording your answer"}
                </p>
              </CardContent>
            </Card>

            {/* Recorded Video Playback */}
            {recordedVideoURL && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Play className="w-5 h-5 text-turquoise" />
                    Your Recording
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <video
                    src={recordedVideoURL}
                    controls
                    className="w-full rounded-lg"
                  />
                </CardContent>
              </Card>
            )}
          </div>

          {/* Analysis Panel */}
          <div className="space-y-6">
            {/* Session Controls */}
            <Card>
              <CardContent className="p-4">
                <div className="flex gap-2">
                  <Button 
                    onClick={nextQuestion} 
                    className="flex-1"
                    disabled={isRecording}
                  >
                    Next Question <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={endSession}
                    disabled={isRecording}
                  >
                    End
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Results */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-violet-500" />
                  AI Body Language Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                {videoAnalysis ? (
                  <div className="space-y-6">
                    {/* Scores */}
                    <div className="grid grid-cols-3 gap-2">
                      <CircularScore 
                        score={videoAnalysis.eye_contact_score} 
                        label="Eye Contact" 
                        color="#20b2aa" 
                      />
                      <CircularScore 
                        score={videoAnalysis.posture_score} 
                        label="Posture" 
                        color="#8b5cf6" 
                      />
                      <CircularScore 
                        score={videoAnalysis.confidence_score} 
                        label="Confidence" 
                        color="#f59e0b" 
                      />
                    </div>

                    {/* Facial Expression */}
                    <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                      <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Facial Expression</p>
                      <p className="font-medium text-slate-900 dark:text-slate-100">
                        {videoAnalysis.facial_expression}
                      </p>
                    </div>

                    {/* Overall Assessment */}
                    <div className="p-3 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
                      <p className="text-sm font-medium text-violet-700 dark:text-violet-300 mb-1">
                        Overall Assessment
                      </p>
                      <p className="text-sm text-violet-600 dark:text-violet-400">
                        {videoAnalysis.overall_assessment}
                      </p>
                    </div>

                    {/* Strengths */}
                    {videoAnalysis.strengths?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-emerald-700 dark:text-emerald-400 mb-2 flex items-center gap-1">
                          <CheckCircle2 className="w-4 h-4" /> Strengths
                        </h4>
                        <ul className="space-y-1">
                          {videoAnalysis.strengths.map((s, i) => (
                            <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                              ✓ {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Improvements */}
                    {videoAnalysis.improvements?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-amber-700 dark:text-amber-400 mb-2 flex items-center gap-1">
                          <Target className="w-4 h-4" /> Areas to Improve
                        </h4>
                        <ul className="space-y-1">
                          {videoAnalysis.improvements.map((s, i) => (
                            <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                              → {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Body Language Tips */}
                    {videoAnalysis.body_language_tips?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-sky-700 dark:text-sky-400 mb-2 flex items-center gap-1">
                          <Zap className="w-4 h-4" /> Quick Tips
                        </h4>
                        <ul className="space-y-1">
                          {videoAnalysis.body_language_tips.slice(0, 3).map((tip, i) => (
                            <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                              💡 {tip}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-400 dark:text-slate-500">
                    <Eye className="w-12 h-12 mx-auto mb-4 opacity-40" />
                    <p>Record a video to receive AI body language analysis</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {/* Previous Recordings */}
      {recordings.length > 0 && !isSessionActive && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
              Previous Practice Sessions
            </CardTitle>
            <CardDescription>Review your past video interview practice</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recordings.slice(0, 5).map((recording) => (
                <div 
                  key={recording.id}
                  className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-900 dark:text-slate-100 text-sm truncate">
                      {recording.question?.slice(0, 60) || 'Practice Recording'}...
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      Duration: {formatTime(recording.duration_seconds || 0)} • 
                      {recording.feedback?.overall_score ? ` Score: ${recording.feedback.overall_score}` : ''}
                      {' • '}{new Date(recording.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteRecording(recording.id)}
                    className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tips Section */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
            Video Interview Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { icon: Eye, title: "Eye Contact", desc: "Look directly at the camera, not at your own image" },
              { icon: User, title: "Good Posture", desc: "Sit up straight with shoulders back" },
              { icon: Camera, title: "Lighting", desc: "Face a light source for clear visibility" },
              { icon: Award, title: "Background", desc: "Keep a clean, professional background" }
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="text-center p-4">
                <Icon className="w-8 h-8 text-turquoise mx-auto mb-2" />
                <h4 className="font-medium text-slate-900 dark:text-slate-100 mb-1">{title}</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">{desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VideoInterviewPage;
