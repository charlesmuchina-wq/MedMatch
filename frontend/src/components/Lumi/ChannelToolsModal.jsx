/**
 * ChannelToolsModal — Channel Templates + Webhooks management
 * Two tabs: Templates (create channels from pre-built templates) and Webhooks (setup integrations)
 */
import { useState, useEffect } from 'react';
import {
  X, Loader2, Plus, Copy, Check, ExternalLink, Zap, Hash,
  FolderKanban, Timer, AlertTriangle, MessageSquare, Globe,
  Github, Activity, Bell, Settings, Trash2, ChevronRight, Code
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { API } from './constants';
import BotChainBuilder from './BotChainBuilder';

const TEMPLATE_ICONS = {
  project: FolderKanban, sprint: Timer, incident: AlertTriangle,
  standup: MessageSquare, general: Globe,
};

const WEBHOOK_ICONS = {
  github: Github, jira: Activity, cicd: Zap,
  slack: MessageSquare, monitoring: Bell, alert: AlertTriangle,
};

const ChannelToolsModal = ({ token, channels, onClose, onChannelCreated }) => {
  const [tab, setTab] = useState('templates');
  const [templates, setTemplates] = useState([]);
  const [webhookTemplates, setWebhookTemplates] = useState([]);
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(null);
  const [namePrefix, setNamePrefix] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const [createdWebhook, setCreatedWebhook] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const headers = { Authorization: `Bearer ${token}` };
    try {
      const [tRes, wRes, iRes] = await Promise.all([
        fetch(`${API}/api/lumi/templates/channels/list`, { headers }),
        fetch(`${API}/api/lumi/automation/webhook-templates/list`, { headers }),
        fetch(`${API}/api/lumi/automation/webhooks`, { headers }).catch(() => ({ ok: false })),
      ]);
      if (tRes.ok) { const d = await tRes.json(); setTemplates(d.templates || []); }
      if (wRes.ok) { const d = await wRes.json(); setWebhookTemplates(d.templates || []); }
      if (iRes.ok) { const d = await iRes.json(); setWebhooks(d.webhooks || []); }
    } catch {}
    setLoading(false);
  };

  const createFromTemplate = async (templateId) => {
    if (!namePrefix.trim()) { toast.error('Enter a name prefix (e.g., "Q1", "Alpha")'); return; }
    setCreating(templateId);
    try {
      const res = await fetch(`${API}/api/lumi/templates/channels/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ template_id: templateId, name_prefix: namePrefix.trim() })
      });
      if (res.ok) {
        const ch = await res.json();
        toast.success(`Channel "${ch.name}" created!`);
        if (onChannelCreated) onChannelCreated(ch);
        setNamePrefix('');
      } else { const e = await res.json(); toast.error(e.detail || 'Creation failed'); }
    } catch { toast.error('Connection error'); }
    setCreating(null);
  };

  const createWebhook = async (templateId) => {
    if (!selectedChannel) { toast.error('Select a channel first'); return; }
    setCreating(templateId);
    try {
      const res = await fetch(`${API}/api/lumi/automation/webhook-templates/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ template_id: templateId, channel_id: selectedChannel })
      });
      if (res.ok) {
        const wh = await res.json();
        setCreatedWebhook(wh);
        toast.success(`${wh.name} webhook created!`);
        loadData();
      } else { const e = await res.json(); toast.error(e.detail || 'Creation failed'); }
    } catch { toast.error('Connection error'); }
    setCreating(null);
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success('Copied!');
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Webhook detail view after creation
  if (createdWebhook) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 max-h-[85vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="webhook-detail-modal">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                <Check className="w-4 h-4 text-green-600" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Webhook Created</h3>
                <p className="text-[10px] text-slate-500">{createdWebhook.name}</p>
              </div>
            </div>
            <button onClick={() => { setCreatedWebhook(null); }} className="p-1.5 hover:bg-slate-100 rounded-lg">
              <X className="w-4 h-4 text-slate-500" />
            </button>
          </div>

          <ScrollArea className="flex-1 px-5 py-4">
            <div className="space-y-4">
              {/* URL */}
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1.5">Webhook URL</label>
                <div className="flex gap-1.5">
                  <Input value={createdWebhook.url} readOnly className="h-8 text-xs font-mono bg-slate-50" data-testid="webhook-url" />
                  <Button size="sm" variant="outline" onClick={() => copyToClipboard(createdWebhook.url, 'url')} className="h-8 px-2.5" data-testid="copy-webhook-url">
                    {copiedId === 'url' ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                  </Button>
                </div>
              </div>

              {/* Events */}
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1.5">Events</label>
                <div className="flex gap-1.5 flex-wrap">
                  {(createdWebhook.events || []).map(e => (
                    <span key={e} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full text-[10px] font-medium">{e}</span>
                  ))}
                </div>
              </div>

              {/* Setup help */}
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1.5">Setup Instructions</label>
                <p className="text-xs text-slate-500 bg-slate-50 rounded-lg p-3">{createdWebhook.format_help}</p>
              </div>

              {/* Sample curl */}
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1.5">Test Command</label>
                <div className="bg-slate-900 rounded-lg p-3 relative group">
                  <code className="text-[10px] text-green-400 break-all leading-relaxed font-mono">{createdWebhook.sample_curl}</code>
                  <button onClick={() => copyToClipboard(createdWebhook.sample_curl, 'curl')}
                    className="absolute top-2 right-2 p-1 rounded bg-slate-700 hover:bg-slate-600 text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity">
                    {copiedId === 'curl' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  </button>
                </div>
              </div>
            </div>
          </ScrollArea>

          <div className="px-5 py-3 border-t border-slate-100">
            <Button size="sm" onClick={() => setCreatedWebhook(null)} className="w-full bg-slate-900 hover:bg-slate-800 text-white text-xs h-8">
              Done
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 max-h-[85vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()} data-testid="channel-tools-modal">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <Settings className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Channel Tools</h3>
              <p className="text-[11px] text-slate-500">Templates, Webhooks & Workflows</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 rounded-lg" data-testid="close-channel-tools">
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-100 px-4">
          {[
            { id: 'templates', label: 'Templates' },
            { id: 'webhooks', label: 'Webhooks' },
            { id: 'workflows', label: 'Workflows' },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-4 py-2.5 text-xs font-medium transition-colors ${tab === t.id ? 'text-violet-600 border-b-2 border-violet-600' : 'text-slate-500 hover:text-slate-700'}`}
              data-testid={`tools-tab-${t.id}`}>{t.label}</button>
          ))}
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center py-16">
            <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
          </div>
        ) : tab === 'templates' ? (
          <>
            {/* Name Prefix Input */}
            <div className="p-4 border-b border-slate-50 flex-shrink-0">
              <label className="text-[11px] text-slate-500 font-medium block mb-1.5">Channel name prefix</label>
              <Input value={namePrefix} onChange={e => setNamePrefix(e.target.value)}
                placeholder='e.g., "Q1", "Alpha", "Team-A"'
                className="h-9 text-xs" data-testid="template-name-prefix" />
              <p className="text-[10px] text-slate-400 mt-1">Creates: {namePrefix || 'PREFIX'}-[Template]</p>
            </div>

            <ScrollArea className="flex-1">
              <div className="p-4 space-y-2">
                {templates.map(tpl => {
                  const Icon = TEMPLATE_ICONS[tpl.id] || Hash;
                  return (
                    <div key={tpl.id} className="p-3.5 rounded-xl border border-slate-100 hover:border-slate-200 transition-all group" data-testid={`template-${tpl.id}`}>
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center flex-shrink-0">
                          <Icon className="w-5 h-5 text-violet-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-slate-800">{tpl.name}</p>
                          <p className="text-[11px] text-slate-500 mt-0.5">{tpl.description}</p>
                          <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 mt-1 inline-block">{tpl.type}</span>
                        </div>
                        <Button size="sm" onClick={() => createFromTemplate(tpl.id)}
                          disabled={creating === tpl.id || !namePrefix.trim()}
                          className="h-8 text-[10px] bg-violet-600 hover:bg-violet-500 text-white mt-1 opacity-80 group-hover:opacity-100"
                          data-testid={`create-template-${tpl.id}`}>
                          {creating === tpl.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Plus className="w-3 h-3 mr-1" />Create</>}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </ScrollArea>
          </>
        ) : tab === 'webhooks' ? (
          <>
            {/* Webhook channel selector */}
            <div className="p-4 border-b border-slate-50 flex-shrink-0">
              <div className="flex gap-2 items-center">
                <span className="text-[11px] text-slate-500 font-medium whitespace-nowrap">Send to:</span>
                <select value={selectedChannel} onChange={e => setSelectedChannel(e.target.value)}
                  className="flex-1 h-8 border border-slate-200 rounded-lg text-xs px-2 bg-white"
                  data-testid="webhook-channel-select">
                  <option value="">Select channel...</option>
                  {(channels || []).map(ch => <option key={ch.id} value={ch.id}>#{ch.name}</option>)}
                </select>
              </div>
            </div>

            <ScrollArea className="flex-1">
              <div className="p-4 space-y-2">
                {/* Webhook Templates */}
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-2">Create Webhook</p>
                {webhookTemplates.map(wt => {
                  const Icon = WEBHOOK_ICONS[wt.icon] || WEBHOOK_ICONS[wt.id] || Zap;
                  return (
                    <div key={wt.id} className="p-3.5 rounded-xl border border-slate-100 hover:border-slate-200 transition-all group" data-testid={`webhook-template-${wt.id}`}>
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                          <Icon className="w-5 h-5 text-amber-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-slate-800">{wt.name}</p>
                          <p className="text-[11px] text-slate-500 mt-0.5">{wt.description}</p>
                          <div className="flex gap-1 mt-1 flex-wrap">
                            {(wt.events || []).slice(0, 3).map(e => (
                              <span key={e} className="text-[8px] px-1.5 py-0.5 rounded bg-amber-50 text-amber-600 font-medium">{e}</span>
                            ))}
                          </div>
                        </div>
                        <Button size="sm" onClick={() => createWebhook(wt.id)}
                          disabled={creating === wt.id || !selectedChannel}
                          className="h-8 text-[10px] bg-amber-600 hover:bg-amber-500 text-white mt-1 opacity-80 group-hover:opacity-100"
                          data-testid={`create-webhook-${wt.id}`}>
                          {creating === wt.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Zap className="w-3 h-3 mr-1" />Setup</>}
                        </Button>
                      </div>
                    </div>
                  );
                })}

                {/* Active Webhooks */}
                {webhooks.length > 0 && (
                  <>
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-2 mt-4">Active Webhooks</p>
                    {webhooks.map(wh => {
                      const Icon = WEBHOOK_ICONS[wh.template_id] || Zap;
                      return (
                        <div key={wh.id} className="p-3 rounded-xl border border-slate-100 hover:border-slate-200 transition-all" data-testid={`active-webhook-${wh.id}`}>
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                              <Icon className="w-4 h-4 text-slate-600" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium text-slate-800">{wh.name}</p>
                              <p className="text-[10px] text-slate-500 truncate">{wh.id?.slice(0, 8)}...</p>
                            </div>
                            <span className={`w-1.5 h-1.5 rounded-full ${wh.is_active ? 'bg-green-500' : 'bg-slate-300'}`} />
                          </div>
                        </div>
                      );
                    })}
                  </>
                )}
              </div>
            </ScrollArea>
          </>
        ) : tab === 'workflows' ? (
          <div className="p-4 flex-1 overflow-auto">
            <BotChainBuilder channelId={channels?.[0]?.id || ''} token={token} />
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default ChannelToolsModal;
