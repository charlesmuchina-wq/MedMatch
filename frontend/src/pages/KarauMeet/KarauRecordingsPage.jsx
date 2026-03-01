import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Video, Clock, Archive, X, Loader2, Cloud, HardDrive,
  Download, CloudUpload, CheckCircle2, FileText, ChevronDown, ChevronUp,
  Sparkles, Send, Copy, Mail
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

const KarauRecordingsPage = () => {
  const { t } = useTranslation();
  const [recordings, setRecordings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);
  const [expandedTranscript, setExpandedTranscript] = useState(null);
  const [transcriptData, setTranscriptData] = useState({});
  const [generatingNotes, setGeneratingNotes] = useState(null);
  const [notesData, setNotesData] = useState({});
  const [expandedNotes, setExpandedNotes] = useState(null);
  const [sendingNotes, setSendingNotes] = useState(null);
  const [sendEmail, setSendEmail] = useState('');

  useEffect(() => { fetchRecordings(); }, []);

  const fetchRecordings = async () => {
    const token = localStorage.getItem('token');
    try {
      const [recordingsRes, statsRes] = await Promise.all([
        fetch(`${API}/api/karau-meet/recordings/`, { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch(`${API}/api/karau-meet/recordings/stats`, { headers: { 'Authorization': `Bearer ${token}` } })
      ]);
      if (recordingsRes.ok) {
        const data = await recordingsRes.json();
        setRecordings(data.recordings || []);
      }
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (error) { console.error('Error fetching recordings:', error); }
    setLoading(false);
  };

  const formatDuration = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) return `${hrs}h ${mins}m`;
    if (mins > 0) return `${mins}m ${secs}s`;
    return `${secs}s`;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  };

  const downloadRecording = async (rec) => {
    if (rec.storage_type !== 'cloud') return;
    setDownloadingId(rec.recording_id);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/download/${rec.recording_id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = rec.file_name || 'recording.webm';
        a.click();
        URL.revokeObjectURL(url);
        toast.success(t("karauMeet.downloadStarted") || 'Download started');
      } else {
        toast.error('Download failed');
      }
    } catch { toast.error('Download error'); }
    setDownloadingId(null);
  };

  const deleteRecording = async (recordingId) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/${recordingId}`, {
        method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setRecordings(prev => prev.filter(r => r.recording_id !== recordingId));
        toast.success(t("karauMeet.recordingDeleted") || 'Recording deleted');
      }
    } catch { toast.error('Failed to delete'); }
  };

  const toggleTranscript = async (recordingId) => {
    if (expandedTranscript === recordingId) {
      setExpandedTranscript(null);
      return;
    }
    setExpandedTranscript(recordingId);
    if (transcriptData[recordingId]) return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/transcript/${recordingId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setTranscriptData(prev => ({ ...prev, [recordingId]: data }));
      }
    } catch {}
  };

  const generateNotes = async (recordingId) => {
    setGeneratingNotes(recordingId);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/${recordingId}/notes/generate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setNotesData(prev => ({ ...prev, [recordingId]: data.notes }));
        setExpandedNotes(recordingId);
        toast.success('AI notes generated');
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Failed to generate notes');
      }
    } catch { toast.error('Notes generation error'); }
    setGeneratingNotes(null);
  };

  const fetchNotes = async (recordingId) => {
    if (notesData[recordingId]) {
      setExpandedNotes(expandedNotes === recordingId ? null : recordingId);
      return;
    }
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/${recordingId}/notes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.notes) {
          setNotesData(prev => ({ ...prev, [recordingId]: data.notes }));
          setExpandedNotes(recordingId);
        }
      }
    } catch {}
  };

  const sendNotes = async (recordingId) => {
    if (!sendEmail.trim()) return;
    setSendingNotes(recordingId);
    const token = localStorage.getItem('token');
    const emails = sendEmail.split(',').map(e => e.trim()).filter(Boolean);
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/${recordingId}/notes/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ recipient_emails: emails })
      });
      if (res.ok) {
        toast.success(`Notes sent to ${emails.length} recipient(s)`);
        setSendEmail('');
        setSendingNotes(null);
      } else {
        toast.error('Failed to send notes');
      }
    } catch { toast.error('Send error'); }
    setSendingNotes(null);
  };

  const copyNotes = (recordingId) => {
    const notes = notesData[recordingId]?.notes;
    if (notes) {
      navigator.clipboard.writeText(notes);
      toast.success('Notes copied to clipboard');
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 space-y-5 max-w-5xl" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <div>
        <h1 className="text-xl font-bold text-white" data-testid="recordings-title">
          {t("karauMeet.recordingsTitle") || "Recordings"}
        </h1>
        <p className="text-xs text-karau-muted mt-0.5">{t("karauMeet.recordingsSubtitle") || "Your meeting recordings"}</p>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="rounded-xl border border-white/5 bg-karau-card/40 p-3">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-violet-500/15 flex items-center justify-center">
                <Video className="w-4 h-4 text-violet-400" />
              </div>
              <div>
                <p className="text-lg font-bold text-white" data-testid="stat-total">{stats.total_recordings}</p>
                <p className="text-[10px] text-karau-muted">{t("karauMeet.totalRecordings") || "Total"}</p>
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-white/5 bg-karau-card/40 p-3">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-emerald-500/15 flex items-center justify-center">
                <Clock className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <p className="text-lg font-bold text-white" data-testid="stat-duration">{formatDuration(stats.total_duration_seconds)}</p>
                <p className="text-[10px] text-karau-muted">{t("karauMeet.totalDuration") || "Duration"}</p>
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-white/5 bg-karau-card/40 p-3">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-blue-500/15 flex items-center justify-center">
                <Cloud className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <p className="text-lg font-bold text-white" data-testid="stat-cloud">{stats.cloud_count || 0}</p>
                <p className="text-[10px] text-karau-muted">{t("karauMeet.cloudRecordings") || "Cloud"}</p>
              </div>
            </div>
          </div>
          <div className="rounded-xl border border-white/5 bg-karau-card/40 p-3">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-amber-500/15 flex items-center justify-center">
                <Archive className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <p className="text-lg font-bold text-white" data-testid="stat-size">{formatFileSize(stats.total_size_bytes)}</p>
                <p className="text-[10px] text-karau-muted">{t("karauMeet.storageUsed") || "Storage"}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-white/5 bg-karau-card/40">
        <div className="px-4 py-3 border-b border-white/5">
          <h2 className="text-sm font-semibold text-white">{t("karauMeet.yourRecordings") || "Your Recordings"}</h2>
        </div>
        <div className="p-3">
          {recordings.length === 0 ? (
            <div className="text-center py-10" data-testid="no-recordings">
              <Video className="w-10 h-10 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-karau-muted">{t("karauMeet.noRecordingsYet") || "No recordings yet"}</p>
              <p className="text-[10px] text-slate-600 mt-0.5">{t("karauMeet.startRecordingHint") || "Start recording in a meeting to see them here"}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {recordings.map((rec) => (
                <div key={rec.recording_id} data-testid={`recording-${rec.recording_id}`}>
                  <div className="flex items-center justify-between p-3 bg-karau-bg/40 rounded-xl hover:bg-karau-surface/40 transition-colors group">
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                        rec.storage_type === 'cloud' ? 'bg-blue-500/15' : 'bg-violet-500/15'
                      }`}>
                        {rec.storage_type === 'cloud'
                          ? <Cloud className="w-5 h-5 text-blue-400" />
                          : <HardDrive className="w-5 h-5 text-violet-400" />}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-white truncate">{rec.meeting_title}</p>
                        <div className="flex items-center gap-2 text-[10px] text-karau-muted mt-0.5">
                          <span>{new Date(rec.recorded_at).toLocaleDateString()}</span>
                          <span>&middot;</span>
                          <span>{formatDuration(rec.duration_seconds)}</span>
                          <span>&middot;</span>
                          <span>{formatFileSize(rec.file_size_bytes)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 ml-2">
                      {/* Transcription status */}
                      {rec.transcription_status === 'completed' && (
                        <Button variant="ghost" size="sm" onClick={() => toggleTranscript(rec.recording_id)}
                          className="h-7 px-1.5 text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10"
                          data-testid={`transcript-${rec.recording_id}`}>
                          <FileText className="w-3.5 h-3.5 mr-0.5" />
                          {expandedTranscript === rec.recording_id ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                        </Button>
                      )}
                      {rec.transcription_status === 'completed' && (
                        notesData[rec.recording_id] ? (
                          <Button variant="ghost" size="sm" onClick={() => fetchNotes(rec.recording_id)}
                            className="h-7 px-1.5 text-violet-400 hover:text-violet-300 hover:bg-violet-500/10"
                            data-testid={`view-notes-${rec.recording_id}`}>
                            <Sparkles className="w-3.5 h-3.5 mr-0.5" />Notes
                          </Button>
                        ) : (
                          <Button variant="ghost" size="sm" onClick={() => generateNotes(rec.recording_id)}
                            disabled={generatingNotes === rec.recording_id}
                            className="h-7 px-1.5 text-amber-400 hover:text-amber-300 hover:bg-amber-500/10"
                            data-testid={`generate-notes-${rec.recording_id}`}>
                            {generatingNotes === rec.recording_id
                              ? <Loader2 className="w-3.5 h-3.5 mr-0.5 animate-spin" />
                              : <Sparkles className="w-3.5 h-3.5 mr-0.5" />}
                            AI Notes
                          </Button>
                        )
                      )}
                      {rec.transcription_status === 'completed' && rec.meeting_notes && !notesData[rec.recording_id] && (
                        <Button variant="ghost" size="sm" onClick={() => fetchNotes(rec.recording_id)}
                          className="h-7 px-1.5 text-violet-400 hover:text-violet-300 hover:bg-violet-500/10"
                          data-testid={`saved-notes-${rec.recording_id}`}>
                          <Sparkles className="w-3.5 h-3.5 mr-0.5" />Notes
                        </Button>
                      )}
                      {rec.transcription_status === 'processing' && (
                        <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/15 text-[8px]">
                          <Loader2 className="w-2 h-2 mr-0.5 animate-spin" />Transcribing
                        </Badge>
                      )}
                      {rec.transcription_status === 'queued' && (
                        <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/15 text-[8px]">Queued</Badge>
                      )}
                      {rec.storage_type === 'cloud' ? (
                        <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/15 text-[9px]">
                          <Cloud className="w-2.5 h-2.5 mr-0.5" />Cloud
                        </Badge>
                      ) : (
                        <Badge className="bg-slate-500/10 text-slate-400 border-slate-500/15 text-[9px]">
                          <HardDrive className="w-2.5 h-2.5 mr-0.5" />Local
                        </Badge>
                      )}
                      {rec.storage_type === 'cloud' && (
                        <Button variant="ghost" size="sm" onClick={() => downloadRecording(rec)}
                          disabled={downloadingId === rec.recording_id}
                          className="h-7 w-7 p-0 text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10"
                          data-testid={`download-${rec.recording_id}`}>
                          {downloadingId === rec.recording_id
                            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            : <Download className="w-3.5 h-3.5" />}
                        </Button>
                      )}
                      <Button variant="ghost" size="sm" onClick={() => deleteRecording(rec.recording_id)}
                        className="h-7 w-7 p-0 text-red-400 hover:text-red-300 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                        data-testid={`delete-${rec.recording_id}`}>
                        <X className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                  {/* Expandable Transcript */}
                  {expandedTranscript === rec.recording_id && (
                    <div className="mt-1 p-3 bg-karau-card/30 rounded-lg border border-white/5 ml-13" data-testid={`transcript-content-${rec.recording_id}`}>
                      {!transcriptData[rec.recording_id] ? (
                        <div className="flex items-center gap-2 text-xs text-slate-400"><Loader2 className="w-3 h-3 animate-spin" />Loading transcript...</div>
                      ) : transcriptData[rec.recording_id].status === 'completed' && transcriptData[rec.recording_id].transcription ? (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-1"><FileText className="w-3 h-3" />Transcript</span>
                            {transcriptData[rec.recording_id].transcription.language && (
                              <Badge className="bg-white/5 text-slate-400 border-white/10 text-[8px]">{transcriptData[rec.recording_id].transcription.language}</Badge>
                            )}
                          </div>
                          {transcriptData[rec.recording_id].transcription.segments?.length > 0 ? (
                            <div className="max-h-48 overflow-y-auto space-y-1">
                              {transcriptData[rec.recording_id].transcription.segments.map((seg, i) => (
                                <div key={i} className="flex gap-2 text-[10px]">
                                  <span className="text-purple-400 font-mono shrink-0 w-12">
                                    {Math.floor(seg.start / 60)}:{String(Math.floor(seg.start % 60)).padStart(2, '0')}
                                  </span>
                                  <span className="text-slate-300">{seg.text}</span>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-[10px] text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
                              {transcriptData[rec.recording_id].transcription.text}
                            </p>
                          )}
                        </div>
                      ) : (
                        <p className="text-[10px] text-slate-500">{transcriptData[rec.recording_id].error || 'Transcript not available'}</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KarauRecordingsPage;
