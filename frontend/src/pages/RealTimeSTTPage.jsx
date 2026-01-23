import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { 
  Mic, MicOff, Loader2, Clock, CheckCircle2, AlertCircle,
  Globe, Copy, Trash2, History, Settings, Volume2, 
  Sparkles, FileText, Download, RotateCcw, Languages
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useTranslation } from "@/utils/i18n";
import { apiClient } from "@/utils/apiClient";

// Voice Waveform Visualization Component
const VoiceWaveform = ({ isActive, audioLevel = 0 }) => {
  const bars = 24;
  // Pre-generate random heights for consistent rendering
  const randomHeights = Array.from({ length: bars }, () => Math.random() * 10);
  
  return (
    <div className="flex items-center justify-center gap-0.5 h-16">
      {[...Array(bars)].map((_, i) => {
        const centerDistance = Math.abs(i - bars / 2) / (bars / 2);
        const baseHeight = isActive ? (1 - centerDistance * 0.7) * (30 + audioLevel * 20) : 4;
        return (
          <div
            key={i}
            className={`w-1 bg-gradient-to-t from-turquoise to-cyan-400 rounded-full transition-all duration-75 ${
              isActive ? 'animate-pulse' : 'opacity-30'
            }`}
            style={{
              height: `${isActive ? baseHeight + randomHeights[i] : 4}px`,
              animationDelay: `${i * 30}ms`
            }}
          />
        );
      })}
    </div>
  );
};

// Transcription History Item
const TranscriptionItem = ({ item, onDelete, onCopy }) => (
  <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg group">
    <div className="flex items-start justify-between gap-3">
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-3">
          {item.text}
        </p>
        <div className="flex items-center gap-3 mt-2 text-xs text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(item.created_at).toLocaleString()}
          </span>
          <span>{item.word_count} words</span>
          <Badge variant="outline" className="text-xs">
            {item.language || 'en'}
          </Badge>
        </div>
      </div>
      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="sm" onClick={() => onCopy(item.text)}>
          <Copy className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="sm" onClick={() => onDelete(item.id)} className="text-red-500 hover:text-red-600">
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  </div>
);

const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'de', name: 'German' },
  { code: 'it', name: 'Italian' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'nl', name: 'Dutch' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'zh', name: 'Chinese' }
];

const RealTimeSTTPage = () => {
  const { t } = useTranslation();
  
  // Service status
  const [serviceStatus, setServiceStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  
  // Settings
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [useWebSocket, setUseWebSocket] = useState(true);
  
  // History
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  
  // Refs
  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const audioChunksRef = useRef([]);

  const checkServiceStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/realtime-stt/status');
      setServiceStatus(response.data);
    } catch (e) {
      console.error('Failed to check STT status:', e);
      setServiceStatus({ available: false });
    }
    setIsLoading(false);
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/realtime-stt/history');
      setHistory(response.data.history || []);
    } catch (e) {
      console.error('Failed to load history:', e);
    }
  }, []);

  // Check service status on mount
  useEffect(() => {
    checkServiceStatus();
    loadHistory();
  }, [checkServiceStatus, loadHistory]);

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

  // Audio level analysis
  const startAudioAnalysis = (stream) => {
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    analyserRef.current = audioContextRef.current.createAnalyser();
    const source = audioContextRef.current.createMediaStreamSource(stream);
    source.connect(analyserRef.current);
    analyserRef.current.fftSize = 256;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const updateLevel = () => {
      if (!analyserRef.current) return;
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setAudioLevel(average / 128); // Normalize to 0-2 range
      animationFrameRef.current = requestAnimationFrame(updateLevel);
    };
    
    updateLevel();
  };

  const stopAudioAnalysis = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    setAudioLevel(0);
  };

  // Start recording with WebSocket streaming
  const startRecording = async () => {
    setIsConnecting(true);
    setTranscript('');
    setInterimTranscript('');
    setElapsedTime(0);
    audioChunksRef.current = [];

    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      streamRef.current = stream;
      startAudioAnalysis(stream);

      if (useWebSocket && serviceStatus?.features?.streaming) {
        // WebSocket streaming mode
        const token = localStorage.getItem('token');
        const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/realtime-stt/stream`;
        
        wsRef.current = new WebSocket(wsUrl);
        
        wsRef.current.onopen = () => {
          // Send authentication and config
          wsRef.current.send(JSON.stringify({
            type: 'start',
            token: token,
            language: selectedLanguage
          }));
        };

        wsRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.type === 'ready') {
            setIsRecording(true);
            setIsConnecting(false);
            // Start sending audio
            startMediaRecorder(stream);
          } else if (data.type === 'transcription') {
            if (data.is_final) {
              setTranscript(prev => prev + ' ' + data.text);
              setInterimTranscript('');
            } else {
              setInterimTranscript(data.text);
            }
          } else if (data.type === 'final') {
            setTranscript(data.text);
            toast.success('Transcription completed!');
          } else if (data.type === 'error') {
            toast.error(data.message);
            stopRecording();
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
          toast.error('Connection error. Falling back to batch mode.');
          setUseWebSocket(false);
          startBatchRecording(stream);
        };

        wsRef.current.onclose = () => {
          if (isRecording) {
            stopRecording();
          }
        };
      } else {
        // Batch recording mode (fallback)
        startBatchRecording(stream);
      }
    } catch (err) {
      console.error('Failed to start recording:', err);
      toast.error('Failed to access microphone');
      setIsConnecting(false);
    }
  };

  const startMediaRecorder = (stream) => {
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    mediaRecorder.ondataavailable = async (event) => {
      if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
        // Convert blob to base64 and send
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result.split(',')[1];
          wsRef.current.send(JSON.stringify({
            type: 'audio',
            data: base64,
            format: 'webm'
          }));
        };
        reader.readAsDataURL(event.data);
      }
    };

    mediaRecorder.start(1000); // Send chunks every 1 second
    mediaRecorderRef.current = mediaRecorder;
  };

  const startBatchRecording = (stream) => {
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };

    mediaRecorder.start(1000);
    mediaRecorderRef.current = mediaRecorder;
    setIsRecording(true);
    setIsConnecting(false);
  };

  const stopRecording = async () => {
    setIsRecording(false);
    stopAudioAnalysis();

    // Stop media recorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    // Stop stream tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: 'stop' }));
      wsRef.current.close();
      wsRef.current = null;
    }

    // If batch mode, send audio for transcription
    if (!useWebSocket && audioChunksRef.current.length > 0) {
      await transcribeBatchAudio();
    }

    loadHistory();
  };

  const transcribeBatchAudio = async () => {
    setIsConnecting(true);
    try {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      
      // Convert to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64 = reader.result.split(',')[1];
        
        try {
          const response = await apiClient.post('/api/realtime-stt/transcribe-base64', {
            audio: base64,
            format: 'webm',
            language: selectedLanguage
          });
          
          if (response.data.success) {
            setTranscript(response.data.text);
            toast.success(`Transcribed ${response.data.word_count} words`);
          }
        } catch (e) {
          toast.error('Transcription failed');
        }
        setIsConnecting(false);
      };
    } catch (e) {
      console.error('Batch transcription error:', e);
      toast.error('Failed to process audio');
      setIsConnecting(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const deleteFromHistory = async (id) => {
    try {
      await apiClient.delete(`/api/realtime-stt/history/${id}`);
      setHistory(prev => prev.filter(h => h.id !== id));
      toast.success('Deleted');
    } catch (e) {
      toast.error('Failed to delete');
    }
  };

  const downloadTranscript = () => {
    if (!transcript) return;
    const blob = new Blob([transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-5xl mx-auto animate-fade-in" data-testid="realtime-stt-page">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-turquoise to-cyan-500 rounded-xl flex items-center justify-center">
            <Mic className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight" style={{ fontFamily: 'IBM Plex Sans' }}>
            Real-Time Voice Transcription
          </h1>
        </div>
        <p className="text-slate-500 dark:text-slate-400">
          Convert your speech to text in real-time using AI-powered transcription
        </p>
      </div>

      {/* Service Status */}
      {!serviceStatus?.available && (
        <Card className="mb-6 border-amber-200 bg-amber-50 dark:bg-amber-900/20">
          <CardContent className="p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-amber-500" />
            <div>
              <p className="font-medium text-amber-800 dark:text-amber-300">
                Transcription service unavailable
              </p>
              <p className="text-sm text-amber-700 dark:text-amber-400">
                The AI transcription service is not configured. Contact support.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Recording Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recording Card */}
          <Card className="border-2 border-turquoise/30">
            <CardContent className="p-8">
              <div className="text-center">
                {/* Waveform */}
                <div className="mb-6 py-4 px-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                  <VoiceWaveform isActive={isRecording} audioLevel={audioLevel} />
                </div>

                {/* Timer */}
                <div className="mb-6">
                  <Badge 
                    variant="outline" 
                    className={`text-lg px-4 py-2 ${isRecording ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 animate-pulse' : ''}`}
                  >
                    <Clock className="w-4 h-4 mr-2" />
                    {formatTime(elapsedTime)}
                  </Badge>
                </div>

                {/* Recording Button */}
                <div className="flex items-center justify-center gap-4">
                  {!isRecording ? (
                    <Button
                      size="lg"
                      onClick={startRecording}
                      disabled={!serviceStatus?.available || isConnecting}
                      className="w-20 h-20 rounded-full bg-gradient-to-r from-red-500 to-rose-600 hover:from-red-600 hover:to-rose-700 shadow-lg shadow-red-500/30"
                      data-testid="start-recording-btn"
                    >
                      {isConnecting ? (
                        <Loader2 className="w-10 h-10 animate-spin" />
                      ) : (
                        <Mic className="w-10 h-10" />
                      )}
                    </Button>
                  ) : (
                    <Button
                      size="lg"
                      onClick={stopRecording}
                      className="w-20 h-20 rounded-full bg-slate-800 hover:bg-slate-700 animate-pulse"
                      data-testid="stop-recording-btn"
                    >
                      <MicOff className="w-10 h-10" />
                    </Button>
                  )}
                </div>

                <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
                  {isRecording 
                    ? 'Recording... Click to stop' 
                    : isConnecting 
                      ? 'Connecting...' 
                      : 'Click to start recording'}
                </p>

                {/* Mode indicator */}
                <div className="mt-4 flex items-center justify-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    <Sparkles className="w-3 h-3 mr-1" />
                    {useWebSocket ? 'Real-time streaming' : 'Batch mode'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Transcript Output */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <FileText className="w-5 h-5 text-turquoise" />
                  Transcript
                </CardTitle>
                {transcript && (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => copyToClipboard(transcript)}>
                      <Copy className="w-4 h-4 mr-1" /> Copy
                    </Button>
                    <Button variant="outline" size="sm" onClick={downloadTranscript}>
                      <Download className="w-4 h-4 mr-1" /> Download
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => { setTranscript(''); setInterimTranscript(''); }}>
                      <RotateCcw className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="min-h-[200px] p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                {transcript || interimTranscript ? (
                  <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                    {transcript}
                    <span className="text-slate-400 dark:text-slate-500 italic">
                      {interimTranscript}
                    </span>
                  </p>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-400 dark:text-slate-500">
                    <div className="text-center">
                      <Volume2 className="w-12 h-12 mx-auto mb-3 opacity-40" />
                      <p>Your transcription will appear here...</p>
                    </div>
                  </div>
                )}
              </div>

              {transcript && (
                <div className="mt-4 flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
                  <span>{transcript.split(' ').filter(Boolean).length} words</span>
                  <span>{transcript.length} characters</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Settings & History Panel */}
        <div className="space-y-6">
          {/* Language Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Languages className="w-5 h-5 text-violet-500" />
                Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2 block">
                  Language
                </label>
                <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SUPPORTED_LANGUAGES.map(lang => (
                      <SelectItem key={lang.code} value={lang.code}>
                        {lang.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="pt-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600 dark:text-slate-400">Model</span>
                  <Badge variant="outline">Whisper-1</Badge>
                </div>
              </div>

              {serviceStatus?.features && (
                <div className="pt-2 space-y-2">
                  <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                    Features
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(serviceStatus.features)
                      .filter(([_, v]) => v === true)
                      .map(([key]) => (
                        <Badge key={key} variant="secondary" className="text-xs">
                          {key.replace('_', ' ')}
                        </Badge>
                      ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* History */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <History className="w-5 h-5 text-amber-500" />
                  History
                </CardTitle>
                <Badge variant="outline">{history.length}</Badge>
              </div>
              <CardDescription>Recent transcriptions</CardDescription>
            </CardHeader>
            <CardContent>
              {history.length > 0 ? (
                <div className="space-y-3 max-h-[400px] overflow-y-auto">
                  {history.slice(0, 10).map(item => (
                    <TranscriptionItem 
                      key={item.id} 
                      item={item}
                      onDelete={deleteFromHistory}
                      onCopy={copyToClipboard}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400 dark:text-slate-500">
                  <History className="w-10 h-10 mx-auto mb-3 opacity-40" />
                  <p className="text-sm">No transcriptions yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Tips Section */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="text-lg" style={{ fontFamily: 'IBM Plex Sans' }}>
            Tips for Better Transcription
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { icon: Mic, title: 'Speak Clearly', desc: 'Enunciate words and maintain consistent volume' },
              { icon: Volume2, title: 'Reduce Background Noise', desc: 'Use a quiet environment for best results' },
              { icon: Globe, title: 'Match Language', desc: 'Select the correct language for accurate transcription' },
              { icon: Clock, title: 'Natural Pace', desc: 'Speak at a normal conversational speed' }
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

export default RealTimeSTTPage;
