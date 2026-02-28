import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Video, Clock, Archive, X, Loader2, Cloud, HardDrive,
  Download, CloudUpload, CheckCircle2, FileText, ChevronDown, ChevronUp
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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
                <div key={rec.recording_id}
                  className="flex items-center justify-between p-3 bg-karau-bg/40 rounded-xl hover:bg-karau-surface/40 transition-colors group"
                  data-testid={`recording-${rec.recording_id}`}>
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
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KarauRecordingsPage;
