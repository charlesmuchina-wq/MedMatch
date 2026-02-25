import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Video, Clock, Archive, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from '@/utils/i18n';

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Recordings Page - View and manage meeting recordings
 */
const KarauRecordingsPage = () => {
  const { t } = useTranslation();
  const [recordings, setRecordings] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecordings();
  }, []);

  const fetchRecordings = async () => {
    const token = localStorage.getItem('token');
    try {
      const [recordingsRes, statsRes] = await Promise.all([
        fetch(`${API}/api/karau-meet/recordings/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API}/api/karau-meet/recordings/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (recordingsRes.ok) {
        const data = await recordingsRes.json();
        setRecordings(data.recordings || []);
      }
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
    } catch (error) {
      console.error('Error fetching recordings:', error);
    }
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

  const deleteRecording = async (recordingId) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/recordings/${recordingId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setRecordings(prev => prev.filter(r => r.recording_id !== recordingId));
        toast.success(t("karauMeet.recordingDeleted"));
      }
    } catch (error) {
      toast.error(t("karauMeet.failedDeleteRecording"));
    }
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-turquoise animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white" data-testid="recordings-title">Recordings</h1>
        <p className="text-slate-400">Access your meeting recordings</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4">
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                <Video className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white" data-testid="stat-total">{stats.total_recordings}</p>
                <p className="text-xs text-slate-400">Total Recordings</p>
              </div>
            </div>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-turquoise/20 flex items-center justify-center">
                <Clock className="w-5 h-5 text-turquoise" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white" data-testid="stat-duration">{formatDuration(stats.total_duration_seconds)}</p>
                <p className="text-xs text-slate-400">Total Duration</p>
              </div>
            </div>
          </Card>
          <Card className="bg-slate-800/50 border-slate-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <Archive className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white" data-testid="stat-size">{formatFileSize(stats.total_size_bytes)}</p>
                <p className="text-xs text-slate-400">Storage Used</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Recordings List */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Your Recordings</CardTitle>
          <CardDescription className="text-slate-400">
            Recordings are saved to your local device
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recordings.length === 0 ? (
            <div className="text-center py-8" data-testid="no-recordings">
              <Video className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">No recordings yet</p>
              <p className="text-sm text-slate-500">Start recording in a meeting to see them here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recordings.map((rec) => (
                <div key={rec.recording_id} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg" data-testid={`recording-${rec.recording_id}`}>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-violet-500/20 flex items-center justify-center">
                      <Video className="w-6 h-6 text-violet-400" />
                    </div>
                    <div>
                      <p className="font-medium text-white">{rec.meeting_title}</p>
                      <div className="flex items-center gap-3 text-xs text-slate-400">
                        <span>{new Date(rec.recorded_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{formatDuration(rec.duration_seconds)}</span>
                        <span>•</span>
                        <span>{formatFileSize(rec.file_size_bytes)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-slate-400 border-slate-600">
                      Local
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteRecording(rec.recording_id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default KarauRecordingsPage;
