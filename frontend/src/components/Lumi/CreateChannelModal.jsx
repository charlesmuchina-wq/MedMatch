import { useState } from 'react';
import { Hash, Lock, Megaphone, X, Loader2, Mail, Shield, UserPlus } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useTranslation } from '@/utils/i18n';
import { API } from './constants';

export const CreateChannelModal = ({ onClose, onCreated, token }) => {
  const { t } = useTranslation();
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [type, setType] = useState('group');
  const [isPrivate, setIsPrivate] = useState(false);
  const [requiresApproval, setRequiresApproval] = useState(false);
  const [inviteEmails, setInviteEmails] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1 = details, 2 = invites

  const handleCreate = async () => {
    if (!name.trim()) return;
    setLoading(true);
    const emails = inviteEmails
      .split(/[,;\n]+/)
      .map(e => e.trim())
      .filter(e => e.includes('@'));

    try {
      const res = await fetch(`${API}/api/lumi/channels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({
          name: name.trim(),
          description: desc,
          channel_type: type,
          is_private: isPrivate,
          requires_approval: requiresApproval,
          invite_emails: emails,
        })
      });
      if (res.ok) {
        const ch = await res.json();
        onCreated(ch);
        toast.success(emails.length > 0
          ? `Channel created & ${emails.length} invite(s) sent`
          : 'Channel created');
      }
    } catch (e) { toast.error('Failed'); }
    setLoading(false);
  };

  const types = [
    { val: 'group', label: 'Group', icon: Hash },
    { val: 'project', label: 'Project', icon: Hash },
    { val: 'announcement', label: 'Announce', icon: Megaphone },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white border border-slate-200 rounded-lg w-full max-w-md p-6 shadow-lg" onClick={e => e.stopPropagation()} data-testid="create-channel-modal">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-semibold text-slate-900">
            {step === 1 ? 'Create Channel' : 'Invite Members'}
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-5 h-5 text-slate-400" /></button>
        </div>

        {step === 1 ? (
          <>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-500 mb-1.5 block">Channel Name</label>
                <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. project-alpha"
                  className="border-slate-200 rounded-md focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="channel-name-input" />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500 mb-1.5 block">Description</label>
                <Input value={desc} onChange={e => setDesc(e.target.value)} placeholder="What's this channel about?"
                  className="border-slate-200 rounded-md focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="channel-desc-input" />
              </div>
              <div className="flex gap-2">
                {types.map(tp => (
                  <button key={tp.val} onClick={() => setType(tp.val)}
                    className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-xs font-medium transition-colors ${
                      type === tp.val ? 'bg-[#008080]/10 text-[#008080] border border-[#008080]/30' : 'bg-slate-50 text-slate-500 border border-slate-200 hover:bg-slate-100'
                    }`} data-testid={`type-${tp.val}`}>
                    <tp.icon className="w-3.5 h-3.5" />{tp.label}
                  </button>
                ))}
              </div>
              <div className="space-y-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={isPrivate} onChange={e => setIsPrivate(e.target.checked)} className="rounded border-slate-300 text-[#008080]" />
                  <Lock className="w-3.5 h-3.5 text-slate-400" /><span className="text-sm text-slate-600">Private channel</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={requiresApproval} onChange={e => setRequiresApproval(e.target.checked)} className="rounded border-slate-300 text-[#008080]" />
                  <Shield className="w-3.5 h-3.5 text-slate-400" /><span className="text-sm text-slate-600">Require approval to join</span>
                </label>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <Button variant="ghost" onClick={onClose} className="flex-1 text-slate-500 hover:bg-slate-100 rounded-md">Cancel</Button>
              <Button onClick={() => setStep(2)} disabled={!name.trim()}
                className="flex-1 bg-[#008080] hover:bg-[#006666] text-white rounded-md" data-testid="next-step-btn">
                <UserPlus className="w-4 h-4 mr-1.5" /> Next: Invite
              </Button>
            </div>
          </>
        ) : (
          <>
            <div className="space-y-4">
              <div className="bg-slate-50 rounded-md p-3">
                <div className="flex items-center gap-2 text-sm text-slate-700">
                  <Hash className="w-4 h-4 text-[#008080]" />
                  <span className="font-medium">{name}</span>
                  {isPrivate && <Lock className="w-3 h-3 text-slate-400" />}
                  {requiresApproval && <Shield className="w-3 h-3 text-amber-500" />}
                </div>
                {desc && <p className="text-xs text-slate-500 mt-1 ml-6">{desc}</p>}
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500 mb-1.5 flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5" /> Invite by email (optional)
                </label>
                <textarea
                  value={inviteEmails}
                  onChange={e => setInviteEmails(e.target.value)}
                  placeholder={"user1@company.com\nuser2@company.com"}
                  rows={4}
                  className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm focus:ring-[#008080]/20 focus:border-[#008080] outline-none resize-none"
                  data-testid="invite-emails-input"
                />
                <p className="text-[10px] text-slate-400 mt-1">Separate emails with commas, semicolons, or new lines</p>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <Button variant="ghost" onClick={() => setStep(1)} className="flex-1 text-slate-500 hover:bg-slate-100 rounded-md">Back</Button>
              <Button onClick={handleCreate} disabled={loading}
                className="flex-1 bg-[#008080] hover:bg-[#006666] text-white rounded-md" data-testid="create-channel-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : inviteEmails.trim() ? 'Create & Invite' : 'Create Channel'}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
