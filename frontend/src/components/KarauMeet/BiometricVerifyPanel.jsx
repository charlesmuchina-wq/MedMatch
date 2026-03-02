import { useState, useEffect, useCallback } from 'react';
import { Shield, ShieldCheck, ShieldAlert, Fingerprint, ScanFace, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const API = process.env.REACT_APP_BACKEND_URL;

const TRUST_COLORS = {
  high: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', border: 'border-emerald-500/15' },
  medium: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/15' },
  low: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/15' },
  unverified: { bg: 'bg-slate-500/10', text: 'text-slate-400', border: 'border-slate-500/15' },
};

export default function BiometricVerifyPanel({ meetingId }) {
  const [trustData, setTrustData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchTrust = useCallback(async () => {
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`${API}/api/karau/biometric/${meetingId}/trust`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) setTrustData(await res.json());
    } catch {}
    setLoading(false);
  }, [meetingId]);

  useEffect(() => { fetchTrust(); const i = setInterval(fetchTrust, 15000); return () => clearInterval(i); }, [fetchTrust]);

  if (loading) return <div className="p-3 text-[9px] text-slate-500">Verifying feeds...</div>;

  const summary = trustData?.summary || {};
  const participants = trustData?.participants || [];
  const overallColors = TRUST_COLORS[summary.overall_trust] || TRUST_COLORS.medium;

  return (
    <div className="flex-1 flex flex-col overflow-hidden" data-testid="biometric-verify-panel">
      <div className="p-2.5 border-b border-white/5">
        <h3 className="text-xs font-semibold text-white flex items-center gap-1.5">
          <Fingerprint className="w-3.5 h-3.5 text-teal-400" />
          Feed Verification
        </h3>
        <p className="text-[8px] text-slate-500 mt-0.5">Anti-deepfake trust scoring</p>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {/* Overall Trust Status */}
        <div className={`p-2 rounded-lg border ${overallColors.bg} ${overallColors.border}`} data-testid="overall-trust">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              {summary.overall_trust === 'high' ? <ShieldCheck className="w-4 h-4 text-emerald-400" /> :
               summary.overall_trust === 'low' ? <ShieldAlert className="w-4 h-4 text-red-400" /> :
               <Shield className="w-4 h-4 text-amber-400" />}
              <div>
                <p className={`text-[10px] font-semibold ${overallColors.text}`}>
                  {summary.overall_trust === 'high' ? 'All Feeds Verified' :
                   summary.overall_trust === 'low' ? 'Trust Concerns' : 'Mostly Verified'}
                </p>
                <p className="text-[8px] text-slate-400">Integrity: {Math.round((summary.average_integrity || 0) * 100)}%</p>
              </div>
            </div>
            <Badge className={`text-[8px] ${overallColors.bg} ${overallColors.text}`}>
              {summary.verified || 0}/{summary.total || 0}
            </Badge>
          </div>
        </div>

        {/* Participant Trust Cards */}
        <div className="space-y-1" data-testid="participant-trust-list">
          {participants.map(p => {
            const colors = TRUST_COLORS[p.trust_level] || TRUST_COLORS.medium;
            const pattern = p.visual_pattern || {};
            const score = Math.round((p.integrity_score || 0) * 100);

            return (
              <div key={p.user_id} className={`p-1.5 rounded-lg border ${colors.border} ${colors.bg}`} data-testid={`trust-${p.user_id}`}>
                <div className="flex items-center gap-2">
                  {/* Watermark Visual */}
                  <div className="w-6 h-6 rounded-full bg-karau-bg/60 flex items-center justify-center relative overflow-hidden">
                    {(pattern.segments || []).map((seg, i) => (
                      <div key={i} className="absolute rounded-full"
                        style={{
                          width: seg.size * 2, height: seg.size * 2,
                          backgroundColor: seg.color,
                          opacity: seg.opacity,
                          left: `${20 + seg.position * 8}%`,
                          top: `${30 + (i % 3) * 15}%`
                        }} />
                    ))}
                    <ScanFace className="w-3 h-3 text-white/40 relative z-10" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1">
                      <span className="text-[9px] text-white font-medium truncate">{p.user_name}</span>
                      {p.verified ? (
                        <ShieldCheck className="w-3 h-3 text-emerald-400 shrink-0" />
                      ) : (
                        <ShieldAlert className="w-3 h-3 text-red-400 shrink-0" />
                      )}
                    </div>
                    {/* Integrity bar */}
                    <div className="flex items-center gap-1 mt-0.5">
                      <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full rounded-full transition-all" style={{
                          width: `${score}%`,
                          backgroundColor: score > 90 ? '#34d399' : score > 70 ? '#fbbf24' : '#f87171'
                        }} />
                      </div>
                      <span className="text-[7px] text-slate-400 w-6 text-right">{score}%</span>
                    </div>
                  </div>

                  <Badge className={`text-[6px] shrink-0 ${colors.bg} ${colors.text}`}>{p.trust_level}</Badge>
                </div>

                {/* Details */}
                <div className="flex items-center gap-2 mt-1 text-[7px] text-slate-500 ml-8">
                  <span>Checks: {p.check_count}</span>
                  {pattern.hash_preview && <span className="font-mono">{pattern.hash_preview}</span>}
                  {p.watermark_active && <span className="w-1 h-1 rounded-full bg-emerald-400" />}
                </div>
              </div>
            );
          })}
        </div>

        {/* Info */}
        <div className="p-2 bg-karau-bg/40 rounded-lg border border-white/5">
          <p className="text-[8px] text-teal-400 uppercase tracking-wider mb-1">How it works</p>
          <ul className="text-[7px] text-slate-400 space-y-0.5 list-disc list-inside">
            <li>Unique watermarks embedded in each video feed</li>
            <li>Continuous integrity checks validate feed authenticity</li>
            <li>Trust score degrades if feed manipulation is detected</li>
            <li>Protects against deepfake impersonation in high-stakes calls</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
