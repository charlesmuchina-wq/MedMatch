import { useState, useEffect } from 'react';
import { Shield, CheckCircle, AlertTriangle } from 'lucide-react';
import { API, ESY } from './constants';

export const ComplianceWidget = ({ token, onClick }) => {
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    const load = async () => {
      try {
        const res = await fetch(`${API}/api/lumi/compliance/status`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) {
          const data = await res.json();
          setScore(data.overall_score);
        }
      } catch (e) {}
      setLoading(false);
    };
    load();
    const interval = setInterval(load, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, [token]);

  if (loading || score === null) return null;

  const isGood = score >= 80;

  return (
    <button onClick={onClick}
      className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg transition-all hover:bg-white/10 group"
      data-testid="compliance-widget">
      <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${isGood ? 'bg-emerald-500/20' : 'bg-amber-500/20'}`}>
        {isGood ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
      </div>
      <div className="flex-1 min-w-0 text-left">
        <p className="text-[10px] font-semibold text-white/70 uppercase tracking-wider">Compliance</p>
        <div className="flex items-center gap-2 mt-0.5">
          <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all ${isGood ? 'bg-emerald-400' : 'bg-amber-400'}`}
              style={{ width: `${score}%` }} />
          </div>
          <span className={`text-[11px] font-bold ${isGood ? 'text-emerald-400' : 'text-amber-400'}`}>{score}%</span>
        </div>
      </div>
    </button>
  );
};
