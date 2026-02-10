import { useState, useEffect, useRef, useCallback, memo } from "react";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  Video, VideoOff, Play, RotateCcw, 
  Sparkles, Loader2, Camera, Clock, CheckCircle2, AlertCircle,
  TrendingUp, Eye, User, Zap, Target, Award,
  ChevronRight, Trash2, Activity, Smile
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";
import { OptimizedVideoPlayer, VideoSkeleton, PlayButton } from "@/components/OptimizedMedia";

// TensorFlow.js imports
let tf, faceLandmarksDetection;

// Dynamic TensorFlow loading to avoid SSR issues with timeout
const loadTensorFlow = async (timeoutMs = 15000) => {
  const timeoutPromise = new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Model loading timeout')), timeoutMs)
  );
  
  const loadPromise = (async () => {
    if (!tf) {
      tf = await import('@tensorflow/tfjs');
      await tf.setBackend('webgl');
      await tf.ready();
    }
    if (!faceLandmarksDetection) {
      faceLandmarksDetection = await import('@tensorflow-models/face-landmarks-detection');
    }
    return { tf, faceLandmarksDetection };
  })();
  
  return Promise.race([loadPromise, timeoutPromise]);
};

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
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold" style={{ color }}>{Math.round(score)}</span>
        </div>
      </div>
      <span className="text-xs text-slate-500 dark:text-slate-400 mt-1 text-center">{label}</span>
    </div>
  );
};

// Real-time facial analysis indicator
const LiveIndicator = ({ isActive, label }) => (
  <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
    isActive 
      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' 
      : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
  }`}>
    <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`} />
    {label}
  </div>
);

// Expression emoji mapping
const EXPRESSION_EMOJI = {
  'neutral': '😐',
  'happy': '😊',
  'confident': '💪',
  'engaged': '🎯',
  'nervous': '😰',
  'uncertain': '🤔',
  'distracted': '😶',
  'focused': '👁️'
};

const VideoInterviewPage = ({ resume }) => {
  const { isDark } = useTheme();
  const { t } = useTranslation();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const detectorRef = useRef(null);
  const analysisIntervalRef = useRef(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [recordedVideoURL, setRecordedVideoURL] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [recordings, setRecordings] = useState([]);
  const [isSessionActive, setIsSessionActive] = useState(false);
  
  // TensorFlow.js state
  const [isModelLoading, setIsModelLoading] = useState(false);
  const [modelLoaded, setModelLoaded] = useState(false);
  const [realTimeAnalysis, setRealTimeAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [sessionSummary, setSessionSummary] = useState(null);
  
  const timerRef = useRef(null);

  // Load TensorFlow model
  const loadModel = async () => {
    if (modelLoaded || isModelLoading) return;
    
    setIsModelLoading(true);
    try {
      const { faceLandmarksDetection } = await loadTensorFlow();
      
      const model = faceLandmarksDetection.SupportedModels.MediaPipeFaceMesh;
      const detectorConfig = {
        runtime: 'tfjs',
        refineLandmarks: true,
        maxFaces: 1
      };
      
      detectorRef.current = await faceLandmarksDetection.createDetector(model, detectorConfig);
      setModelLoaded(true);
      toast.success('Facial analysis ready!');
    } catch (error) {
      console.error('Failed to load face detection model:', error);
      toast.error('Failed to load facial analysis. Using basic mode.');
    }
    setIsModelLoading(false);
  };

  // Analyze face from video frame
  const analyzeFace = async () => {
    if (!detectorRef.current || !videoRef.current || !isPreviewing) return null;
    
    try {
      const video = videoRef.current;
      if (video.readyState < 2) return null;
      
      const faces = await detectorRef.current.estimateFaces(video);
      
      if (faces.length === 0) {
        return {
          faceDetected: false,
          eyeContact: 0,
          expression: 'no_face',
          engagement: 0,
          tips: ['Make sure your face is clearly visible in the frame']
        };
      }
      
      const face = faces[0];
      const keypoints = face.keypoints;
      
      // Calculate eye contact based on iris position
      const leftIris = keypoints.find(p => p.name === 'leftIris');
      const rightIris = keypoints.find(p => p.name === 'rightIris');
      const nose = keypoints.find(p => p.name === 'noseTip');
      
      let eyeContactScore = 70; // Base score
      if (leftIris && rightIris && nose) {
        // Check if eyes are looking forward (at camera)
        const irisCenter = {
          x: (leftIris.x + rightIris.x) / 2,
          y: (leftIris.y + rightIris.y) / 2
        };
        const noseX = nose.x;
        
        // Distance from center indicates where person is looking
        const horizontalOffset = Math.abs(irisCenter.x - noseX);
        const normalizedOffset = horizontalOffset / video.videoWidth;
        
        // Lower offset = better eye contact
        eyeContactScore = Math.max(0, Math.min(100, 100 - (normalizedOffset * 500)));
      }
      
      // Calculate head position
      const leftEar = keypoints.find(p => p.name === 'leftEarTragion');
      const rightEar = keypoints.find(p => p.name === 'rightEarTragion');
      let headPosition = 'centered';
      
      if (leftEar && rightEar) {
        const earDiff = Math.abs(leftEar.y - rightEar.y);
        if (earDiff > 20) {
          headPosition = leftEar.y > rightEar.y ? 'tilted_left' : 'tilted_right';
        }
        
        const faceWidth = Math.abs(leftEar.x - rightEar.x);
        const faceCenterX = (leftEar.x + rightEar.x) / 2;
        const frameCenter = video.videoWidth / 2;
        
        if (Math.abs(faceCenterX - frameCenter) > faceWidth * 0.3) {
          headPosition = faceCenterX < frameCenter ? 'looking_left' : 'looking_right';
        }
      }
      
      // Estimate expression based on mouth landmarks
      const upperLip = keypoints.find(p => p.name === 'upperLip');
      const lowerLip = keypoints.find(p => p.name === 'lowerLip');
      const leftMouth = keypoints.find(p => p.name === 'mouthLeft');
      const rightMouth = keypoints.find(p => p.name === 'mouthRight');
      
      let expression = 'neutral';
      let engagementScore = 75;
      
      if (upperLip && lowerLip && leftMouth && rightMouth) {
        const mouthOpenness = Math.abs(upperLip.y - lowerLip.y);
        const mouthWidth = Math.abs(leftMouth.x - rightMouth.x);
        
        // Speaking detection
        if (mouthOpenness > 15) {
          expression = 'engaged';
          engagementScore = 85;
        }
        
        // Smile detection (corners of mouth higher)
        const mouthCenterY = (upperLip.y + lowerLip.y) / 2;
        const leftCornerOffset = mouthCenterY - leftMouth.y;
        const rightCornerOffset = mouthCenterY - rightMouth.y;
        
        if (leftCornerOffset > 3 && rightCornerOffset > 3) {
          expression = 'happy';
          engagementScore = 90;
        }
      }
      
      // Adjust engagement based on eye contact and head position
      if (eyeContactScore > 80) engagementScore += 5;
      if (headPosition === 'centered') engagementScore += 5;
      if (headPosition.includes('tilted') || headPosition.includes('looking')) engagementScore -= 10;
      
      engagementScore = Math.max(0, Math.min(100, engagementScore));
      
      // Generate tips
      const tips = [];
      if (eyeContactScore < 60) tips.push('Look directly at the camera lens');
      if (headPosition !== 'centered') tips.push('Keep your head centered and facing forward');
      if (engagementScore < 70) tips.push('Try to show more enthusiasm with your expressions');
      if (expression === 'neutral') tips.push('A slight smile can make you appear more confident');
      
      return {
        faceDetected: true,
        eyeContact: Math.round(eyeContactScore),
        expression,
        engagement: Math.round(engagementScore),
        headPosition,
        confidence: Math.round((eyeContactScore + engagementScore) / 2),
        tips: tips.length > 0 ? tips : ['Great! Keep maintaining your presence']
      };
    } catch (error) {
      console.error('Face analysis error:', error);
      return null;
    }
  };

  // Start real-time analysis
  const startRealTimeAnalysis = () => {
    if (!modelLoaded || analysisIntervalRef.current) return;
    
    analysisIntervalRef.current = setInterval(async () => {
      const analysis = await analyzeFace();
      if (analysis) {
        setRealTimeAnalysis(analysis);
        if (analysis.faceDetected) {
          setAnalysisHistory(prev => [...prev, {
            ...analysis,
            timestamp: Date.now()
          }]);
        }
      }
    }, 500); // Analyze every 500ms
  };

  // Stop real-time analysis
  const stopRealTimeAnalysis = () => {
    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current);
      analysisIntervalRef.current = null;
    }
  };

  // Calculate session summary from analysis history
  const calculateSessionSummary = () => {
    if (analysisHistory.length === 0) return null;
    
    const validAnalyses = analysisHistory.filter(a => a.faceDetected);
    if (validAnalyses.length === 0) return null;
    
    const avgEyeContact = validAnalyses.reduce((sum, a) => sum + a.eyeContact, 0) / validAnalyses.length;
    const avgEngagement = validAnalyses.reduce((sum, a) => sum + a.engagement, 0) / validAnalyses.length;
    const avgConfidence = validAnalyses.reduce((sum, a) => sum + a.confidence, 0) / validAnalyses.length;
    
    // Expression distribution
    const expressionCounts = {};
    validAnalyses.forEach(a => {
      expressionCounts[a.expression] = (expressionCounts[a.expression] || 0) + 1;
    });
    
    const dominantExpression = Object.entries(expressionCounts)
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'neutral';
    
    // Trend analysis
    const firstHalf = validAnalyses.slice(0, Math.floor(validAnalyses.length / 2));
    const secondHalf = validAnalyses.slice(Math.floor(validAnalyses.length / 2));
    
    const firstHalfEngagement = firstHalf.reduce((sum, a) => sum + a.engagement, 0) / firstHalf.length;
    const secondHalfEngagement = secondHalf.reduce((sum, a) => sum + a.engagement, 0) / secondHalf.length;
    
    let trend = 'consistent';
    if (secondHalfEngagement > firstHalfEngagement + 5) trend = 'improving';
    if (secondHalfEngagement < firstHalfEngagement - 5) trend = 'declining';
    
    // Generate strengths and improvements
    const strengths = [];
    const improvements = [];
    
    if (avgEyeContact >= 75) strengths.push('Excellent eye contact maintained throughout');
    else if (avgEyeContact < 60) improvements.push('Work on maintaining consistent eye contact with the camera');
    
    if (avgEngagement >= 80) strengths.push('High engagement and enthusiasm shown');
    else if (avgEngagement < 65) improvements.push('Try to appear more engaged and enthusiastic');
    
    if (dominantExpression === 'happy' || dominantExpression === 'engaged') {
      strengths.push('Positive and approachable demeanor');
    }
    
    if (trend === 'improving') strengths.push('Great improvement as the session progressed');
    if (trend === 'declining') improvements.push('Try to maintain energy throughout longer responses');
    
    return {
      eyeContact: Math.round(avgEyeContact),
      engagement: Math.round(avgEngagement),
      confidence: Math.round(avgConfidence),
      dominantExpression,
      expressionDistribution: expressionCounts,
      trend,
      strengths: strengths.length > 0 ? strengths : ['Completed the practice session'],
      improvements: improvements.length > 0 ? improvements : ['Continue practicing to build confidence'],
      totalFrames: validAnalyses.length,
      duration: elapsedTime
    };
  };

  const generateQuestions = useCallback(async () => {
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
    
    try {
      const response = await apiClient.post("/api/interview/generate-questions", {
        job_title: "Quality Manager",
        company: "",
        resume_skills: resume?.skills || []
      });
      setQuestions(response.data.questions || []);
      if (response.data.questions?.length > 0) {
        setCurrentQuestion(response.data.questions[0]);
      }
    } catch (e) {
      // Fallback questions
      const defaultQuestions = [
        { text: "Tell me about yourself and your professional background.", category: "Behavioral" },
        { text: "Describe a challenging project you've led.", category: "Leadership" },
        { text: "How do you handle tight deadlines?", category: "Situational" },
        { text: "What are your greatest strengths?", category: "Self-Assessment" },
        { text: "Where do you see yourself in 5 years?", category: "Goals" }
      ];
      setQuestions(defaultQuestions);
      setCurrentQuestion(defaultQuestions[0]);
    }
  }, [resume]);

  const loadRecordings = useCallback(async () => {
    try {
      const response = await apiClient.get("/api/interview/video-recordings");
      setRecordings(response.data || []);
    } catch (e) {
      console.error("Failed to load recordings");
    }
  }, []);

  useEffect(() => {
    if (resume?.skills?.length > 0) {
      generateQuestions();
    }
    loadRecordings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resume?.skills?.length]);

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

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRealTimeAnalysis();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

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
      
      // Load model in background
      loadModel();
    } catch (err) {
      toast.error(t("errors.somethingWentWrong"));
      console.error("Camera error:", err);
    }
  };

  const stopPreview = () => {
    stopRealTimeAnalysis();
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsPreviewing(false);
    setRealTimeAnalysis(null);
  };

  const startRecording = () => {
    if (!streamRef.current) return;
    
    chunksRef.current = [];
    setAnalysisHistory([]);
    setSessionSummary(null);
    
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
    
    // Start real-time analysis
    if (modelLoaded) {
      startRealTimeAnalysis();
    }
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
    stopRealTimeAnalysis();
    
    // Calculate session summary
    const summary = calculateSessionSummary();
    setSessionSummary(summary);
    
    if (summary) {
      toast.success('Analysis complete!');
    }
  };

  const startSession = () => {
    setIsSessionActive(true);
    setQuestionIndex(0);
    setSessionSummary(null);
    setRecordedVideoURL(null);
    setAnalysisHistory([]);
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
      setSessionSummary(null);
      setRecordedVideoURL(null);
      setElapsedTime(0);
      setAnalysisHistory([]);
    } else {
      toast.success(t("common.success"));
      setIsSessionActive(false);
      stopPreview();
    }
  };

  const endSession = () => {
    setIsSessionActive(false);
    stopPreview();
    setSessionSummary(null);
    setRecordedVideoURL(null);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const deleteRecording = async (recordingId) => {
    try {
      await apiClient.delete(`/api/interview/video-recordings/${recordingId}`);
      setRecordings(prev => prev.filter(r => r.id !== recordingId));
      toast.success(t("common.delete") + " " + t("common.success").toLowerCase());
    } catch (e) {
      toast.error(t("errors.somethingWentWrong"));
    }
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="video-interview-page">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Video className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
            {t("video.title")}
          </h1>
        </div>
        <p className="text-slate-500 dark:text-slate-400">
          {t("video.subtitle")} • Real-time facial expression analysis powered by TensorFlow.js
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
              AI-Powered Video Practice
            </h2>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              Practice interviews with real-time AI analysis of your facial expressions, eye contact, and body language
            </p>
            
            <div className="flex flex-wrap justify-center gap-3 mb-8">
              {[
                { icon: Eye, label: 'Eye Contact Tracking' },
                { icon: Smile, label: 'Expression Analysis' },
                { icon: Activity, label: 'Engagement Score' },
                { icon: Sparkles, label: 'AI Coaching Tips' }
              ].map(({ icon: Icon, label }) => (
                <Badge key={label} variant="outline" className="px-3 py-1.5">
                  <Icon className="w-3 h-3 mr-1.5" /> {label}
                </Badge>
              ))}
            </div>

            <Button 
              size="lg" 
              onClick={startSession}
              className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700"
              data-testid="start-video-session"
            >
              <Camera className="w-5 h-5 mr-2" /> {t("video.startSession")}
            </Button>
            
            {questions.length === 0 && (
              <p className="text-sm text-amber-600 mt-4">{t("video.loadingQuestions")}</p>
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
                  <canvas ref={canvasRef} className="hidden" />
                  
                  {/* Status Indicators */}
                  <div className="absolute top-4 left-4 flex items-center gap-2">
                    {isRecording && (
                      <div className="flex items-center gap-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm">
                        <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
                        REC {formatTime(elapsedTime)}
                      </div>
                    )}
                    <LiveIndicator 
                      isActive={modelLoaded && isPreviewing} 
                      label={modelLoaded ? 'AI Active' : isModelLoading ? 'Loading AI...' : 'Basic Mode'} 
                    />
                  </div>
                  
                  {/* Real-time feedback overlay */}
                  {isRecording && realTimeAnalysis?.faceDetected && (
                    <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end">
                      <div className="bg-black/60 backdrop-blur-sm rounded-lg px-4 py-2 text-white text-sm">
                        <div className="flex items-center gap-4">
                          <span className="flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            Eye: {realTimeAnalysis.eyeContact}%
                          </span>
                          <span className="flex items-center gap-1">
                            <Activity className="w-4 h-4" />
                            Engagement: {realTimeAnalysis.engagement}%
                          </span>
                          <span className="text-lg">
                            {EXPRESSION_EMOJI[realTimeAnalysis.expression] || '😐'}
                          </span>
                        </div>
                      </div>
                      
                      {realTimeAnalysis.tips?.[0] && (
                        <div className="bg-turquoise/90 backdrop-blur-sm rounded-lg px-3 py-1.5 text-white text-xs max-w-xs">
                          💡 {realTimeAnalysis.tips[0]}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Loading Model Overlay */}
                  {isModelLoading && (
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                      <div className="text-center text-white">
                        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                        <p className="text-sm">Loading AI analysis...</p>
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
                      disabled={!isPreviewing}
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
                </div>

                <p className="text-center text-sm text-slate-500 dark:text-slate-400 pb-4">
                  {isRecording ? 'Recording with live AI analysis...' : 'Click to start recording'}
                </p>
              </CardContent>
            </Card>

            {/* Recorded Video Playback */}
            {recordedVideoURL && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Play className="w-5 h-5 text-turquoise" />
                    {t("video.yourRecording")}
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
                    {t("video.nextQuestion")} <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={endSession}
                    disabled={isRecording}
                  >
                    {t("video.end")}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Results */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-violet-500" />
                  {sessionSummary ? 'Session Analysis' : 'Live Analysis'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {sessionSummary ? (
                  <div className="space-y-6">
                    {/* Scores */}
                    <div className="grid grid-cols-3 gap-2">
                      <CircularScore 
                        score={sessionSummary.eyeContact} 
                        label="Eye Contact" 
                        color="#20b2aa" 
                      />
                      <CircularScore 
                        score={sessionSummary.engagement} 
                        label="Engagement" 
                        color="#8b5cf6" 
                      />
                      <CircularScore 
                        score={sessionSummary.confidence} 
                        label="Confidence" 
                        color="#f59e0b" 
                      />
                    </div>

                    {/* Expression & Trend */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg text-center">
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Expression</p>
                        <p className="text-2xl">{EXPRESSION_EMOJI[sessionSummary.dominantExpression]}</p>
                        <p className="text-xs font-medium capitalize">{sessionSummary.dominantExpression}</p>
                      </div>
                      <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg text-center">
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Trend</p>
                        <TrendingUp className={`w-6 h-6 mx-auto ${
                          sessionSummary.trend === 'improving' ? 'text-emerald-500' :
                          sessionSummary.trend === 'declining' ? 'text-red-500 rotate-180' :
                          'text-slate-400'
                        }`} />
                        <p className="text-xs font-medium capitalize">{sessionSummary.trend}</p>
                      </div>
                    </div>

                    {/* Strengths */}
                    {sessionSummary.strengths?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-emerald-700 dark:text-emerald-400 mb-2 flex items-center gap-1">
                          <CheckCircle2 className="w-4 h-4" /> Strengths
                        </h4>
                        <ul className="space-y-1">
                          {sessionSummary.strengths.map((s, i) => (
                            <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                              ✓ {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Improvements */}
                    {sessionSummary.improvements?.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-amber-700 dark:text-amber-400 mb-2 flex items-center gap-1">
                          <Target className="w-4 h-4" /> Areas to Improve
                        </h4>
                        <ul className="space-y-1">
                          {sessionSummary.improvements.map((s, i) => (
                            <li key={i} className="text-sm text-slate-600 dark:text-slate-400">
                              → {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="text-xs text-slate-400 dark:text-slate-500 text-center pt-2 border-t border-slate-200 dark:border-slate-700">
                      Analyzed {sessionSummary.totalFrames} frames over {formatTime(sessionSummary.duration)}
                    </div>
                  </div>
                ) : realTimeAnalysis ? (
                  <div className="space-y-4">
                    {realTimeAnalysis.faceDetected ? (
                      <>
                        <div className="grid grid-cols-3 gap-2">
                          <CircularScore 
                            score={realTimeAnalysis.eyeContact} 
                            label="Eye" 
                            color="#20b2aa" 
                          />
                          <CircularScore 
                            score={realTimeAnalysis.engagement} 
                            label="Engage" 
                            color="#8b5cf6" 
                          />
                          <CircularScore 
                            score={realTimeAnalysis.confidence} 
                            label="Conf." 
                            color="#f59e0b" 
                          />
                        </div>
                        
                        <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg text-center">
                          <p className="text-xs text-slate-500 dark:text-slate-400">Expression</p>
                          <p className="text-3xl my-1">{EXPRESSION_EMOJI[realTimeAnalysis.expression]}</p>
                          <p className="text-sm font-medium capitalize">{realTimeAnalysis.expression}</p>
                        </div>

                        {realTimeAnalysis.tips?.[0] && (
                          <div className="p-3 bg-turquoise/10 rounded-lg">
                            <p className="text-sm text-turquoise font-medium">💡 Quick Tip</p>
                            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                              {realTimeAnalysis.tips[0]}
                            </p>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="text-center py-4 text-amber-600 dark:text-amber-400">
                        <AlertCircle className="w-10 h-10 mx-auto mb-2 opacity-60" />
                        <p className="text-sm">Face not detected</p>
                        <p className="text-xs mt-1">Position yourself in the center of the frame</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-400 dark:text-slate-500">
                    <Eye className="w-12 h-12 mx-auto mb-4 opacity-40" />
                    <p>{isRecording ? 'Analyzing...' : 'Start recording to see live analysis'}</p>
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
              {t("video.previousSessions")}
            </CardTitle>
            <CardDescription>{t("video.previousSessionsDesc")}</CardDescription>
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
              { icon: Eye, title: 'Eye Contact', desc: 'Look directly at the camera lens, not the screen' },
              { icon: User, title: 'Posture', desc: 'Sit up straight with shoulders back' },
              { icon: Camera, title: 'Lighting', desc: 'Face a light source, avoid backlighting' },
              { icon: Award, title: 'Expression', desc: 'Maintain a natural, friendly expression' }
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
