import { useState, useEffect } from 'react';
import { Lock, Unlock, Shield, Loader2, Key, ShieldCheck, ShieldX } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { API, ESY } from './constants';
import { generateKeyPair, getPublicKeyJwk, isE2EESupported } from '@/utils/e2ee';

const E2EEIndicator = ({ channelId, token, isDm }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isDm || !channelId) return;
    checkStatus();
  }, [channelId, isDm]);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API}/api/lumi/e2ee/dm/${channelId}/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setStatus(await res.json());
    } catch {}
  };

  const enableE2EE = async () => {
    if (!isE2EESupported()) {
      toast.error('E2EE not supported in this browser');
      return;
    }
    setLoading(true);
    try {
      // Generate key pair
      const { publicKey } = await generateKeyPair();

      // Publish public key to server
      await fetch(`${API}/api/lumi/e2ee/keys/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ public_key: publicKey })
      });

      // Enable E2EE for user
      await fetch(`${API}/api/lumi/e2ee/enable`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success('E2EE enabled! Your keys have been generated.');
      checkStatus();
    } catch (e) {
      toast.error('Failed to enable E2EE');
    }
    setLoading(false);
  };

  if (!isDm) return null;

  if (!status) {
    return (
      <div className="flex items-center gap-1.5 px-2 py-1 text-[10px] text-slate-400" data-testid="e2ee-loading">
        <Shield className="w-3 h-3" />
        <span>Checking encryption...</span>
      </div>
    );
  }

  if (status.encrypted) {
    return (
      <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 border-b border-emerald-100" data-testid="e2ee-active">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
        <span className="text-[11px] font-medium text-emerald-700">End-to-end encrypted</span>
        <Lock className="w-3 h-3 text-emerald-500 ml-auto" />
      </div>
    );
  }

  if (!status.my_key_published) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-amber-50 border-b border-amber-100" data-testid="e2ee-setup-needed">
        <ShieldX className="w-3.5 h-3.5 text-amber-600" />
        <span className="text-[11px] text-amber-700">Not encrypted</span>
        <Button size="sm" onClick={enableE2EE} disabled={loading}
          className="ml-auto h-6 text-[10px] px-2 text-white rounded"
          style={{ background: ESY.turquoise }}
          data-testid="enable-e2ee-btn">
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Key className="w-3 h-3 mr-1" />Enable E2EE</>}
        </Button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border-b border-slate-100" data-testid="e2ee-partial">
      <Unlock className="w-3.5 h-3.5 text-slate-500" />
      <span className="text-[11px] text-slate-600">Your keys are ready. Waiting for partner to enable E2EE.</span>
    </div>
  );
};

export default E2EEIndicator;
