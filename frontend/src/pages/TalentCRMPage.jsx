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
  Users, Plus, FolderOpen, Send, Loader2, Tag, Trash2,
  Phone, Mail, Building2, Search, ChevronRight, ArrowLeft,
  MessageSquare, Calendar, UserPlus, Filter, MoreVertical, GripVertical,
  LayoutGrid, List
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const STAGES = ['new', 'contacted', 'screening', 'interview', 'offer', 'hired', 'rejected', 'archived'];
const STAGE_COLORS = {
  new: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  contacted: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  screening: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  interview: 'bg-violet-500/20 text-violet-400 border-violet-500/30',
  offer: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
  hired: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  rejected: 'bg-red-500/20 text-red-400 border-red-500/30',
  archived: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
};
const INTERACTION_ICONS = { call: Phone, email: Mail, meeting: Users, note: MessageSquare, linkedin: Building2 };

function PipelineBar({ pipeline }) {
  const total = pipeline.total || 1;
  return (
    <div className="flex items-center gap-0.5 h-8 rounded-lg overflow-hidden" data-testid="pipeline-bar">
      {STAGES.filter(s => (pipeline.stages?.[s] || 0) > 0).map(s => {
        const count = pipeline.stages[s];
        const pct = Math.max((count / total) * 100, 4);
        const colors = { new: '#3b82f6', contacted: '#06b6d4', screening: '#f59e0b', interview: '#8b5cf6', offer: '#14b8a6', hired: '#10b981', rejected: '#ef4444', archived: '#64748b' };
        return (
          <div key={s} style={{ width: `${pct}%`, background: colors[s] }}
            className="h-full flex items-center justify-center text-[10px] font-bold text-white min-w-[28px] transition-all"
            title={`${s}: ${count}`}>
            {count}
          </div>
        );
      })}
    </div>
  );
}

function ContactCard({ contact, onClick }) {
  return (
    <button onClick={onClick} className="w-full text-left group" data-testid={`contact-${contact.id}`}>
      <div className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 hover:border-teal-500/40 transition-all">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-teal-500/30 to-blue-500/30 flex items-center justify-center text-sm font-semibold text-teal-300 shrink-0">
              {contact.name?.charAt(0)?.toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-white truncate">{contact.name}</p>
              <p className="text-xs text-slate-400 truncate">{contact.title}{contact.company ? ` at ${contact.company}` : ''}</p>
            </div>
          </div>
          <Badge className={`text-[10px] shrink-0 ${STAGE_COLORS[contact.stage] || STAGE_COLORS.new}`}>{contact.stage}</Badge>
        </div>
        {contact.tags?.length > 0 && (
          <div className="flex gap-1 mt-2 flex-wrap">
            {contact.tags.slice(0, 3).map(t => <span key={t} className="px-1.5 py-0.5 text-[10px] bg-slate-700/60 text-slate-300 rounded">{t}</span>)}
          </div>
        )}
      </div>
    </button>
  );
}

function ContactDetail({ contact, onBack, onUpdate, onDelete }) {
  const [interactions, setInteractions] = useState([]);
  const [interactionForm, setInteractionForm] = useState({ type: 'note', summary: '', outcome: '' });
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    fetch(`${API}/api/talent-crm/interactions/${contact.id}`).then(r => r.json()).then(d => setInteractions(d.interactions || [])).catch(() => {});
  }, [contact.id]);

  const addInteraction = async () => {
    if (!interactionForm.summary.trim()) return;
    setAdding(true);
    try {
      const res = await fetch(`${API}/api/talent-crm/interactions`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contact_id: contact.id, interaction_type: interactionForm.type, summary: interactionForm.summary, outcome: interactionForm.outcome })
      });
      if (res.ok) {
        const i = await res.json();
        setInteractions([i, ...interactions]);
        setInteractionForm({ type: 'note', summary: '', outcome: '' });
      }
    } catch (e) { console.error(e); }
    setAdding(false);
  };

  const changeStage = async (stage) => {
    try {
      await fetch(`${API}/api/talent-crm/contacts/${contact.id}/stage`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stage })
      });
      onUpdate({ ...contact, stage });
    } catch (e) { console.error(e); }
  };

  const saveEdit = async () => {
    try {
      const res = await fetch(`${API}/api/talent-crm/contacts/${contact.id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm)
      });
      if (res.ok) {
        const updated = await res.json();
        onUpdate(updated);
        setEditing(false);
      }
    } catch (e) { console.error(e); }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" className="text-slate-400 h-8" onClick={onBack} data-testid="back-to-list">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back
        </Button>
      </div>

      {/* Contact Header */}
      <Card className="bg-slate-800/80 border-slate-700/60">
        <CardContent className="p-5">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-teal-500/40 to-blue-500/40 flex items-center justify-center text-lg font-bold text-teal-300">
                {contact.name?.charAt(0)?.toUpperCase()}
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white" data-testid="contact-detail-name">{contact.name}</h2>
                <p className="text-sm text-slate-400">{contact.title}{contact.company ? ` at ${contact.company}` : ''}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" className="h-7 text-xs border-slate-600 text-slate-300" onClick={() => { setEditForm({ name: contact.name, email: contact.email, phone: contact.phone, title: contact.title, company: contact.company, tags: contact.tags, notes: contact.notes }); setEditing(true); }} data-testid="edit-contact-btn">Edit</Button>
              <Button size="sm" variant="ghost" className="h-7 text-xs text-red-400 hover:text-red-300" onClick={() => onDelete(contact.id)} data-testid="delete-contact-btn"><Trash2 className="w-3 h-3" /></Button>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            {contact.email && <div className="flex items-center gap-1.5 text-slate-300"><Mail className="w-3.5 h-3.5 text-slate-500" />{contact.email}</div>}
            {contact.phone && <div className="flex items-center gap-1.5 text-slate-300"><Phone className="w-3.5 h-3.5 text-slate-500" />{contact.phone}</div>}
            <div className="flex items-center gap-1.5 text-slate-300"><Tag className="w-3.5 h-3.5 text-slate-500" />Source: {contact.source || 'manual'}</div>
            <div className="flex items-center gap-1.5 text-slate-300"><Calendar className="w-3.5 h-3.5 text-slate-500" />{contact.interactions_count || 0} interactions</div>
          </div>
          {/* Pipeline Stage Selector */}
          <div className="mt-4">
            <p className="text-xs text-slate-500 mb-2">Pipeline Stage</p>
            <div className="flex gap-1 flex-wrap">
              {STAGES.map(s => (
                <button key={s} onClick={() => changeStage(s)}
                  className={`px-2.5 py-1 text-xs rounded-full border transition-all ${contact.stage === s ? STAGE_COLORS[s] : 'border-slate-700 text-slate-500 hover:border-slate-500'}`}
                  data-testid={`stage-${s}`}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Add Interaction */}
      <Card className="bg-slate-800/60 border-slate-700/50">
        <CardContent className="p-4">
          <h3 className="text-sm font-medium text-slate-300 mb-3">Log Interaction</h3>
          <div className="flex gap-2 mb-2">
            {['note', 'call', 'email', 'meeting', 'linkedin'].map(t => (
              <button key={t} onClick={() => setInteractionForm({ ...interactionForm, type: t })}
                className={`px-2.5 py-1 text-xs rounded-full border transition-all capitalize ${interactionForm.type === t ? 'border-teal-500 text-teal-400 bg-teal-500/10' : 'border-slate-700 text-slate-500'}`}>
                {t}
              </button>
            ))}
          </div>
          <Textarea value={interactionForm.summary} onChange={e => setInteractionForm({ ...interactionForm, summary: e.target.value })}
            placeholder="What happened?" className="bg-slate-700/50 border-slate-600 text-white text-sm mb-2 min-h-[60px]" data-testid="interaction-summary" />
          <div className="flex gap-2">
            <Input value={interactionForm.outcome} onChange={e => setInteractionForm({ ...interactionForm, outcome: e.target.value })}
              placeholder="Outcome (optional)" className="bg-slate-700/50 border-slate-600 text-white text-sm flex-1" />
            <Button size="sm" className="bg-teal-600 hover:bg-teal-500" onClick={addInteraction} disabled={adding || !interactionForm.summary.trim()} data-testid="add-interaction-btn">
              {adding ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3 mr-1" />} Log
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Interaction Timeline */}
      <div>
        <h3 className="text-sm font-medium text-slate-400 mb-3">Activity Timeline</h3>
        {interactions.length === 0 ? (
          <p className="text-center text-slate-600 py-8 text-sm">No interactions logged yet</p>
        ) : (
          <div className="space-y-2" data-testid="interactions-timeline">
            {interactions.map((i, idx) => {
              const Icon = INTERACTION_ICONS[i.type] || MessageSquare;
              return (
                <div key={i.id || idx} className="flex gap-3 p-3 rounded-lg bg-slate-800/40 border border-slate-700/30">
                  <div className="w-7 h-7 rounded-full bg-slate-700/60 flex items-center justify-center shrink-0">
                    <Icon className="w-3.5 h-3.5 text-teal-400" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-0.5">
                      <Badge className="text-[10px] bg-slate-700/60 text-slate-300 capitalize">{i.type}</Badge>
                      <span className="text-[10px] text-slate-500">{new Date(i.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="text-sm text-slate-200">{i.summary}</p>
                    {i.outcome && <p className="text-xs text-slate-400 mt-1">Outcome: {i.outcome}</p>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog open={editing} onOpenChange={setEditing}>
        <DialogContent className="bg-slate-800 border-slate-700 text-white">
          <DialogHeader><DialogTitle>Edit Contact</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <Input value={editForm.name || ''} onChange={e => setEditForm({ ...editForm, name: e.target.value })} placeholder="Name" className="bg-slate-700 border-slate-600 text-white" />
            <Input value={editForm.email || ''} onChange={e => setEditForm({ ...editForm, email: e.target.value })} placeholder="Email" className="bg-slate-700 border-slate-600 text-white" />
            <Input value={editForm.phone || ''} onChange={e => setEditForm({ ...editForm, phone: e.target.value })} placeholder="Phone" className="bg-slate-700 border-slate-600 text-white" />
            <Input value={editForm.title || ''} onChange={e => setEditForm({ ...editForm, title: e.target.value })} placeholder="Title" className="bg-slate-700 border-slate-600 text-white" />
            <Input value={editForm.company || ''} onChange={e => setEditForm({ ...editForm, company: e.target.value })} placeholder="Company" className="bg-slate-700 border-slate-600 text-white" />
          </div>
          <DialogFooter>
            <Button variant="ghost" className="text-slate-400" onClick={() => setEditing(false)}>Cancel</Button>
            <Button className="bg-teal-600 hover:bg-teal-500" onClick={saveEdit} data-testid="save-edit-btn">Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function TalentCRMPage() {
  const [contacts, setContacts] = useState([]);
  const [pools, setPools] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [pipeline, setPipeline] = useState({ stages: {}, total: 0 });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('contacts');
  const [selectedContact, setSelectedContact] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('all');
  const [form, setForm] = useState({ name: '', email: '', phone: '', title: '', company: '', source: 'manual', stage: 'new', tags: '', notes: '' });
  const [showPoolCreate, setShowPoolCreate] = useState(false);
  const [poolForm, setPoolForm] = useState({ name: '', description: '', tags: '' });
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'kanban'
  const [dragContact, setDragContact] = useState(null);

  const loadData = useCallback(async () => {
    try {
      const [contactsRes, poolsRes, campaignsRes, pipelineRes] = await Promise.all([
        fetch(`${API}/api/talent-crm/contacts?stage=${stageFilter}&search=${search}`).then(r => r.json()),
        fetch(`${API}/api/talent-crm/pools`).then(r => r.json()),
        fetch(`${API}/api/talent-crm/campaigns`).then(r => r.json()),
        fetch(`${API}/api/talent-crm/pipeline`).then(r => r.json())
      ]);
      setContacts(contactsRes.contacts || []);
      setPools(poolsRes.pools || []);
      setCampaigns(campaignsRes.campaigns || []);
      setPipeline(pipelineRes);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [stageFilter, search]);

  useEffect(() => { loadData(); }, [loadData]);

  const createContact = async () => {
    if (!form.name.trim()) return;
    try {
      const res = await fetch(`${API}/api/talent-crm/contacts`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, tags: form.tags.split(',').map(t => t.trim()).filter(Boolean) })
      });
      if (res.ok) {
        const c = await res.json();
        setContacts([c, ...contacts]);
        setForm({ name: '', email: '', phone: '', title: '', company: '', source: 'manual', stage: 'new', tags: '', notes: '' });
        setShowCreate(false);
        loadData();
      }
    } catch (e) { console.error(e); }
  };

  const deleteContact = async (id) => {
    try {
      await fetch(`${API}/api/talent-crm/contacts/${id}`, { method: 'DELETE' });
      setContacts(contacts.filter(c => c.id !== id));
      setSelectedContact(null);
      loadData();
    } catch (e) { console.error(e); }
  };

  const createPool = async () => {
    if (!poolForm.name.trim()) return;
    try {
      const res = await fetch(`${API}/api/talent-crm/pools`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...poolForm, tags: poolForm.tags.split(',').map(t => t.trim()).filter(Boolean) })
      });
      if (res.ok) {
        const p = await res.json();
        setPools([p, ...pools]);
        setPoolForm({ name: '', description: '', tags: '' });
        setShowPoolCreate(false);
      }
    } catch (e) { console.error(e); }
  };

  const deletePool = async (poolId) => {
    try {
      await fetch(`${API}/api/talent-crm/pools/${poolId}`, { method: 'DELETE' });
      setPools(pools.filter(p => p.pool_id !== poolId));
    } catch (e) { console.error(e); }
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><Loader2 className="w-8 h-8 text-teal-400 animate-spin" /></div>;

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500/20 to-blue-500/20 flex items-center justify-center">
              <Users className="w-5 h-5 text-teal-400" />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-white" data-testid="crm-page-title">Talent CRM</h1>
              <p className="text-xs text-slate-400">{pipeline.total} contacts across your pipeline</p>
            </div>
          </div>
          <Button className="bg-teal-600 hover:bg-teal-500 text-sm h-9" onClick={() => setShowCreate(true)} data-testid="create-contact-btn">
            <UserPlus className="w-4 h-4 mr-1.5" /> Add Contact
          </Button>
        </div>

        {/* Pipeline Overview */}
        {pipeline.total > 0 && (
          <div className="mb-5">
            <PipelineBar pipeline={pipeline} />
            <div className="flex gap-2 mt-2 flex-wrap">
              {STAGES.map(s => (pipeline.stages?.[s] || 0) > 0 && (
                <button key={s} onClick={() => { setStageFilter(s === stageFilter ? 'all' : s); }}
                  className={`text-[10px] px-2 py-0.5 rounded-full border transition-all capitalize ${stageFilter === s ? STAGE_COLORS[s] : 'border-slate-700 text-slate-500'}`}>
                  {s} ({pipeline.stages[s]})
                </button>
              ))}
              {stageFilter !== 'all' && (
                <button onClick={() => setStageFilter('all')} className="text-[10px] px-2 py-0.5 rounded-full border border-slate-700 text-slate-400">All</button>
              )}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1.5 mb-5 border-b border-slate-800 pb-2">
          {[{ id: 'contacts', label: 'Contacts', icon: Users }, { id: 'pools', label: 'Pools', icon: FolderOpen }, { id: 'campaigns', label: 'Campaigns', icon: Send }].map(tab => (
            <button key={tab.id} onClick={() => { setActiveTab(tab.id); setSelectedContact(null); }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-all ${activeTab === tab.id ? 'bg-teal-600/15 text-teal-400 font-medium' : 'text-slate-400 hover:text-slate-300'}`}
              data-testid={`tab-${tab.id}`}>
              <tab.icon className="w-4 h-4" /> {tab.label}
            </button>
          ))}
        </div>

        {/* Create Contact Dialog */}
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-lg">
            <DialogHeader><DialogTitle>New Contact</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Full name *" className="bg-slate-700 border-slate-600 text-white" data-testid="contact-name-input" />
                <Input value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="Email" className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} placeholder="Phone" className="bg-slate-700 border-slate-600 text-white" />
                <Input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} placeholder="Job title" className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input value={form.company} onChange={e => setForm({ ...form, company: e.target.value })} placeholder="Company" className="bg-slate-700 border-slate-600 text-white" />
                <Select value={form.source} onValueChange={v => setForm({ ...form, source: v })}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {['manual', 'linkedin', 'referral', 'job_board', 'career_fair', 'inbound'].map(s => (
                      <SelectItem key={s} value={s}>{s.replace('_', ' ')}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Input value={form.tags} onChange={e => setForm({ ...form, tags: e.target.value })} placeholder="Tags (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
              <Textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Notes" className="bg-slate-700 border-slate-600 text-white min-h-[60px]" />
            </div>
            <DialogFooter>
              <Button variant="ghost" className="text-slate-400" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button className="bg-teal-600 hover:bg-teal-500" onClick={createContact} disabled={!form.name.trim()} data-testid="save-contact-btn">Create Contact</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* CONTACTS TAB */}
        {activeTab === 'contacts' && !selectedContact && (
          <div>
            <div className="mb-4 flex items-center gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search contacts..."
                  className="bg-slate-800/60 border-slate-700 text-white pl-9 h-9" data-testid="search-contacts" />
              </div>
              <div className="flex gap-0.5 bg-slate-800/60 rounded-lg p-0.5 border border-slate-700/50">
                <button onClick={() => setViewMode('list')}
                  className={`p-1.5 rounded transition-all ${viewMode === 'list' ? 'bg-teal-600/20 text-teal-400' : 'text-slate-500 hover:text-slate-300'}`}
                  data-testid="view-list-btn" title="List view">
                  <List className="w-4 h-4" />
                </button>
                <button onClick={() => setViewMode('kanban')}
                  className={`p-1.5 rounded transition-all ${viewMode === 'kanban' ? 'bg-teal-600/20 text-teal-400' : 'text-slate-500 hover:text-slate-300'}`}
                  data-testid="view-kanban-btn" title="Kanban board">
                  <LayoutGrid className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* List View */}
            {viewMode === 'list' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2" data-testid="contacts-grid">
                {contacts.length === 0 ? (
                  <div className="col-span-full text-center py-16 text-slate-500">
                    <Users className="w-10 h-10 mx-auto mb-3 opacity-20" />
                    <p className="text-sm">No contacts yet. Add your first candidate.</p>
                  </div>
                ) : contacts.map(c => (
                  <ContactCard key={c.id} contact={c} onClick={() => setSelectedContact(c)} />
                ))}
              </div>
            )}

            {/* Kanban Board View */}
            {viewMode === 'kanban' && (
              <div className="flex gap-2.5 overflow-x-auto pb-4" data-testid="kanban-board">
                {STAGES.filter(s => s !== 'archived').map(stage => {
                  const stageContacts = contacts.filter(c => c.stage === stage);
                  const STAGE_HEADER_COLORS = {
                    new: 'border-t-blue-500', contacted: 'border-t-cyan-500', screening: 'border-t-amber-500',
                    interview: 'border-t-violet-500', offer: 'border-t-teal-500', hired: 'border-t-emerald-500', rejected: 'border-t-red-500'
                  };
                  return (
                    <div
                      key={stage}
                      className={`min-w-[220px] w-[220px] shrink-0 rounded-lg bg-slate-800/40 border border-slate-700/40 border-t-2 ${STAGE_HEADER_COLORS[stage] || 'border-t-slate-500'}`}
                      onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('ring-1', 'ring-teal-500/50'); }}
                      onDragLeave={(e) => { e.currentTarget.classList.remove('ring-1', 'ring-teal-500/50'); }}
                      onDrop={async (e) => {
                        e.preventDefault();
                        e.currentTarget.classList.remove('ring-1', 'ring-teal-500/50');
                        if (dragContact && dragContact.stage !== stage) {
                          try {
                            await fetch(`${API}/api/talent-crm/contacts/${dragContact.id}/stage`, {
                              method: 'PUT', headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ stage })
                            });
                            setContacts(contacts.map(c => c.id === dragContact.id ? { ...c, stage } : c));
                            setPipeline(prev => {
                              const newStages = { ...prev.stages };
                              newStages[dragContact.stage] = Math.max((newStages[dragContact.stage] || 0) - 1, 0);
                              newStages[stage] = (newStages[stage] || 0) + 1;
                              return { ...prev, stages: newStages };
                            });
                          } catch (err) { console.error(err); }
                          setDragContact(null);
                        }
                      }}
                      data-testid={`kanban-col-${stage}`}
                    >
                      {/* Column Header */}
                      <div className="p-2.5 border-b border-slate-700/30">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-slate-300 capitalize">{stage}</span>
                          <span className="text-[10px] text-slate-500 bg-slate-700/50 px-1.5 py-0.5 rounded-full">{stageContacts.length}</span>
                        </div>
                      </div>
                      {/* Column Cards */}
                      <div className="p-1.5 space-y-1.5 min-h-[100px]">
                        {stageContacts.map(c => (
                          <div
                            key={c.id}
                            draggable
                            onDragStart={() => setDragContact(c)}
                            onDragEnd={() => setDragContact(null)}
                            onClick={() => setSelectedContact(c)}
                            className="p-2 rounded-md bg-slate-700/40 border border-slate-600/30 cursor-grab active:cursor-grabbing hover:border-teal-500/30 transition-all group"
                            data-testid={`kanban-card-${c.id}`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              <GripVertical className="w-3 h-3 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                              <div className="w-6 h-6 rounded-full bg-gradient-to-br from-teal-500/30 to-blue-500/30 flex items-center justify-center text-[10px] font-bold text-teal-300 shrink-0">
                                {c.name?.charAt(0)?.toUpperCase()}
                              </div>
                              <p className="text-xs text-white truncate font-medium">{c.name}</p>
                            </div>
                            <p className="text-[10px] text-slate-500 truncate ml-8">{c.title}</p>
                            {c.tags?.length > 0 && (
                              <div className="flex gap-0.5 mt-1 ml-8">
                                {c.tags.slice(0, 2).map(t => <span key={t} className="px-1 py-0 text-[8px] bg-slate-600/40 text-slate-400 rounded">{t}</span>)}
                              </div>
                            )}
                          </div>
                        ))}
                        {stageContacts.length === 0 && (
                          <div className="text-center py-6 text-slate-600">
                            <p className="text-[10px]">Drop here</p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {activeTab === 'contacts' && selectedContact && (
          <ContactDetail
            contact={selectedContact}
            onBack={() => { setSelectedContact(null); loadData(); }}
            onUpdate={(updated) => { setSelectedContact(updated); setContacts(contacts.map(c => c.id === updated.id ? updated : c)); }}
            onDelete={deleteContact}
          />
        )}

        {/* POOLS TAB */}
        {activeTab === 'pools' && (
          <div>
            <div className="flex justify-end mb-4">
              <Button size="sm" className="bg-teal-600 hover:bg-teal-500 h-8 text-xs" onClick={() => setShowPoolCreate(true)} data-testid="create-pool-btn">
                <Plus className="w-3 h-3 mr-1" /> New Pool
              </Button>
            </div>
            <Dialog open={showPoolCreate} onOpenChange={setShowPoolCreate}>
              <DialogContent className="bg-slate-800 border-slate-700 text-white">
                <DialogHeader><DialogTitle>Create Talent Pool</DialogTitle></DialogHeader>
                <div className="space-y-3">
                  <Input value={poolForm.name} onChange={e => setPoolForm({ ...poolForm, name: e.target.value })} placeholder="Pool name *" className="bg-slate-700 border-slate-600 text-white" data-testid="pool-name-input" />
                  <Textarea value={poolForm.description} onChange={e => setPoolForm({ ...poolForm, description: e.target.value })} placeholder="Description" className="bg-slate-700 border-slate-600 text-white" />
                  <Input value={poolForm.tags} onChange={e => setPoolForm({ ...poolForm, tags: e.target.value })} placeholder="Tags (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
                </div>
                <DialogFooter>
                  <Button variant="ghost" className="text-slate-400" onClick={() => setShowPoolCreate(false)}>Cancel</Button>
                  <Button className="bg-teal-600 hover:bg-teal-500" onClick={createPool} data-testid="save-pool-btn">Create Pool</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="pools-grid">
              {pools.length === 0 ? (
                <div className="col-span-full text-center py-12 text-slate-500">
                  <FolderOpen className="w-10 h-10 mx-auto mb-3 opacity-20" />
                  <p className="text-sm">No talent pools yet.</p>
                </div>
              ) : pools.map(pool => (
                <Card key={pool.pool_id} className="bg-slate-800/60 border-slate-700/50 hover:border-teal-500/30 transition-colors group">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-sm font-medium text-white">{pool.name}</h3>
                      <Button size="sm" variant="ghost" className="h-6 w-6 p-0 text-slate-500 opacity-0 group-hover:opacity-100" onClick={() => deletePool(pool.pool_id)}>
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                    {pool.description && <p className="text-xs text-slate-400 mb-3">{pool.description}</p>}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 flex items-center gap-1"><Users className="w-3 h-3" /> {pool.candidate_count || 0}</span>
                      <div className="flex gap-1">
                        {(pool.tags || []).slice(0, 2).map(t => <span key={t} className="text-[10px] px-1.5 py-0.5 bg-slate-700/60 text-slate-300 rounded">{t}</span>)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* CAMPAIGNS TAB */}
        {activeTab === 'campaigns' && (
          <div className="space-y-3" data-testid="campaigns-list">
            {campaigns.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Send className="w-10 h-10 mx-auto mb-3 opacity-20" />
                <p className="text-sm">No nurture campaigns yet.</p>
              </div>
            ) : campaigns.map(c => (
              <Card key={c.campaign_id} className="bg-slate-800/60 border-slate-700/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-white">{c.name}</h3>
                      <p className="text-xs text-slate-400 mt-1">
                        Sent: {c.sent_count} | Opened: {c.open_count} | Replied: {c.reply_count}
                      </p>
                    </div>
                    <Badge className={c.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-600/30 text-slate-300'}>{c.status}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
