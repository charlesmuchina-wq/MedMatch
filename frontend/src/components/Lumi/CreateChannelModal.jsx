import { useState } from 'react';
import { Hash, Lock, Megaphone, X, Loader2 } from 'lucide-react';
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
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/lumi/channels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ name: name.trim(), description: desc, channel_type: type, is_private: isPrivate })
      });
      if (res.ok) { onCreated(await res.json()); toast.success('Channel created'); }
    } catch (e) { toast.error('Failed'); }
    setLoading(false);
  };

  const types = [
    { val: 'group', label: t('lumi.typeGroup') || 'Group', icon: Hash },
    { val: 'project', label: t('lumi.typeProject') || 'Project', icon: Hash },
    { val: 'announcement', label: t('lumi.typeAnnouncement') || 'Announcement', icon: Megaphone },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white border border-slate-200 rounded-lg w-full max-w-md p-6 shadow-lg" onClick={e => e.stopPropagation()} data-testid="create-channel-modal">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-semibold text-slate-900">{t('lumi.createChannel') || 'Create Channel'}</h3>
          <button onClick={onClose} className="p-1 hover:bg-slate-100 rounded-md"><X className="w-5 h-5 text-slate-400" /></button>
        </div>
        <div className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">{t('lumi.channelName') || 'Channel Name'}</label>
            <Input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. project-alpha"
              className="border-slate-200 rounded-md focus:ring-[#008080]/20 focus:border-[#008080]" data-testid="channel-name-input" />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-500 mb-1.5 block">{t('lumi.description') || 'Description'}</label>
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
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={isPrivate} onChange={e => setIsPrivate(e.target.checked)} className="rounded border-slate-300 text-[#008080]" />
            <Lock className="w-3.5 h-3.5 text-slate-400" /><span className="text-sm text-slate-600">{t('lumi.privateChannel') || 'Private'}</span>
          </label>
        </div>
        <div className="flex gap-3 mt-6">
          <Button variant="ghost" onClick={onClose} className="flex-1 text-slate-500 hover:bg-slate-100 rounded-md">Cancel</Button>
          <Button onClick={handleCreate} disabled={!name.trim() || loading}
            className="flex-1 bg-[#008080] hover:bg-[#006666] text-white rounded-md" data-testid="create-channel-btn">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create'}
          </Button>
        </div>
      </div>
    </div>
  );
};
