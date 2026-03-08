import { useState, useEffect } from 'react';
import { X, Crown, Check, Loader2, CreditCard, Zap, Shield, Brain, Users, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { API, ESY } from './constants';

const TIER_STYLES = {
  pro_monthly: { gradient: 'linear-gradient(135deg, #00CEC9, #0984E3)', icon: Zap },
  pro_yearly: { gradient: 'linear-gradient(135deg, #00CEC9, #0984E3)', icon: Zap },
  team_monthly: { gradient: 'linear-gradient(135deg, #6C5CE7, #E84393)', icon: Users },
  enterprise: { gradient: 'linear-gradient(135deg, #2D3436, #636E72)', icon: Shield },
};

const PremiumModal = ({ token, onClose }) => {
  const [packages, setPackages] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [pkgRes, subRes] = await Promise.all([
        fetch(`${API}/api/lumi/payments/packages`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/api/lumi/payments/my-subscription`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      if (pkgRes.ok) setPackages((await pkgRes.json()).packages || []);
      if (subRes.ok) setSubscription(await subRes.json());
    } catch {}
    setLoading(false);
  };

  const handleCheckout = async (pkgId) => {
    setCheckingOut(pkgId);
    try {
      const res = await fetch(`${API}/api/lumi/payments/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ package_id: pkgId, origin_url: window.location.origin })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.url) window.location.href = data.url;
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to start checkout');
      }
    } catch { toast.error('Connection error'); }
    setCheckingOut(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[85vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="premium-modal">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #FFD700, #FFA500)' }}>
              <Crown className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">ENZI Premium</h3>
              <p className="text-[11px] text-slate-500">{subscription?.is_premium ? `Current: ${subscription.package_name}` : 'Upgrade your experience'}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-premium-modal"><X className="w-4 h-4 text-slate-500" /></button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-6">
            {loading ? <div className="flex justify-center py-12"><Loader2 className="w-5 h-5 animate-spin text-slate-400" /></div> : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {packages.map(pkg => {
                  const style = TIER_STYLES[pkg.id] || TIER_STYLES.pro_monthly;
                  const Icon = style.icon;
                  const isActive = subscription?.package_id === pkg.id;
                  return (
                    <div key={pkg.id} className={`p-4 rounded-xl border-2 transition-all ${isActive ? 'border-[#00CEC9] bg-[#00CEC9]/5' : 'border-slate-100 hover:border-slate-200'}`} data-testid={`package-${pkg.id}`}>
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: style.gradient }}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-slate-900">{pkg.name}</h4>
                          <p className="text-[11px] text-slate-500">{pkg.period}</p>
                        </div>
                      </div>
                      <div className="mb-3">
                        <span className="text-2xl font-bold text-slate-900">${pkg.amount}</span>
                        <span className="text-xs text-slate-500">/{pkg.period === 'yearly' ? 'year' : 'month'}</span>
                      </div>
                      <ul className="space-y-1.5 mb-4">
                        {pkg.features.map(f => (
                          <li key={f} className="flex items-center gap-2 text-[11px] text-slate-600">
                            <Check className="w-3 h-3 text-emerald-500 flex-shrink-0" />{f}
                          </li>
                        ))}
                      </ul>
                      {isActive ? (
                        <div className="text-center text-[11px] font-medium text-[#00CEC9] py-2" data-testid={`active-plan-${pkg.id}`}>Current Plan</div>
                      ) : (
                        <Button onClick={() => handleCheckout(pkg.id)} disabled={checkingOut === pkg.id}
                          className="w-full h-9 text-white text-xs font-medium rounded-lg"
                          style={{ background: style.gradient }}
                          data-testid={`checkout-${pkg.id}`}>
                          {checkingOut === pkg.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><CreditCard className="w-3 h-3 mr-1.5" />Upgrade</>}
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};

export default PremiumModal;
