import { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Captions, CaptionsOff, Circle } from 'lucide-react';

/**
 * Live Captions component using Web Speech API
 * Provides real-time speech-to-text captions overlay
 */
const LiveCaptions = ({ isEnabled, onTranscriptUpdate, onToggle }) => {
  const [caption, setCaption] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const transcriptRef = useRef([]);
  const restartTimeoutRef = useRef(null);

  const startRecognition = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch {}
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if (final) {
        const segment = {
          speaker: 'You',
          text: final.trim(),
          timestamp: new Date().toISOString()
        };
        transcriptRef.current.push(segment);
        onTranscriptUpdate?.(segment);
        setCaption(final.trim());
      } else if (interim) {
        setCaption(interim);
      }
    };

    recognition.onerror = (event) => {
      if (event.error === 'no-speech' || event.error === 'aborted') {
        // Auto-restart on these non-fatal errors
        if (isEnabled) {
          restartTimeoutRef.current = setTimeout(startRecognition, 300);
        }
        return;
      }
      console.warn('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      // Auto-restart if still enabled
      if (isEnabled) {
        restartTimeoutRef.current = setTimeout(startRecognition, 300);
      }
    };

    recognitionRef.current = recognition;
    try { recognition.start(); } catch {}
  }, [isEnabled, onTranscriptUpdate]);

  useEffect(() => {
    if (isEnabled) {
      startRecognition();
    } else {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
      clearTimeout(restartTimeoutRef.current);
      setIsListening(false);
      setCaption('');
    }
    return () => {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
      clearTimeout(restartTimeoutRef.current);
    };
  }, [isEnabled, startRecognition]);

  // Get full transcript for summary generation
  const getFullTranscript = useCallback(() => transcriptRef.current, []);

  // Expose getFullTranscript
  useEffect(() => {
    if (window) window.__karauGetTranscript = getFullTranscript;
    return () => { if (window) delete window.__karauGetTranscript; };
  }, [getFullTranscript]);

  if (!isEnabled) return null;

  return (
    <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-30 max-w-[80%] pointer-events-none" data-testid="live-captions">
      {caption && (
        <div className="bg-black/80 backdrop-blur-sm rounded-lg px-4 py-2 text-center animate-in fade-in duration-200">
          <div className="flex items-center justify-center gap-2 mb-1">
            {isListening && (
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-[10px] px-1.5 py-0">
                <Circle className="w-1.5 h-1.5 mr-1 fill-current animate-pulse" />
                LIVE
              </Badge>
            )}
          </div>
          <p className="text-white text-sm md:text-base font-medium leading-relaxed">
            {caption}
          </p>
        </div>
      )}
    </div>
  );
};

/**
 * Captions toggle button for the control bar
 */
export const CaptionsButton = ({ isEnabled, onToggle }) => (
  <Button
    variant={isEnabled ? 'default' : 'secondary'}
    size="lg"
    className={`rounded-full w-12 h-12 ${isEnabled ? 'bg-turquoise' : ''}`}
    onClick={onToggle}
    title={isEnabled ? 'Disable Captions' : 'Enable Captions'}
    data-testid="control-captions"
  >
    {isEnabled ? <Captions className="w-5 h-5" /> : <CaptionsOff className="w-5 h-5" />}
  </Button>
);

export default LiveCaptions;
