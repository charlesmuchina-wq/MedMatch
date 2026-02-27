import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Users, Send, MessageSquare, Mail, Smartphone, Linkedin, Plus, Clock,
  Check, FileText, Loader2, ThumbsUp, Heart, Star, Smile, Reply,
  Search, Filter, ArrowUpRight, Hash, Trash2, Copy, Eye
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const REACTIONS = [
  { emoji: 'thumbsup', icon: ThumbsUp, label: 'Like' },
  { emoji: 'heart', icon: Heart, label: 'Love' },
  { emoji: 'star', icon: Star, label: 'Star' },
];

const CHANNEL_CONFIG = {
  email: { icon: Mail, color: 'text-blue-400 bg-blue-500/15', label: 'Email' },
  sms: { icon: Smartphone, color: 'text-emerald-400 bg-emerald-500/15', label: 'SMS' },
  inmail: { icon: Linkedin, color: 'text-violet-400 bg-violet-500/15', label: 'InMail' },
};

function StatCard({ label, value, icon: Icon, accent }) {
  return (
    <div className="p-3 rounded-lg bg-slate-700/30 border border-slate-700/40">
      <div className="flex items-center gap-2 mb-1">
        {Icon && <Icon className={`w-3.5 h-3.5 ${accent || 'text-slate-500'}`} />}
        <span className="text-[10px] text-slate-400 uppercase tracking-wider">{label}</span>
      </div>
      <p className="text-lg font-bold text-white">{value}</p>
    </div>
  );
}

export default function TeamOutreachPage() {
  const [tab, setTab] = useState('collaborate');
  const [comments, setComments] = useState([]);
  const [outreachHistory, setOutreachHistory] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [candidateSearch, setCandidateSearch] = useState('');
  const [outreachMsg, setOutreachMsg] = useState('');
  const [outreachSubject, setOutreachSubject] = useState('');
  const [outreachChannel, setOutreachChannel] = useState('email');
  const [selectedRecipients, setSelectedRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [showTemplateCreate, setShowTemplateCreate] = useState(false);
  const [templateForm, setTemplateForm] = useState({ name: '', channel: 'email', subject: '', body: '' });
  const [creatingTemplate, setCreatingTemplate] = useState(false);

  const fetchOpts = { credentials: 'include' };
  const postOpts = { credentials: 'include', headers: { 'Content-Type': 'application/json' } };

  const loadData = useCallback(async () => {
    try {
      const [historyRes, templatesRes, contactsRes] = await Promise.all([
        fetch(`${API}/api/talent-tools/outreach/history`, fetchOpts).then(r => r.ok ? r.json() : { messages: [] }),
        fetch(`${API}/api/talent-tools/outreach/templates`, fetchOpts).then(r => r.ok ? r.json() : { templates: [] }),
        fetch(`${API}/api/talent-crm/contacts`).then(r => r.ok ? r.json() : { contacts: [] })
      ]);
      setOutreachHistory(historyRes.messages || []);
      setTemplates(templatesRes.templates || []);
      setContacts(contactsRes.contacts || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const loadComments = async (contactId) => {
    try {
      const res = await fetch(`${API}/api/talent-tools/collaborate/comments/${contactId}`, fetchOpts);
      if (res.ok) { const d = await res.json(); setComments(d.comments || []); }
    } catch (e) { console.error(e); }
  };

  const addComment = async () => {
    if (!selectedCandidate || !newComment.trim()) return;
    setSending(true);
    try {
      const res = await fetch(`${API}/api/talent-tools/collaborate/comment`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify({ candidate_id: selectedCandidate.id, comment: newComment, mentions: [] })
      });
      if (res.ok) {
        const c = await res.json();
        setComments([c, ...comments]);
        setNewComment('');
      }
    } catch (e) { console.error(e); }
    setSending(false);
  };

  const reactToComment = async (commentId, emoji) => {
    try {
      await fetch(`${API}/api/talent-tools/collaborate/comment/${commentId}/react`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify({ emoji })
      });
    } catch (e) { console.error(e); }
  };

  const sendOutreach = async () => {
    if (!outreachMsg.trim()) return;
    setSending(true);
    try {
      const ids = selectedRecipients.length > 0 ? selectedRecipients.map(c => c.id) : ['broadcast'];
      const res = await fetch(`${API}/api/talent-tools/outreach/send`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify({ candidate_ids: ids, channel: outreachChannel, subject: outreachSubject, message: outreachMsg })
      });
      if (res.ok) {
        const d = await res.json();
        setOutreachHistory([d, ...outreachHistory]);
        setOutreachMsg(''); setOutreachSubject(''); setSelectedRecipients([]);
      }
    } catch (e) { console.error(e); }
    setSending(false);
  };

  const createTemplate = async () => {
    if (!templateForm.name || !templateForm.body) return;
    setCreatingTemplate(true);
    try {
      const res = await fetch(`${API}/api/talent-tools/outreach/templates`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify(templateForm)
      });
      if (res.ok) {
        const t = await res.json();
        setTemplates([t, ...templates]);
        setShowTemplateCreate(false);
        setTemplateForm({ name: '', channel: 'email', subject: '', body: '' });
      }
    } catch (e) { console.error(e); }
    setCreatingTemplate(false);
  };

  const useTemplate = (template) => {
    setOutreachChannel(template.channel);
    setOutreachSubject(template.subject || '');
    setOutreachMsg(template.body);
    setTab('outreach');
  };

  const toggleRecipient = (contact) => {
    setSelectedRecipients(prev =>
      prev.find(c => c.id === contact.id)
        ? prev.filter(c => c.id !== contact.id)
        : [...prev, contact]
    );
  };

  const filteredContacts = contacts.filter(c =>
    !candidateSearch || c.name?.toLowerCase().includes(candidateSearch.toLowerCase()) || c.email?.toLowerCase().includes(candidateSearch.toLowerCase())
  );

  // Stats
  const totalSent = outreachHistory.reduce((s, m) => s + (m.sent_count || 0), 0);
  const totalDelivered = outreachHistory.reduce((s, m) => s + (m.delivered_count || 0), 0);

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><Loader2 className="w-8 h-8 text-teal-400 animate-spin" /></div>;

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-violet-500/20 flex items-center justify-center">
              <Users className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-white" data-testid="team-outreach-title">Team & Outreach</h1>
              <p className="text-xs text-slate-400">Collaborate on candidates and manage multi-channel outreach</p>
            </div>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
          <StatCard label="Messages Sent" value={totalSent} icon={Send} accent="text-cyan-400" />
          <StatCard label="Delivered" value={totalDelivered} icon={Check} accent="text-emerald-400" />
          <StatCard label="Templates" value={templates.length} icon={FileText} accent="text-violet-400" />
          <StatCard label="Team Comments" value={comments.length} icon={MessageSquare} accent="text-amber-400" />
        </div>

        {/* Tab Nav */}
        <div className="flex gap-1.5 mb-5 border-b border-slate-800 pb-2">
          {[
            { id: 'collaborate', label: 'Collaborate', icon: MessageSquare },
            { id: 'outreach', label: 'Send Outreach', icon: Send },
            { id: 'templates', label: 'Templates', icon: FileText },
            { id: 'history', label: 'History', icon: Clock }
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all ${tab === t.id ? 'bg-cyan-600/15 text-cyan-400 font-medium' : 'text-slate-400 hover:text-slate-300'}`}
              data-testid={`tab-${t.id}`}>
              <t.icon className="w-4 h-4" /> {t.label}
            </button>
          ))}
        </div>

        {/* ====== COLLABORATE TAB ====== */}
        {tab === 'collaborate' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Contact Picker */}
            <div className="lg:col-span-1">
              <div className="mb-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <Input value={candidateSearch} onChange={e => setCandidateSearch(e.target.value)}
                    placeholder="Search candidates..." className="bg-slate-800/60 border-slate-700 text-white pl-9 h-9" data-testid="collab-search" />
                </div>
              </div>
              <ScrollArea className="h-[400px]">
                <div className="space-y-1.5">
                  {filteredContacts.map(c => (
                    <button key={c.id} onClick={() => { setSelectedCandidate(c); loadComments(c.id); }}
                      className={`w-full text-left p-2.5 rounded-lg border transition-all ${selectedCandidate?.id === c.id ? 'bg-slate-700/60 border-cyan-500/40' : 'bg-slate-800/40 border-slate-700/30 hover:border-slate-600'}`}
                      data-testid={`collab-contact-${c.id}`}>
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-500/30 to-violet-500/30 flex items-center justify-center text-xs font-bold text-cyan-300 shrink-0">
                          {c.name?.charAt(0)?.toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm text-white truncate">{c.name}</p>
                          <p className="text-[10px] text-slate-500 truncate">{c.title}</p>
                        </div>
                      </div>
                    </button>
                  ))}
                  {filteredContacts.length === 0 && <p className="text-slate-500 text-xs text-center py-8">No contacts found. Add contacts in Talent CRM.</p>}
                </div>
              </ScrollArea>
            </div>

            {/* Discussion Thread */}
            <div className="lg:col-span-2">
              {selectedCandidate ? (
                <Card className="bg-slate-800/60 border-slate-700/50">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-500/30 to-violet-500/30 flex items-center justify-center text-sm font-bold text-cyan-300">
                        {selectedCandidate.name?.charAt(0)?.toUpperCase()}
                      </div>
                      <div>
                        <CardTitle className="text-white text-sm">{selectedCandidate.name}</CardTitle>
                        <p className="text-xs text-slate-400">{selectedCandidate.title} {selectedCandidate.company ? `at ${selectedCandidate.company}` : ''}</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[280px] mb-3" data-testid="comment-thread">
                      {comments.length === 0 ? (
                        <p className="text-slate-500 text-sm text-center py-12">Start the discussion about this candidate</p>
                      ) : (
                        <div className="space-y-2">
                          {comments.map(c => (
                            <div key={c.id} className="p-3 rounded-lg bg-slate-700/40 border border-slate-700/30">
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-xs font-medium text-cyan-400">{c.author_name}</span>
                                <span className="text-[10px] text-slate-500">{new Date(c.created_at).toLocaleString()}</span>
                              </div>
                              <p className="text-sm text-slate-200">{c.comment}</p>
                              <div className="flex gap-1 mt-2">
                                {REACTIONS.map(r => (
                                  <button key={r.emoji} onClick={() => reactToComment(c.id, r.emoji)}
                                    className="p-1 rounded hover:bg-slate-600/40 text-slate-500 hover:text-slate-300 transition-colors"
                                    title={r.label}>
                                    <r.icon className="w-3 h-3" />
                                  </button>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </ScrollArea>
                    <div className="flex gap-2">
                      <Input value={newComment} onChange={e => setNewComment(e.target.value)} placeholder="Write a comment..."
                        className="bg-slate-700/50 border-slate-600 text-white text-sm" data-testid="collab-comment-input"
                        onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); addComment(); } }} />
                      <Button size="sm" className="bg-cyan-600 hover:bg-cyan-500 h-9" onClick={addComment} disabled={sending || !newComment.trim()} data-testid="add-comment-btn">
                        {sending ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <div className="flex items-center justify-center h-80 text-slate-500 rounded-lg border border-dashed border-slate-700/50">
                  <div className="text-center">
                    <MessageSquare className="w-10 h-10 mx-auto mb-3 opacity-15" />
                    <p className="text-sm">Select a candidate to start collaborating</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ====== OUTREACH TAB ====== */}
        {tab === 'outreach' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Recipient Picker */}
            <div className="lg:col-span-1">
              <h3 className="text-xs font-medium text-slate-400 mb-2">Select Recipients ({selectedRecipients.length})</h3>
              <ScrollArea className="h-[350px]">
                <div className="space-y-1">
                  {contacts.map(c => {
                    const isSelected = selectedRecipients.find(r => r.id === c.id);
                    return (
                      <button key={c.id} onClick={() => toggleRecipient(c)}
                        className={`w-full text-left p-2 rounded-lg border transition-all flex items-center gap-2 ${isSelected ? 'bg-cyan-500/10 border-cyan-500/40' : 'bg-slate-800/40 border-slate-700/30 hover:border-slate-600'}`}
                        data-testid={`recipient-${c.id}`}>
                        <div className={`w-4 h-4 rounded border flex items-center justify-center ${isSelected ? 'bg-cyan-500 border-cyan-500' : 'border-slate-600'}`}>
                          {isSelected && <Check className="w-2.5 h-2.5 text-white" />}
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs text-white truncate">{c.name}</p>
                          <p className="text-[10px] text-slate-500 truncate">{c.email}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </ScrollArea>
            </div>

            {/* Compose */}
            <div className="lg:col-span-2">
              <Card className="bg-slate-800/60 border-slate-700/50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-white text-sm flex items-center gap-2"><Send className="w-4 h-4 text-cyan-400" /> Compose Message</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-2">
                    {Object.entries(CHANNEL_CONFIG).map(([key, cfg]) => (
                      <button key={key} onClick={() => setOutreachChannel(key)}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs transition-all ${outreachChannel === key ? `border-cyan-500 text-cyan-400 bg-cyan-500/10` : 'border-slate-700 text-slate-500'}`}>
                        <cfg.icon className="w-3 h-3" /> {cfg.label}
                      </button>
                    ))}
                  </div>
                  {outreachChannel === 'email' && (
                    <Input value={outreachSubject} onChange={e => setOutreachSubject(e.target.value)}
                      placeholder="Subject line" className="bg-slate-700/50 border-slate-600 text-white text-sm" data-testid="outreach-subject" />
                  )}
                  {selectedRecipients.length > 0 && (
                    <div className="flex gap-1 flex-wrap">
                      <span className="text-[10px] text-slate-500">To:</span>
                      {selectedRecipients.map(r => (
                        <span key={r.id} className="px-1.5 py-0.5 text-[10px] bg-cyan-500/10 text-cyan-400 rounded-full border border-cyan-500/30">
                          {r.name} <button onClick={() => toggleRecipient(r)} className="ml-0.5 text-cyan-300">×</button>
                        </span>
                      ))}
                    </div>
                  )}
                  <Textarea value={outreachMsg} onChange={e => setOutreachMsg(e.target.value)}
                    placeholder="Write your message... Use {{name}} for personalization"
                    className="bg-slate-700/50 border-slate-600 text-white text-sm min-h-[150px]" data-testid="outreach-message" />
                  <div className="flex items-center justify-between">
                    <p className="text-[10px] text-slate-500">
                      {selectedRecipients.length > 0 ? `Sending to ${selectedRecipients.length} recipient(s)` : 'No recipients selected — will send as broadcast'}
                    </p>
                    <Button className="bg-cyan-600 hover:bg-cyan-500" onClick={sendOutreach} disabled={sending || !outreachMsg.trim()} data-testid="send-outreach-btn">
                      {sending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />} Send
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* ====== TEMPLATES TAB ====== */}
        {tab === 'templates' && (
          <div>
            <div className="flex justify-end mb-4">
              <Button size="sm" className="bg-violet-600 hover:bg-violet-500 h-8 text-xs" onClick={() => setShowTemplateCreate(true)} data-testid="create-template-btn">
                <Plus className="w-3 h-3 mr-1" /> New Template
              </Button>
            </div>

            <Dialog open={showTemplateCreate} onOpenChange={setShowTemplateCreate}>
              <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-lg">
                <DialogHeader><DialogTitle>Create Outreach Template</DialogTitle></DialogHeader>
                <div className="space-y-3">
                  <Input value={templateForm.name} onChange={e => setTemplateForm({ ...templateForm, name: e.target.value })}
                    placeholder="Template name *" className="bg-slate-700 border-slate-600 text-white" data-testid="template-name-input" />
                  <Select value={templateForm.channel} onValueChange={v => setTemplateForm({ ...templateForm, channel: v })}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="sms">SMS</SelectItem>
                      <SelectItem value="inmail">InMail</SelectItem>
                    </SelectContent>
                  </Select>
                  {templateForm.channel === 'email' && (
                    <Input value={templateForm.subject} onChange={e => setTemplateForm({ ...templateForm, subject: e.target.value })}
                      placeholder="Subject line" className="bg-slate-700 border-slate-600 text-white" />
                  )}
                  <Textarea value={templateForm.body} onChange={e => setTemplateForm({ ...templateForm, body: e.target.value })}
                    placeholder="Template body... Use {{name}}, {{title}}, {{company}} for personalization"
                    className="bg-slate-700 border-slate-600 text-white min-h-[120px]" data-testid="template-body-input" />
                </div>
                <DialogFooter>
                  <Button variant="ghost" className="text-slate-400" onClick={() => setShowTemplateCreate(false)}>Cancel</Button>
                  <Button className="bg-violet-600 hover:bg-violet-500" onClick={createTemplate} disabled={creatingTemplate || !templateForm.name || !templateForm.body} data-testid="save-template-btn">
                    {creatingTemplate ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : null} Save Template
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="templates-grid">
              {templates.length === 0 ? (
                <div className="col-span-full text-center py-12 text-slate-500">
                  <FileText className="w-10 h-10 mx-auto mb-3 opacity-15" />
                  <p className="text-sm">No templates yet. Create your first one.</p>
                </div>
              ) : templates.map(t => {
                const cfg = CHANNEL_CONFIG[t.channel] || CHANNEL_CONFIG.email;
                return (
                  <Card key={t.id} className="bg-slate-800/60 border-slate-700/50 hover:border-violet-500/30 transition-all group">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-sm font-medium text-white">{t.name}</h3>
                        <div className={`w-6 h-6 rounded flex items-center justify-center ${cfg.color}`}>
                          <cfg.icon className="w-3 h-3" />
                        </div>
                      </div>
                      {t.subject && <p className="text-xs text-slate-400 mb-1">Subject: {t.subject}</p>}
                      <p className="text-xs text-slate-500 line-clamp-3">{t.body}</p>
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" variant="ghost" className="h-6 text-[10px] text-cyan-400" onClick={() => useTemplate(t)} data-testid={`use-template-${t.id}`}>
                          <Copy className="w-2.5 h-2.5 mr-1" /> Use
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}

        {/* ====== HISTORY TAB ====== */}
        {tab === 'history' && (
          <div className="space-y-2" data-testid="outreach-history">
            {outreachHistory.length === 0 ? (
              <div className="text-center py-16 text-slate-500">
                <Clock className="w-10 h-10 mx-auto mb-3 opacity-15" />
                <p className="text-sm">No outreach sent yet. Go to Send Outreach to get started.</p>
              </div>
            ) : outreachHistory.map(m => {
              const cfg = CHANNEL_CONFIG[m.channel] || CHANNEL_CONFIG.email;
              return (
                <Card key={m.id} className="bg-slate-800/50 border-slate-700/40 hover:border-slate-600/60 transition-all">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 min-w-0 flex-1">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${cfg.color}`}>
                          <cfg.icon className="w-4 h-4" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm text-white truncate">{m.message?.substring(0, 80)}{m.message?.length > 80 ? '...' : ''}</p>
                          <div className="flex items-center gap-3 mt-0.5 text-xs text-slate-500">
                            <span>Sent to {m.sent_count} contact(s)</span>
                            <span>Delivered: {m.delivered_count}</span>
                            <span>Opened: {m.opened_count || 0}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right shrink-0 ml-3">
                        <Badge className="bg-emerald-500/20 text-emerald-400 text-[10px]">{m.status}</Badge>
                        <p className="text-[10px] text-slate-500 mt-1">{new Date(m.sent_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
