/**
import { useTranslation } from "@/utils/i18n";
 * Voice Search Component
 * 
 * Features:
 * - Web Speech API for voice recognition
 * - Real-time transcription display
 * - Automatic search on speech end
 * - Visual feedback during recording
 * - Mobile-friendly with touch support
 * - Fallback for unsupported browsers
 */

import React, { useState, useEffect, useCallback, useRef, memo } from 'react';
import { Mic, MicOff, Loader2, X, Volume2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

// Check for browser support
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const isSpeechSupported = !!SpeechRecognition;

// ============== Voice Search Button ==============
export const VoiceSearchButton = memo(({ 
  onResult, 
  onInterimResult,
  className = "",
  size = "default",
  variant = "outline",
  disabled = false,
  language = "en-US",
  continuous = false,
  "data-testid": testId
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const recognitionRef = useRef(null);

  // Initialize speech recognition
  useEffect(() => {
    if (!isSpeechSupported) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.lang = language;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setIsProcessing(false);
    };

    recognition.onend = () => {
      setIsListening(false);
      setIsProcessing(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      setIsProcessing(false);
      
      if (event.error === 'not-allowed') {
        toast.error('Microphone access denied. Please enable microphone permissions.');
      } else if (event.error === 'no-speech') {
        toast.info('No speech detected. Please try again.');
      } else if (event.error !== 'aborted') {
        toast.error(`Voice recognition error: ${event.error}`);
      }
    };

    recognition.onresult = (event) => {
      const lastResult = event.results[event.results.length - 1];
      const transcript = lastResult[0].transcript;
      
      if (lastResult.isFinal) {
        setIsProcessing(true);
        onResult?.(transcript.trim());
        setIsProcessing(false);
      } else {
        onInterimResult?.(transcript);
      }
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [language, continuous, onResult, onInterimResult]);

  const toggleListening = useCallback(() => {
    if (!isSpeechSupported) {
      toast.error('Voice search is not supported in your browser. Please try Chrome or Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      try {
        recognitionRef.current?.start();
      } catch (error) {
        console.error('Failed to start speech recognition:', error);
        toast.error('Failed to start voice recognition. Please try again.');
      }
    }
  }, [isListening]);

  const sizeClasses = {
    sm: "h-8 w-8",
    default: "h-10 w-10",
    lg: "h-12 w-12"
  };

  const iconSizes = {
    sm: "w-4 h-4",
    default: "w-5 h-5",
    lg: "w-6 h-6"
  };

  if (!isSpeechSupported) {
    return (
      <Button
        variant={variant}
        size="icon"
        className={`${sizeClasses[size]} ${className} opacity-50 cursor-not-allowed`}
        disabled
        title="Voice search not supported in this browser"
        data-testid={testId}
      >
        <MicOff className={iconSizes[size]} />
      </Button>
    );
  }

  return (
    <Button
      variant={isListening ? "destructive" : variant}
      size="icon"
      className={`${sizeClasses[size]} ${className} ${isListening ? 'animate-pulse' : ''}`}
      onClick={toggleListening}
      disabled={disabled || isProcessing}
      title={isListening ? "Stop listening" : "Start voice search"}
      data-testid={testId}
    >
      {isProcessing ? (
        <Loader2 className={`${iconSizes[size]} animate-spin`} />
      ) : isListening ? (
        <MicOff className={iconSizes[size]} />
      ) : (
        <Mic className={iconSizes[size]} />
      )}
    </Button>
  );
});

// ============== Voice Search Modal ==============
export const VoiceSearchModal = memo(({
  isOpen,
  onClose,
  onResult,
  language = "en-US"
}) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (!isOpen || !isSpeechSupported) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      
      if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please enable permissions in your browser settings.');
      } else if (event.error === 'no-speech') {
        setError('No speech detected. Please try speaking again.');
      } else if (event.error !== 'aborted') {
        setError(`Error: ${event.error}`);
      }
    };

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interim = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interim += result[0].transcript;
        }
      }

      if (finalTranscript) {
        setTranscript(prev => prev + finalTranscript);
        setInterimTranscript('');
        
        // Auto-submit after 2 seconds of silence
        clearTimeout(timeoutRef.current);
        timeoutRef.current = setTimeout(() => {
          const fullTranscript = transcript + finalTranscript;
          if (fullTranscript.trim()) {
            onResult?.(fullTranscript.trim());
            handleClose();
          }
        }, 2000);
      } else {
        setInterimTranscript(interim);
      }
    };

    recognitionRef.current = recognition;

    // Auto-start when modal opens
    try {
      recognition.start();
    } catch (e) {
      console.error('Failed to start recognition:', e);
    }

    return () => {
      clearTimeout(timeoutRef.current);
      recognition.abort();
    };
  }, [isOpen, language]);

  const handleClose = useCallback(() => {
    clearTimeout(timeoutRef.current);
    recognitionRef.current?.abort();
    setTranscript('');
    setInterimTranscript('');
    setError(null);
    onClose?.();
  }, [onClose]);

  const handleSubmit = useCallback(() => {
    const fullTranscript = (transcript + interimTranscript).trim();
    if (fullTranscript) {
      onResult?.(fullTranscript);
      handleClose();
    }
  }, [transcript, interimTranscript, onResult, handleClose]);

  const handleRetry = useCallback(() => {
    setError(null);
    setTranscript('');
    setInterimTranscript('');
    try {
      recognitionRef.current?.start();
    } catch (e) {
      console.error('Failed to restart recognition:', e);
    }
  }, []);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Voice Search</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Microphone Animation */}
        <div className="flex justify-center mb-6">
          <div className={`relative ${isListening ? 'animate-pulse' : ''}`}>
            {/* Ripple effects */}
            {isListening && (
              <>
                <div className="absolute inset-0 rounded-full bg-teal-500/20 animate-ping" style={{ animationDuration: '1.5s' }} />
                <div className="absolute inset-2 rounded-full bg-teal-500/30 animate-ping" style={{ animationDuration: '1.5s', animationDelay: '0.3s' }} />
              </>
            )}
            
            {/* Mic button */}
            <div className={`relative w-24 h-24 rounded-full flex items-center justify-center ${
              isListening 
                ? 'bg-teal-500 text-white' 
                : error 
                  ? 'bg-red-100 text-red-500 dark:bg-red-900/30' 
                  : 'bg-gray-100 text-gray-400 dark:bg-gray-700'
            }`}>
              {error ? (
                <AlertCircle className="w-10 h-10" />
              ) : (
                <Mic className="w-10 h-10" />
              )}
            </div>
          </div>
        </div>

        {/* Status Text */}
        <div className="text-center mb-6">
          {error ? (
            <p className="text-red-500 text-sm">{error}</p>
          ) : isListening ? (
            <p className="text-teal-600 dark:text-teal-400 font-medium">Listening...</p>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">Tap the mic to start</p>
          )}
        </div>

        {/* Transcript Display */}
        <div className="min-h-[80px] bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
          {transcript || interimTranscript ? (
            <p className="text-gray-900 dark:text-white">
              {transcript}
              <span className="text-gray-400">{interimTranscript}</span>
            </p>
          ) : (
            <p className="text-gray-400 dark:text-gray-500 italic">
              Say something like "Find quality engineer jobs in Boston"...
            </p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          {error ? (
            <Button onClick={handleRetry} className="flex-1 bg-teal-500 hover:bg-teal-600">
              Try Again
            </Button>
          ) : (
            <>
              <Button 
                variant="outline" 
                onClick={handleClose}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleSubmit}
                disabled={!transcript && !interimTranscript}
                className="flex-1 bg-teal-500 hover:bg-teal-600"
              >
                Search
              </Button>
            </>
          )}
        </div>

        {/* Hint */}
        <p className="text-xs text-gray-400 text-center mt-4">
          Speak naturally. Search will auto-submit after you stop speaking.
        </p>
      </div>
    </div>
  );
});

// ============== Voice Search with Intent Display ==============
export const VoiceSearchWithIntent = memo(({
  onSearch,
  placeholder = "Try: 'Remote software engineer in San Francisco'",
  className = ""
}) => {
  const [showModal, setShowModal] = useState(false);
  const [lastQuery, setLastQuery] = useState('');
  const [intent, setIntent] = useState(null);

  const handleResult = useCallback(async (transcript) => {
    setLastQuery(transcript);
    
    // Fetch intent from backend
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/search/intent?q=${encodeURIComponent(transcript)}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      const data = await response.json();
      setIntent(data.intent);
    } catch (error) {
      console.error('Failed to extract intent:', error);
    }
    
    // Trigger search
    onSearch?.(transcript);
  }, [onSearch]);

  return (
    <div className={className}>
      {/* Voice Search Trigger */}
      <div className="flex items-center gap-2">
        <Button
          onClick={() => setShowModal(true)}
          variant="outline"
          className="flex items-center gap-2"
          data-testid="voice-search-trigger"
        >
          <Mic className="w-5 h-5 text-teal-500" />
          <span className="hidden sm:inline">Voice Search</span>
        </Button>
        
        {lastQuery && (
          <span className="text-sm text-gray-500 truncate max-w-xs">
            Last: "{lastQuery}"
          </span>
        )}
      </div>

      {/* Intent Display */}
      {intent && (
        <div className="mt-3 p-3 bg-teal-50 dark:bg-teal-900/20 rounded-lg text-sm">
          <p className="font-medium text-teal-700 dark:text-teal-300 mb-1">Understood:</p>
          <div className="flex flex-wrap gap-2">
            {intent.job_title && (
              <span className="px-2 py-1 bg-white dark:bg-gray-800 rounded text-gray-700 dark:text-gray-300">
                🎯 {intent.job_title}
              </span>
            )}
            {intent.location && (
              <span className="px-2 py-1 bg-white dark:bg-gray-800 rounded text-gray-700 dark:text-gray-300">
                📍 {intent.location}
              </span>
            )}
            {intent.job_type && (
              <span className="px-2 py-1 bg-white dark:bg-gray-800 rounded text-gray-700 dark:text-gray-300">
                🏢 {intent.job_type}
              </span>
            )}
            {intent.experience_level && (
              <span className="px-2 py-1 bg-white dark:bg-gray-800 rounded text-gray-700 dark:text-gray-300">
                📊 {intent.experience_level}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Modal */}
      <VoiceSearchModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onResult={handleResult}
      />
    </div>
  );
});

// Display names
VoiceSearchButton.displayName = 'VoiceSearchButton';
VoiceSearchModal.displayName = 'VoiceSearchModal';
VoiceSearchWithIntent.displayName = 'VoiceSearchWithIntent';

export default VoiceSearchButton;
