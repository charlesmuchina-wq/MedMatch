import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Fingerprint, Plus, Trash2, Loader2, ShieldCheck, Key, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { API, ESY } from './constants';

const b64ToArray = (b64) => Uint8Array.from(atob(b64.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
const arrayToB64 = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');

export const PasskeyManager = ({ user }) => {
  const [passkeys, setPasskeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const token = localStorage.getItem('token');
  const email = user?.email;

  const fetchPasskeys = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API}/api/auth/passkeys`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPasskeys(data.passkeys || []);
      }
    } catch { /* silent */ }
    setLoading(false);
  }, [token]);

  useEffect(() => { fetchPasskeys(); }, [fetchPasskeys]);

  const handleRegister = async () => {
    if (!email) { toast.error('Email not available'); return; }
    if (!window.PublicKeyCredential) { toast.error('Passkeys not supported on this browser'); return; }
    setRegistering(true);
    try {
      const startRes = await fetch(`${API}/api/auth/passkey/register/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      if (!startRes.ok) {
        const err = await startRes.json();
        toast.error(err.detail || 'Cannot start registration');
        setRegistering(false);
        return;
      }
      const opts = await startRes.json();
      const cred = await navigator.credentials.create({
        publicKey: {
          challenge: b64ToArray(opts.challenge),
          rp: { name: opts.rp.name, id: opts.rp.id || window.location.hostname },
          user: {
            id: Uint8Array.from(opts.user.id, c => c.charCodeAt(0)),
            name: opts.user.name,
            displayName: opts.user.displayName
          },
          pubKeyCredParams: opts.pubKeyCredParams,
          timeout: 60000,
          attestation: 'none'
        }
      });
      const pk = cred.response.getPublicKey ? arrayToB64(cred.response.getPublicKey()) : '';
      const finishRes = await fetch(`${API}/api/auth/passkey/register/finish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          credential_id: arrayToB64(cred.rawId),
          public_key: pk,
          attestation: arrayToB64(cred.response.attestationObject)
        })
      });
      if (finishRes.ok) {
        toast.success('Passkey registered successfully!');
        fetchPasskeys();
      } else {
        const err = await finishRes.json();
        toast.error(err.detail || 'Registration failed');
      }
    } catch (e) {
      if (e.name === 'NotAllowedError') toast.info('Passkey creation was cancelled');
      else toast.error('Failed to create passkey');
    }
    setRegistering(false);
  };

  const handleDelete = async (credentialId) => {
    setDeleting(credentialId);
    try {
      const res = await fetch(`${API}/api/auth/passkeys/${encodeURIComponent(credentialId)}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        toast.success('Passkey removed');
        setPasskeys(prev => prev.filter(p => p.credential_id !== credentialId));
      } else {
        const err = await res.json();
        toast.error(err.detail || 'Failed to delete');
      }
    } catch {
      toast.error('Failed to delete passkey');
    }
    setDeleting(null);
  };

  const supported = typeof window !== 'undefined' && window.PublicKeyCredential;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4" style={{ color: ESY.turquoise }} />
          <h3 className="text-sm font-bold text-slate-800">Passkeys & Security</h3>
        </div>
        {supported && (
          <Button
            size="sm"
            onClick={handleRegister}
            disabled={registering}
            data-testid="add-passkey-btn"
            className="h-7 text-xs text-white"
            style={{ background: `linear-gradient(135deg, ${ESY.turquoise}, ${ESY.pink})` }}
          >
            {registering ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Plus className="w-3 h-3 mr-1" />}
            Add Passkey
          </Button>
        )}
      </div>

      {/* Info */}
      <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
        <p className="text-xs text-slate-600 leading-relaxed">
          Passkeys use your device's biometrics (Face ID, fingerprint, Windows Hello) for secure, password-free sign-in. Each passkey is tied to this device.
        </p>
      </div>

      {/* Passkey List */}
      {loading ? (
        <div className="flex items-center justify-center py-6">
          <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
        </div>
      ) : passkeys.length === 0 ? (
        <div className="text-center py-6 rounded-lg border border-dashed border-slate-200">
          <Key className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-xs text-slate-500" data-testid="no-passkeys-msg">No passkeys registered</p>
          <p className="text-[10px] text-slate-400 mt-1">Add one to sign in without a password</p>
        </div>
      ) : (
        <div className="space-y-2" data-testid="passkey-list">
          {passkeys.map((pk) => (
            <div
              key={pk.credential_id}
              data-testid={`passkey-item-${pk.credential_id?.slice(0, 8)}`}
              className="flex items-center justify-between p-3 rounded-lg border border-slate-100 bg-white hover:border-slate-200 transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${ESY.turquoise}15` }}>
                  <Fingerprint className="w-4 h-4" style={{ color: ESY.turquoise }} />
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-slate-700 truncate">
                    {pk.device_name || 'Passkey Device'}
                  </p>
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                    <Clock className="w-2.5 h-2.5" />
                    {pk.created_at ? new Date(pk.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'Unknown'}
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleDelete(pk.credential_id)}
                disabled={deleting === pk.credential_id}
                data-testid={`delete-passkey-${pk.credential_id?.slice(0, 8)}`}
                className="p-1.5 rounded-md text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
              >
                {deleting === pk.credential_id ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Trash2 className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          ))}
        </div>
      )}

      {!supported && (
        <div className="p-3 rounded-lg bg-amber-50 border border-amber-100">
          <p className="text-xs text-amber-700">
            Passkeys are not supported on this browser. Use Chrome, Safari, or Edge for passkey support.
          </p>
        </div>
      )}
    </div>
  );
};
