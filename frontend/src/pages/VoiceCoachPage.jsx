import { useState, useEffect, useRef, useCallback, memo } from "react";
import { toast } from "sonner";
import { 
  Mic, MicOff, Play, Pause, RotateCcw, Sparkles, Loader2,
  Volume2, Clock, CheckCircle2, AlertCircle, TrendingUp,
  MessageSquare, Zap, Target, Award, ChevronRight, RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";
import { OptimizedAudioPlayer, AudioSkeleton, PlayButton } from "@/components/OptimizedMedia";

// Speech Recognition Hook
const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        setIsSupported(true);
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event) => {
          let finalTranscript = '';
          let currentInterim = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const currentTranscript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += currentTranscript + ' ';
            } else {
              currentInterim += currentTranscript;
            }
          }
          
          if (finalTranscript) {
            setTranscript(prev => prev + finalTranscript);
          }
          setInterimTranscript(currentInterim);
        };

        recognitionRef.current.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          if (event.error === 'not-allowed') {
            toast.error("Microphone access denied. Please allow microphone access.");
          }
          setIsListening(false);
        };
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListening) {
      setTranscript("");
      setInterimTranscript("");
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error('Failed to start recognition:', e);
      }
    }
  }, [isListening]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      setInterimTranscript("");
    }
  }, [isListening]);

  const resetTranscript = useCallback(() => {
    setTranscript("");
    setInterimTranscript("");
  }, []);

  return {
    isListening,
    transcript,
    interimTranscript,
    isSupported,
    startListening,
    stopListening,
    resetTranscript
  };
};

// Circular Progress Component
const CircularScore = ({ score, label, color }) => {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24">
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
          <span className="text-2xl font-bold" style={{ color }}>{score}</span>
        </div>
      </div>
      <span className="text-sm text-slate-500 dark:text-slate-400 mt-2">{label}</span>
    </div>
  );
};

// Voice Waveform Visualization
const VoiceWaveform = ({ isActive }) => {
  return (
    <div className="flex items-center justify-center gap-1 h-12">
      {[...Array(12)].map((_, i) => (
        <div
          key={i}
          className={`w-1 bg-turquoise rounded-full transition-all duration-150 ${
            isActive ? 'animate-wave' : 'h-2'
          }`}
          style={{
            animationDelay: `${i * 0.1}s`,
            height: isActive ? `${Math.random() * 30 + 10}px` : '8px'
          }}
        />
      ))}
    </div>
  );
};

const VoiceCoachPage = ({ resume }) => {
  const { t } = useTranslation();
  const {
    isListening,
    transcript,
    interimTranscript,
    isSupported,
    startListening,
    stopListening,
    resetTranscript
  } = useSpeechRecognition();

  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [sessionStats, setSessionStats] = useState({
    questionsAnswered: 0,
    averageScore: 0,
    totalTime: 0
  });
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const timerRef = useRef(null);
  
  // Audio recording state
  const [audioURL, setAudioURL] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingHistory, setRecordingHistory] = useState([]);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);

  const generateQuestions = useCallback(async () => {
    // First try to get cached questions
    try {
      const cachedResponse = await apiClient.get("/api/interview/cached-questions");
      if (cachedResponse.data.questions?.length > 0) {
        setQuestions(cachedResponse.data.questions);
        setCurrentQuestion(cachedResponse.data.questions[0]);
        return;
      }
    } catch (e) {
      console.log("No cached questions, generating new ones");
    }
    
    // Generate new questions using AI interview prep endpoint
    try {
      const response = await apiClient.post("/api/interview-prep", {
        job_title: "Quality Manager",
        company: "",
        difficulty: "medium",
        num_questions: 5,
        topics: resume?.skills?.slice(0, 5) || []
      });
      
      // Map response to expected format
      const questions = response.data.questions?.map(q => ({
        text: q.question,
        type: q.type,
        tip: q.tip,
        sample_points: q.sample_points
      })) || [];
      
      setQuestions(questions);
      if (questions.length > 0) {
        setCurrentQuestion(questions[0]);
      }
    } catch (e) {
      // Fallback to default questions if AI fails
      const defaultQuestions = [
        { text: "Tell me about yourself and your professional background.", type: "Behavioral" },
        { text: "Describe a challenging project you've worked on.", type: "Behavioral" },
        { text: "What are your greatest strengths?", type: "Behavioral" },
        { text: "Where do you see yourself in 5 years?", type: "Behavioral" },
        { text: "Why are you interested in this position?", type: "Situational" }
      ];
      setQuestions(defaultQuestions);
      setCurrentQuestion(defaultQuestions[0]);
    }
  }, [resume?.skills, t]);

  // Load questions on mount
  useEffect(() => {
    if (resume?.skills?.length > 0) {
      generateQuestions();
    }
  }, [resume?.skills?.length, generateQuestions]);

  // Timer for recording duration
  useEffect(() => {
    if (isListening) {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isListening]);

  const startSession = () => {
    setIsSessionActive(true);
    setQuestionIndex(0);
    setFeedback(null);
    setAudioURL(null);
    setRecordingHistory([]);
    setSessionStats({ questionsAnswered: 0, averageScore: 0, totalTime: 0 });
    if (questions.length > 0) {
      setCurrentQuestion(questions[0]);
    }
  };

  // Start audio recording with MediaRecorder
  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioURL(url);
        
        setRecordingHistory(prev => [...prev, {
          id: Date.now(),
          url,
          question: currentQuestion?.text || currentQuestion,
          transcript,
          duration: elapsedTime,
          timestamp: new Date().toISOString()
        }]);
        
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
    } catch (err) {
      console.error('Failed to start audio recording:', err);
    }
  };

  const stopAudioRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const handleStartRecording = async () => {
    setElapsedTime(0);
    setFeedback(null);
    setAudioURL(null);
    startListening();
    await startAudioRecording();
  };

  const handleStopRecording = async () => {
    stopListening();
    stopAudioRecording();
    
    if (transcript.trim().length < 10) {
      toast.error(t("voiceCoach.speakLonger") || "Please speak a longer answer");
      return;
    }

    setIsAnalyzing(true);
    try {
      // Use new Q&A practice endpoint for evaluation
      const response = await apiClient.post("/api/qa-practice", {
        question: currentQuestion?.text || currentQuestion,
        answer: transcript,
        job_context: "Interview practice"
      });
      
      // Map response to expected feedback format
      const feedbackData = {
        overall_score: response.data.score * 10, // Convert 1-10 to percentage
        feedback: response.data.feedback,
        strengths: response.data.strengths || [],
        areas_to_improve: response.data.improvements || [],
        example_answer: response.data.example_answer,
        follow_up_questions: response.data.follow_up_questions || []
      };
      
      setFeedback(feedbackData);
      
      setSessionStats(prev => ({
        questionsAnswered: prev.questionsAnswered + 1,
        averageScore: Math.round(
          (prev.averageScore * prev.questionsAnswered + feedbackData.overall_score) / 
          (prev.questionsAnswered + 1)
        ),
        totalTime: prev.totalTime + elapsedTime
      }));
    } catch (e) {
      toast.error(t("errors.somethingWentWrong"));
    }
    setIsAnalyzing(false);
  };

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.onended = () => setIsPlaying(false);
    }
  }, [audioURL]);

  const nextQuestion = () => {
    const newIndex = questionIndex + 1;
    if (newIndex < questions.length) {
      setQuestionIndex(newIndex);
      setCurrentQuestion(questions[newIndex]);
      setFeedback(null);
      resetTranscript();
      setElapsedTime(0);
    } else {
      toast.success(t("common.success"));
      setIsSessionActive(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isSupported) {
    return (
      <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto">
        <Card className="border-amber-200 bg-amber-50 dark:bg-amber-900/20">
          <CardContent className="p-6 text-center">
            <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-amber-800 dark:text-amber-300 mb-2">
              {t("voiceCoach.notSupported") || "Speech Recognition Not Supported"}
            </h3>
            <p className="text-amber-700 dark:text-amber-400">
              {t("voiceCoach.useChrome") || "Your browser doesn't support voice input. Please use Chrome, Edge, or Safari."}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto animate-fade-in" data-testid="voice-coach-page">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-2" style={{ fontFamily: 'IBM Plex Sans' }}>
          {t("voiceCoach.title") || "AI Interview Coach"}
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          {t("voiceCoach.subtitle") || "Practice speaking your answers and get real-time AI feedback"}
        </p>
      </div>

      {isSessionActive && (
        <Card className="mb-6 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 border-violet-200 dark:border-violet-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-violet-500" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">
                    {t("skills.questionOf", { current: questionIndex + 1, total: questions.length })}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-500" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">
                    {t("voiceCoach.avgScore") || "Avg Score"}: {sessionStats.averageScore || '-'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-sky-500" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">
                    {t("voiceCoach.totalTime") || "Total Time"}: {formatTime(sessionStats.totalTime)}
                  </span>
                </div>
              </div>
              <Badge variant="outline" className="bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300">
                {sessionStats.questionsAnswered} {t("voiceCoach.answered") || "Answered"}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {!isSessionActive ? (
        <Card className="mb-6">
          <CardContent className="p-12 text-center">
            <div className="w-24 h-24 bg-gradient-to-br from-violet-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg shadow-violet-500/30">
              <Mic className="w-12 h-12 text-white" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-3" style={{ fontFamily: 'IBM Plex Sans' }}>
              {t("voiceCoach.practice") || "Voice Interview Practice"}
            </h2>
            <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-md mx-auto">
              {t("voiceCoach.practiceDesc") || "Speak your answers out loud and receive AI-powered feedback on your content, delivery pace, confidence level, and areas for improvement."}
            </p>
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              {[
                { icon: Volume2, label: t("voiceCoach.voiceAnalysis") || "Voice Analysis" },
                { icon: TrendingUp, label: t("video.confidenceScore") || "Confidence Score" },
                { icon: Zap, label: t("voiceCoach.realtimeFeedback") || "Real-time Feedback" },
                { icon: Target, label: t("video.improvementTips") || "Improvement Tips" }
              ].map(({ icon: Icon, label }) => (
                <div key={label} className="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-full">
                  <Icon className="w-4 h-4 text-turquoise" />
                  <span className="text-sm text-slate-600 dark:text-slate-300">{label}</span>
                </div>
              ))}
            </div>
            <Button 
              onClick={startSession}
              size="lg"
              className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
              disabled={questions.length === 0}
              data-testid="start-voice-session"
            >
              <Mic className="w-5 h-5 mr-2" /> {t("voiceCoach.startPractice") || "Start Practice Session"}
            </Button>
            {questions.length === 0 && (
              <p className="text-sm text-amber-600 mt-4">
                {t("video.loadingQuestions") || "Loading interview questions..."}
              </p>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3 space-y-6">
            <Card className="border-2 border-violet-200 dark:border-violet-800">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <Badge variant="outline">{currentQuestion?.category || 'Question'}</Badge>
                  <Badge className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                    {currentQuestion?.difficulty || 'medium'}
                  </Badge>
                </div>
                <CardTitle className="text-xl mt-4" style={{ fontFamily: 'IBM Plex Sans' }}>
                  {currentQuestion?.text || currentQuestion}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center py-6">
                  <VoiceWaveform isActive={isListening} />
                  
                  <div className="flex items-center gap-4 mt-6">
                    {!isListening ? (
                      <Button
                        size="lg"
                        onClick={handleStartRecording}
                        className="w-16 h-16 rounded-full bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700"
                        disabled={isAnalyzing}
                        data-testid="start-voice-recording"
                      >
                        <Mic className="w-8 h-8" />
                      </Button>
                    ) : (
                      <Button
                        size="lg"
                        onClick={handleStopRecording}
                        className="w-16 h-16 rounded-full bg-slate-800 hover:bg-slate-700 animate-pulse"
                        data-testid="stop-voice-recording"
                      >
                        <MicOff className="w-8 h-8" />
                      </Button>
                    )}
                  </div>

                  <div className="flex items-center gap-4 mt-4">
                    <Badge variant="outline" className={isListening ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' : ''}>
                      <Clock className="w-3 h-3 mr-1" />
                      {formatTime(elapsedTime)}
                    </Badge>
                    {transcript && (
                      <Button variant="ghost" size="sm" onClick={resetTranscript}>
                        <RotateCcw className="w-4 h-4 mr-1" /> {t("common.reset") || "Reset"}
                      </Button>
                    )}
                  </div>

                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-4">
                    {isListening ? (t("voiceCoach.listening") || "Listening... Speak your answer") : (t("voiceCoach.clickToRecord") || "Click the microphone to start recording")}
                  </p>
                </div>

                {(transcript || interimTranscript) && (
                  <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                      <MessageSquare className="w-4 h-4" /> {t("interview.yourAnswer") || "Your Answer"}
                    </h4>
                    <p className="text-slate-600 dark:text-slate-400">
                      {transcript}
                      <span className="text-slate-400 dark:text-slate-500">{interimTranscript}</span>
                    </p>
                  </div>
                )}

                {audioURL && (
                  <div className="mt-4 p-4 bg-turquoise/10 dark:bg-turquoise/20 rounded-lg">
                    <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-2">
                      <Volume2 className="w-4 h-4 text-turquoise" /> {t("voiceCoach.playback") || "Recording Playback"}
                    </h4>
                    <div className="flex items-center gap-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={togglePlayback}
                        className="border-turquoise text-turquoise hover:bg-turquoise/10"
                        data-testid="playback-toggle"
                      >
                        {isPlaying ? (
                          <><Pause className="w-4 h-4 mr-2" /> {t("common.pause") || "Pause"}</>
                        ) : (
                          <><Play className="w-4 h-4 mr-2" /> {t("voiceCoach.playRecording") || "Play Recording"}</>
                        )}
                      </Button>
                      <audio ref={audioRef} src={audioURL} className="hidden" />
                      <span className="text-sm text-slate-500 dark:text-slate-400">
                        {t("voiceCoach.duration") || "Duration"}: {formatTime(elapsedTime)}
                      </span>
                    </div>
                  </div>
                )}

                {isAnalyzing && (
                  <div className="mt-4 p-4 bg-violet-50 dark:bg-violet-900/20 rounded-lg text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-violet-500 mx-auto mb-2" />
                    <p className="text-violet-700 dark:text-violet-300">{t("common.loading") || "Analyzing your response..."}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {feedback && (
              <div className="flex justify-between">
                <Button variant="outline" onClick={() => { setFeedback(null); resetTranscript(); setElapsedTime(0); }}>
                  <RefreshCw className="w-4 h-4 mr-2" /> {t("interview.tryAgain") || "Try Again"}
                </Button>
                <Button onClick={nextQuestion} className="bg-gradient-to-r from-violet-500 to-purple-600">
                  {questionIndex + 1 < questions.length ? (
                    <>{t("interview.nextQuestion") || "Next Question"} <ChevronRight className="w-4 h-4 ml-1" /></>
                  ) : (
                    <>{t("voiceCoach.finishSession") || "Finish Session"} <CheckCircle2 className="w-4 h-4 ml-1" /></>
                  )}
                </Button>
              </div>
            )}
          </div>

          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
                  <Sparkles className="w-5 h-5 text-violet-500" />
                  {t("voiceCoach.aiFeedback") || "AI Feedback"}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {feedback ? (
                  <div className="space-y-6">
                    <div className="flex justify-around">
                      <CircularScore 
                        score={feedback.overall_score} 
                        label={t("voiceCoach.overall") || "Overall"} 
                        color="#8B5CF6" 
                      />
                      <CircularScore 
                        score={feedback.confidence_score} 
                        label={t("video.confidence") || "Confidence"} 
                        color="#20b2aa" 
                      />
                    </div>

                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-slate-600 dark:text-slate-400">{t("voiceCoach.contentQuality") || "Content Quality"}</span>
                          <span className="font-medium">{feedback.content_score}%</span>
                        </div>
                        <Progress value={feedback.content_score} className="h-2" />
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-slate-600 dark:text-slate-400">{t("voiceCoach.deliveryPace") || "Delivery Pace"}</span>
                          <span className="font-medium">{feedback.pace_score}%</span>
                        </div>
                        <Progress value={feedback.pace_score} className="h-2" />
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-slate-600 dark:text-slate-400">{t("voiceCoach.structure") || "Structure"}</span>
                          <span className="font-medium">{feedback.structure_score}%</span>
                        </div>
                        <Progress value={feedback.structure_score} className="h-2" />
                      </div>
                    </div>

                    {feedback.strengths?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-emerald-700 dark:text-emerald-400 mb-2 flex items-center gap-1">
                          <CheckCircle2 className="w-4 h-4" /> {t("video.strengths") || "Strengths"}
                        </h4>
                        <ul className="space-y-1">
                          {feedback.strengths.map((s, i) => (
                            <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                              ✓ {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {feedback.improvements?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-amber-700 dark:text-amber-400 mb-2 flex items-center gap-1">
                          <Target className="w-4 h-4" /> {t("video.areasToImprove") || "Areas to Improve"}
                        </h4>
                        <ul className="space-y-1">
                          {feedback.improvements.map((s, i) => (
                            <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                              → {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {feedback.delivery_tip && (
                      <div className="p-3 bg-violet-50 dark:bg-violet-900/20 rounded-lg">
                        <h4 className="text-sm font-medium text-violet-700 dark:text-violet-300 mb-1">
                          💡 {t("voiceCoach.deliveryTip") || "Delivery Tip"}
                        </h4>
                        <p className="text-sm text-violet-600 dark:text-violet-400">
                          {feedback.delivery_tip}
                        </p>
                      </div>
                    )}

                    <div className="flex gap-4 text-sm text-slate-500 dark:text-slate-400">
                      <span>{t("voiceCoach.words") || "Words"}: {feedback.word_count}</span>
                      <span>{t("voiceCoach.pace") || "Pace"}: {feedback.words_per_minute} WPM</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-400 dark:text-slate-500">
                    <Volume2 className="w-12 h-12 mx-auto mb-4 opacity-40" />
                    <p>{t("voiceCoach.recordToReceive") || "Record your answer to receive AI feedback"}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {recordingHistory.length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2" style={{ fontFamily: 'IBM Plex Sans' }}>
              <Volume2 className="w-5 h-5 text-turquoise" />
              {t("voiceCoach.recordingHistory") || "Recording History"} ({recordingHistory.length})
            </CardTitle>
            <CardDescription>{t("voiceCoach.replayRecordings") || "Replay your practice recordings from this session"}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recordingHistory.map((recording, idx) => (
                <div 
                  key={recording.id} 
                  className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-slate-900 dark:text-slate-100 text-sm truncate">
                      Q{idx + 1}: {typeof recording.question === 'string' ? recording.question.slice(0, 60) : 'Practice Response'}...
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {t("voiceCoach.duration") || "Duration"}: {formatTime(recording.duration)} • {recording.transcript?.split(' ').length || 0} {t("voiceCoach.words") || "words"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <audio 
                      id={`audio-history-${recording.id}`}
                      src={recording.url} 
                      className="hidden"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        const audio = document.getElementById(`audio-history-${recording.id}`);
                        if (audio) {
                          if (audio.paused) {
                            audio.play();
                          } else {
                            audio.pause();
                            audio.currentTime = 0;
                          }
                        }
                      }}
                      className="border-turquoise text-turquoise hover:bg-turquoise/10"
                      data-testid={`play-recording-${idx}`}
                    >
                      <Play className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
            {t("voiceCoach.tips") || "Voice Interview Tips"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { icon: Clock, title: t("voiceCoach.idealLength") || "Ideal Length", desc: t("voiceCoach.idealLengthDesc") || "Aim for 1-2 minute answers (150-300 words)" },
              { icon: Volume2, title: t("voiceCoach.clearSpeech") || "Clear Speech", desc: t("voiceCoach.clearSpeechDesc") || "Speak clearly and at a moderate pace" },
              { icon: Zap, title: t("voiceCoach.beSpecific") || "Be Specific", desc: t("voiceCoach.beSpecificDesc") || "Use concrete examples and metrics" },
              { icon: Target, title: t("voiceCoach.stayFocused") || "Stay Focused", desc: t("voiceCoach.stayFocusedDesc") || "Answer the question directly, then elaborate" }
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

      <style>{`
        @keyframes wave {
          0%, 100% { height: 8px; }
          50% { height: 32px; }
        }
        .animate-wave {
          animation: wave 0.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default VoiceCoachPage;
