import { useState, useEffect } from 'react';
import { QrCode, Copy, Check, Clock, Users, Trash2, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

export default function QRCodePanel({ meetingId, meetingTitle }) {
  const [qrCodes, setQrCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(null);

  useEffect(() => { fetchQRCodes(); }, [meetingId]);

  const fetchQRCodes = async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/qr/meeting/${meetingId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setQrCodes(data.qr_codes || []);
      }
    } catch {}
  };

  const generateQR = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/qr/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          meeting_id: meetingId,
          expires_minutes: 120,
          max_uses: 50,
          label: `QR for ${meetingTitle || 'Meeting'}`
        })
      });
      if (res.ok) {
        toast.success('QR code generated');
        fetchQRCodes();
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || 'Failed to generate QR');
      }
    } catch { toast.error('QR generation error'); }
    setLoading(false);
  };

  const deactivateQR = async (token_id) => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau-meet/qr/${token_id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        toast.success('QR code deactivated');
        fetchQRCodes();
      }
    } catch {}
  };

  const copyJoinLink = (qr) => {
    const url = `${window.location.origin}${qr.join_url}`;
    navigator.clipboard.writeText(url);
    setCopied(qr.qr_token);
    setTimeout(() => setCopied(null), 2000);
    toast.success('Join link copied');
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="qr-code-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <QrCode className="w-3.5 h-3.5 text-teal-400" />
          Touchless QR Entry
        </h3>
        <p className="text-[8px] text-slate-500 mt-0.5">Scan to join instantly</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        <Button size="sm" onClick={generateQR} disabled={loading}
          className="w-full h-7 text-[10px] bg-teal-500/80 hover:bg-teal-400 rounded-lg" data-testid="generate-qr-btn">
          <Plus className="w-3 h-3 mr-1" />
          {loading ? 'Generating...' : 'Generate New QR Code'}
        </Button>

        {qrCodes.length === 0 ? (
          <p className="text-[9px] text-slate-500 text-center py-4">No QR codes yet. Generate one above.</p>
        ) : qrCodes.map(qr => (
          <div key={qr.qr_token} className={`p-2 rounded-lg border ${qr.active ? 'bg-teal-500/5 border-teal-500/15' : 'bg-slate-500/5 border-slate-500/10 opacity-50'}`} data-testid={`qr-item-${qr.qr_token}`}>
            {/* QR Visual Placeholder */}
            <div className="w-full aspect-square bg-white/5 rounded-lg flex items-center justify-center mb-2 border border-white/10">
              <div className="text-center">
                <QrCode className="w-12 h-12 text-teal-400 mx-auto mb-1" />
                <p className="text-[8px] text-teal-300 font-mono break-all">{qr.qr_token}</p>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <p className="text-[9px] text-white font-medium truncate">{qr.label}</p>
                <div className="flex items-center gap-2 text-[8px] text-slate-400">
                  <span className="flex items-center gap-0.5"><Users className="w-2 h-2" />{qr.use_count}/{qr.max_uses}</span>
                  <span className="flex items-center gap-0.5"><Clock className="w-2 h-2" />Exp: {new Date(qr.expires_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </div>
              <Badge className={`text-[7px] ${qr.active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-500/10 text-slate-400'}`}>
                {qr.active ? 'Active' : 'Expired'}
              </Badge>
            </div>

            {qr.active && (
              <div className="flex gap-1 mt-1.5">
                <Button size="sm" variant="ghost" onClick={() => copyJoinLink(qr)}
                  className="h-5 flex-1 text-[8px] text-teal-400 hover:bg-teal-500/10" data-testid={`copy-qr-${qr.qr_token}`}>
                  {copied === qr.qr_token ? <Check className="w-2 h-2 mr-0.5" /> : <Copy className="w-2 h-2 mr-0.5" />}
                  {copied === qr.qr_token ? 'Copied' : 'Copy Link'}
                </Button>
                <Button size="sm" variant="ghost" onClick={() => deactivateQR(qr.qr_token)}
                  className="h-5 px-1.5 text-[8px] text-red-400 hover:bg-red-500/10" data-testid={`deactivate-qr-${qr.qr_token}`}>
                  <Trash2 className="w-2 h-2" />
                </Button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
