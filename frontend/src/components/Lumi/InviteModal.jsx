import { useState, useEffect } from 'react';
import { X, Mail, Link2, Copy, Check, Send, Linkedin, MessageSquare, Twitter, Loader2, Users } from 'lucide-react';
import { toast } from 'sonner';
import { API } from './constants';

const InviteModal = ({ onClose, token }) => {
  const [tab, setTab] = useState('email');
  const [emails, setEmails] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [inviteLink, setInviteLink] = useState(null);
  const [linkCopied, setLinkCopied] = useState(false);
  const [history, setHistory] = useState([]);
  const [loadingLink, setLoadingLink] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/lumi/invite/history`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(d => setHistory(d.invites || [])).catch(() => {});
  }, [token]);

  const sendEmails = async () => {
    const emailList = emails.split(/[,;\n]/).map(e => e.trim()).filter(e => e.includes('@'));
    if (emailList.length === 0) { toast.error('Enter at least one valid email'); return; }
    setSending(true);
    try {
      const res = await fetch(`${API}/api/lumi/invite/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ emails: emailList, message })
      });
      if (res.ok) {
        const data = await res.json();
        const sent = data.results.filter(r => r.email_sent).length;
        const alreadyReg = data.results.filter(r => r.status === 'already_registered').length;
        if (sent > 0) toast.success(`${sent} invitation${sent > 1 ? 's' : ''} sent!`);
        if (alreadyReg > 0) toast.info(`${alreadyReg} user${alreadyReg > 1 ? 's are' : ' is'} already registered`);
        setEmails('');
        setMessage('');
        // Refresh history
        fetch(`${API}/api/lumi/invite/history`, { headers: { Authorization: `Bearer ${token}` } })
          .then(r => r.json()).then(d => setHistory(d.invites || [])).catch(() => {});
      }
    } catch { toast.error('Failed to send invites'); }
    setSending(false);
  };

  const generateLink = async () => {
    setLoadingLink(true);
    try {
      const res = await fetch(`${API}/api/lumi/invite/link`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setInviteLink(await res.json());
    } catch { toast.error('Failed to generate link'); }
    setLoadingLink(false);
  };

  const copyLink = () => {
    if (inviteLink?.invite_url) {
      navigator.clipboard.writeText(inviteLink.invite_url);
      setLinkCopied(true);
      toast.success('Link copied!');
      setTimeout(() => setLinkCopied(false), 2000);
    }
  };

  const shareSMS = () => {
    if (inviteLink?.sms_text) window.open(`sms:?body=${encodeURIComponent(inviteLink.sms_text)}`, '_blank');
  };

  const shareLinkedIn = () => {
    if (inviteLink?.linkedin_url) window.open(inviteLink.linkedin_url, '_blank');
  };

  const shareTwitter = () => {
    if (inviteLink?.twitter_url) window.open(inviteLink.twitter_url, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="invite-modal">
      <div className="w-full max-w-lg mx-4 bg-[#131920] border border-white/10 rounded-2xl shadow-2xl overflow-hidden" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7)' }}>
              <Users className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Invite to ENZI</h2>
              <p className="text-[10px] text-slate-500">Invited users must register before chatting</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-white/10 rounded-lg transition-colors" data-testid="close-invite-modal">
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/10">
          {[
            { id: 'email', label: 'Email', icon: Mail },
            { id: 'link', label: 'Share Link', icon: Link2 },
            { id: 'history', label: 'History', icon: Users },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`flex-1 flex items-center justify-center gap-1.5 px-4 py-3 text-xs font-medium transition-colors ${tab === t.id ? 'text-white border-b-2 border-[#00CEC9] bg-white/[0.03]' : 'text-slate-500 hover:text-white/70'}`}
              data-testid={`invite-tab-${t.id}`}>
              <t.icon className="w-3.5 h-3.5" />{t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6 max-h-[400px] overflow-auto">
          {tab === 'email' && (
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1.5 block">Email addresses</label>
                <textarea value={emails} onChange={e => setEmails(e.target.value)}
                  placeholder="Enter emails separated by commas or new lines..."
                  className="w-full h-24 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 resize-none transition-colors"
                  data-testid="invite-emails-input" />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 mb-1.5 block">Personal message (optional)</label>
                <input value={message} onChange={e => setMessage(e.target.value)}
                  placeholder="Hey, join me on ENZI..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-slate-600 outline-none focus:border-[#00CEC9]/50 transition-colors"
                  data-testid="invite-message-input" />
              </div>
              <button onClick={sendEmails} disabled={sending}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-white text-sm font-semibold transition-all hover:opacity-90 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, #00CEC9, #6C5CE7)' }}
                data-testid="send-invites-btn">
                {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                {sending ? 'Sending...' : 'Send Invitations'}
              </button>
              <p className="text-[10px] text-slate-600 text-center">Invitees will need to create an account to access ENZI</p>
            </div>
          )}

          {tab === 'link' && (
            <div className="space-y-4">
              {!inviteLink ? (
                <button onClick={generateLink} disabled={loadingLink}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border border-white/10 text-white text-sm font-medium hover:bg-white/5 transition-colors"
                  data-testid="generate-link-btn">
                  {loadingLink ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link2 className="w-4 h-4" />}
                  Generate Invite Link
                </button>
              ) : (
                <>
                  <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-4 py-3">
                    <input value={inviteLink.invite_url} readOnly className="flex-1 bg-transparent text-xs text-white/70 outline-none" data-testid="invite-link-input" />
                    <button onClick={copyLink} className="p-1.5 hover:bg-white/10 rounded-lg transition-colors" data-testid="copy-link-btn">
                      {linkCopied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-slate-400" />}
                    </button>
                  </div>

                  <p className="text-[10px] text-slate-500 text-center">Share via</p>

                  <div className="grid grid-cols-3 gap-3">
                    <button onClick={shareSMS}
                      className="flex flex-col items-center gap-2 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                      data-testid="share-sms-btn">
                      <MessageSquare className="w-5 h-5 text-emerald-400" />
                      <span className="text-[10px] text-slate-400">SMS</span>
                    </button>
                    <button onClick={shareLinkedIn}
                      className="flex flex-col items-center gap-2 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                      data-testid="share-linkedin-btn">
                      <Linkedin className="w-5 h-5 text-blue-400" />
                      <span className="text-[10px] text-slate-400">LinkedIn</span>
                    </button>
                    <button onClick={shareTwitter}
                      className="flex flex-col items-center gap-2 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                      data-testid="share-twitter-btn">
                      <Twitter className="w-5 h-5 text-sky-400" />
                      <span className="text-[10px] text-slate-400">Twitter/X</span>
                    </button>
                  </div>
                </>
              )}

              <p className="text-[10px] text-slate-600 text-center">Link expires in 7 days. Recipients must register to access ENZI.</p>
            </div>
          )}

          {tab === 'history' && (
            <div className="space-y-2">
              {history.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">No invitations sent yet</p>
              ) : history.map((inv, i) => (
                <div key={i} className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.03] border border-white/5">
                  <Mail className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-white/80 truncate">{inv.invited_email || 'Link invite'}</p>
                    <p className="text-[10px] text-slate-600">{new Date(inv.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className={`text-[9px] px-2 py-0.5 rounded-full font-medium ${
                    inv.status === 'accepted' ? 'bg-emerald-500/10 text-emerald-400' :
                    inv.status === 'pending' ? 'bg-amber-500/10 text-amber-400' :
                    'bg-white/5 text-slate-500'
                  }`}>{inv.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(16px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default InviteModal;
