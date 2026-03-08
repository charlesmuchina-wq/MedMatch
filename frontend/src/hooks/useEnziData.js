/**
 * useEnziData - Custom hook for ENZI data loading
 * Extracts data fetching logic from LumiMessenger.jsx
 */
import { useState, useCallback } from 'react';
import { API } from '@/components/Lumi/constants';

export const useEnziData = (token) => {
  const [channels, setChannels] = useState([]);
  const [discoverChannels, setDiscoverChannels] = useState([]);
  const [dms, setDms] = useState([]);
  const [unreadCounts, setUnreadCounts] = useState({});
  const [presenceMap, setPresenceMap] = useState({});
  const [pendingInvites, setPendingInvites] = useState([]);
  const [bucketCounts, setBucketCounts] = useState({ urgent: 0, action_required: 0, meeting_request: 0, fyi: 0, social: 0 });
  const [calendarStatus, setCalendarStatus] = useState({ status: 'available', source: 'manual', calendar_event: null, microsoft_linked: false });
  const [predictions, setPredictions] = useState({ channels: [], dms: [] });
  const [domainColleagues, setDomainColleagues] = useState([]);

  const loadChannels = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/channels`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        const data = await res.json();
        setChannels(data.my_channels || []);
        setDiscoverChannels(data.discover || []);
        if ((data.my_channels || []).length === 0 && (data.discover || []).length === 0) {
          await fetch(`${API}/api/lumi/seed`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
          await fetch(`${API}/api/lumi/domain/auto-channel`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
          const r2 = await fetch(`${API}/api/lumi/channels`, { headers: { Authorization: `Bearer ${token}` } });
          if (r2.ok) { const d2 = await r2.json(); setChannels(d2.my_channels || []); setDiscoverChannels(d2.discover || []); }
        }
      }
    } catch {}
  }, [token]);

  const loadDms = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/dm`, { headers: { Authorization: `Bearer ${token}` } }); if (res.ok) setDms((await res.json()).dms || []); } catch {}
  }, [token]);

  const loadUnreadCounts = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/unread-counts`, { headers: { Authorization: `Bearer ${token}` } }); if (res.ok) setUnreadCounts((await res.json()).unread || {}); } catch {}
  }, [token]);

  const loadPresence = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/presence/all`, { headers: { Authorization: `Bearer ${token}` } }); if (res.ok) setPresenceMap((await res.json()).presence || {}); } catch {}
  }, [token]);

  const loadInvites = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/invites`, { headers: { Authorization: `Bearer ${token}` } }); if (res.ok) setPendingInvites((await res.json()).invites || []); } catch {}
  }, [token]);

  const loadBucketCounts = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/buckets/counts`, { headers: { Authorization: `Bearer ${token}` } }); if (res.ok) setBucketCounts((await res.json()).counts || {}); } catch {}
  }, [token]);

  const scanAndLoadBuckets = useCallback(async () => {
    if (!token) return;
    try { await fetch(`${API}/api/lumi/buckets/scan`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } }); loadBucketCounts(); } catch {}
  }, [token, loadBucketCounts]);

  const loadCalendarStatus = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/calendar/status`, { headers: { Authorization: `Bearer ${token}` } }); if (res.ok) setCalendarStatus(await res.json()); } catch {}
  }, [token]);

  const loadPredictions = useCallback(async () => {
    if (!token) return;
    try { const res = await fetch(`${API}/api/lumi/predict/suggestions`, { headers: { Authorization: `Bearer ${token}` } }); if (res.ok) setPredictions(await res.json()); } catch {}
  }, [token]);

  const loadDomainColleagues = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/lumi/domain/colleagues`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) { const data = await res.json(); if (data.is_company_domain) setDomainColleagues(data.colleagues || []); }
    } catch {}
  }, [token]);

  const trackAction = async (action, targetId, targetName) => {
    if (!token) return;
    fetch(`${API}/api/lumi/predict/track`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ action, target_id: targetId, target_name: targetName })
    }).catch(() => {});
  };

  const loadAll = () => {
    loadChannels(); loadDms(); loadUnreadCounts(); loadPresence();
    loadInvites(); scanAndLoadBuckets(); loadCalendarStatus();
    loadPredictions(); loadDomainColleagues();
  };

  return {
    channels, setChannels, discoverChannels, dms, setDms,
    unreadCounts, setUnreadCounts, presenceMap, setPresenceMap,
    pendingInvites, bucketCounts, calendarStatus, predictions,
    domainColleagues, loadChannels, loadDms, loadUnreadCounts,
    loadPresence, loadAll, trackAction, scanAndLoadBuckets,
    loadBucketCounts, loadCalendarStatus, loadPredictions,
    loadInvites,
  };
};
