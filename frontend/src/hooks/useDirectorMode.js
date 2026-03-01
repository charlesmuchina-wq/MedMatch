import { useState, useEffect, useRef, useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Hook for Cinematic Director Mode
 * AI auto-switches between panoramic, speaker close-up, and conversation views
 */
export function useDirectorMode(meetingId, speakerDetection, remoteStreams) {
  const [mode, setMode] = useState('auto'); // auto, panoramic, speaker_closeup, conversation, manual
  const [recommendedView, setRecommendedView] = useState('panoramic');
  const [focusUsers, setFocusUsers] = useState([]);
  const [enabled, setEnabled] = useState(true);
  const analyzeInterval = useRef(null);
  const speakingHistory = useRef([]);

  // Track speaking events for analysis
  useEffect(() => {
    if (!speakerDetection?.speakers) return;

    const events = Object.entries(speakerDetection.speakers)
      .filter(([uid]) => uid !== '__local__')
      .map(([uid, info]) => ({
        user_id: uid,
        user_name: info.name || uid,
        is_speaking: info.speaking || false,
        duration_seconds: info.speaking ? 2.0 : 0
      }));

    speakingHistory.current = events;
  }, [speakerDetection?.speakers]);

  // Periodically analyze and recommend view
  useEffect(() => {
    if (!meetingId || !enabled || mode !== 'auto') return;

    const analyze = async () => {
      const events = speakingHistory.current;
      if (events.length === 0) return;

      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/karau/director/${meetingId}/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({
            meeting_id: meetingId,
            speaking_events: events,
            participant_count: Object.keys(remoteStreams || {}).length + 1,
            elapsed_seconds: 0
          })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.should_switch) {
            setRecommendedView(data.recommended_view);
            setFocusUsers(data.focus_users || []);
          }
        }
      } catch {}
    };

    analyzeInterval.current = setInterval(analyze, 3000);
    return () => { if (analyzeInterval.current) clearInterval(analyzeInterval.current); };
  }, [meetingId, enabled, mode, remoteStreams]);

  const setDirectorMode = useCallback(async (newMode) => {
    setMode(newMode);
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau/director/${meetingId}/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ mode: newMode })
      });
    } catch {}
  }, [meetingId]);

  const toggle = useCallback(() => {
    setEnabled(prev => !prev);
  }, []);

  // Determine what the active view should be
  const activeView = mode === 'auto' ? recommendedView : mode;

  return {
    mode,
    activeView,
    focusUsers,
    enabled,
    setDirectorMode,
    toggle,
    recommendedView
  };
}
