import { useCallback } from 'react';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export function useWebinarActions(webinarId, navigate, fetchRoomInfo) {
  const apiPost = useCallback(async (path) => {
    const token = localStorage.getItem('token');
    return fetch(`${API}/api/karau/webinar/${webinarId}${path}`, {
      method: 'POST', headers: { 'Authorization': `Bearer ${token}` }
    });
  }, [webinarId]);

  const apiPostJson = useCallback(async (path, body) => {
    const token = localStorage.getItem('token');
    return fetch(`${API}/api/karau/webinar/${webinarId}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(body)
    });
  }, [webinarId]);

  const toggleHandRaise = useCallback(async (isRaised) => {
    await apiPost(isRaised ? '/hand-lower' : '/hand-raise');
  }, [apiPost]);

  const promoteUser = useCallback(async (userId, role) => {
    const res = await apiPostJson('/roles/promote', { user_id: userId, role });
    if (res.ok) { toast.success(`Promoted to ${role}`); fetchRoomInfo(); }
  }, [apiPostJson, fetchRoomInfo]);

  const demoteUser = useCallback(async (userId) => {
    const res = await apiPostJson('/roles/demote', { user_id: userId });
    if (res.ok) { toast.success('Demoted'); fetchRoomInfo(); }
  }, [apiPostJson, fetchRoomInfo]);

  const startWebinar = useCallback(async () => {
    const r = await apiPost('/start');
    if (r.ok) { toast.success('LIVE!'); fetchRoomInfo(); }
  }, [apiPost, fetchRoomInfo]);

  const endWebinar = useCallback(async () => {
    const r = await apiPost('/end');
    if (r.ok) { toast.success('Ended'); navigate('/karau-meet/webinars'); }
  }, [apiPost, navigate]);

  const startPractice = useCallback(async () => {
    const r = await apiPost('/practice/start');
    if (r.ok) { toast.success('Practice started'); fetchRoomInfo(); }
  }, [apiPost, fetchRoomInfo]);

  const endPractice = useCallback(async () => {
    const r = await apiPost('/practice/end');
    if (r.ok) { toast.success('Practice ended'); fetchRoomInfo(); }
  }, [apiPost, fetchRoomInfo]);

  const muteAll = useCallback(async () => {
    await apiPost('/controls/mute-all');
    toast.success('All muted');
  }, [apiPost]);

  const submitQuestion = useCallback(async (question) => {
    const res = await apiPostJson('/qa/ask', { question, is_anonymous: false });
    return res.ok;
  }, [apiPostJson]);

  const answerQuestion = useCallback(async (qId, answer) => {
    const res = await apiPostJson(`/qa/${qId}/answer`, { answer });
    return res.ok;
  }, [apiPostJson]);

  const upvoteQuestion = useCallback(async (qId) => {
    await apiPost(`/qa/${qId}/upvote`);
  }, [apiPost]);

  const fetchQA = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/qa`);
      if (res.ok) return (await res.json()).questions || [];
    } catch {}
    return null;
  }, [webinarId]);

  const fetchHandRaises = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/hand-raises`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) return (await res.json()).hand_raises || [];
    } catch {}
    return null;
  }, [webinarId]);

  const saveTranscript = useCallback(async (transcript) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/live-transcript/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ transcript })
      });
      if (res.ok) toast.success('Transcript saved');
      else toast.error('Failed to save transcript');
    } catch { toast.error('Save error'); }
  }, [webinarId]);

  const grantGuestPermission = useCallback(async (userId, permission) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/guest-permission/grant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ user_id: userId, permission })
      });
      if (res.ok) toast.success(`${permission} permission granted`);
      else toast.error('Failed to grant permission');
    } catch { toast.error('Permission error'); }
  }, [webinarId]);

  const revokeGuestPermission = useCallback(async (userId) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/webinar/${webinarId}/guest-permission/revoke`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ user_id: userId, permission: '' })
      });
      if (res.ok) toast.success('Permission revoked');
    } catch { toast.error('Revoke error'); }
  }, [webinarId]);

  return {
    toggleHandRaise, promoteUser, demoteUser,
    startWebinar, endWebinar, startPractice, endPractice, muteAll,
    submitQuestion, answerQuestion, upvoteQuestion,
    fetchQA, fetchHandRaises, saveTranscript,
    grantGuestPermission, revokeGuestPermission,
  };
}
