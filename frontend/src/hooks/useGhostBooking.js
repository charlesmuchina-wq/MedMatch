import { useState, useEffect, useRef, useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Hook for Ghost Booking Prevention
 * Sends activity pings and monitors for idle meetings
 */
export function useGhostBooking(meetingId) {
  const [ghostStatus, setGhostStatus] = useState(null);
  const [showWarning, setShowWarning] = useState(false);
  const pingInterval = useRef(null);
  const checkInterval = useRef(null);

  // Send activity pings every 60 seconds
  useEffect(() => {
    if (!meetingId) return;

    const ping = async () => {
      const token = localStorage.getItem('token');
      try {
        await fetch(`${API}/api/karau-meet/ghost/ping`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ meeting_id: meetingId, activity_type: 'presence' })
        });
      } catch {}
    };

    ping(); // Initial ping
    pingInterval.current = setInterval(ping, 60000);
    return () => { if (pingInterval.current) clearInterval(pingInterval.current); };
  }, [meetingId]);

  // Check ghost status every 2 minutes
  useEffect(() => {
    if (!meetingId) return;

    const check = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/api/karau-meet/ghost/check/${meetingId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setGhostStatus(data);
          setShowWarning(data.approaching_idle || data.is_idle);
        }
      } catch {}
    };

    check();
    checkInterval.current = setInterval(check, 120000);
    return () => { if (checkInterval.current) clearInterval(checkInterval.current); };
  }, [meetingId]);

  const keepAlive = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau-meet/ghost/keep/${meetingId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setShowWarning(false);
    } catch {}
  }, [meetingId]);

  const releaseMeeting = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API}/api/karau-meet/ghost/release/${meetingId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setShowWarning(false);
    } catch {}
  }, [meetingId]);

  return {
    ghostStatus,
    showWarning,
    keepAlive,
    releaseMeeting
  };
}
