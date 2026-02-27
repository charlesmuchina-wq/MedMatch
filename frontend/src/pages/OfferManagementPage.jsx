import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import {
  FileText, DollarSign, Calendar, Send, Plus, Loader2, Sparkles,
  Check, Clock, X, AlertCircle, ChevronRight, ArrowUpRight,
  ArrowDownRight, Briefcase, User, Eye
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const STATUS_CONFIG = {
  draft: { color: 'bg-slate-500/20 text-slate-400 border-slate-500/30', icon: FileText, label: 'Draft' },
  pending_approval: { color: 'bg-amber-500/20 text-amber-400 border-amber-500/30', icon: Clock, label: 'Pending' },
  approved: { color: 'bg-blue-500/20 text-blue-400 border-blue-500/30', icon: Check, label: 'Approved' },
  sent: { color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30', icon: Send, label: 'Sent' },
  negotiating: { color: 'bg-violet-500/20 text-violet-400 border-violet-500/30', icon: AlertCircle, label: 'Negotiating' },
  accepted: { color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30', icon: Check, label: 'Accepted' },
  declined: { color: 'bg-red-500/20 text-red-400 border-red-500/30', icon: X, label: 'Declined' },
  withdrawn: { color: 'bg-orange-500/20 text-orange-400 border-orange-500/30', icon: X, label: 'Withdrawn' },
};

const STATUS_FLOW = {
  draft: ['pending_approval', 'sent', 'withdrawn'],
  pending_approval: ['approved', 'withdrawn'],
  approved: ['sent', 'withdrawn'],
  sent: ['negotiating', 'accepted', 'declined', 'withdrawn'],
  negotiating: ['sent', 'accepted', 'declined', 'withdrawn'],
  accepted: [],
  declined: [],
  withdrawn: [],
};

function StatBadge({ label, value, icon: Icon, accent }) {
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

function OfferTimeline({ timeline }) {
  if (!timeline?.length) return null;
  return (
    <div className="space-y-2 mt-3">
      <h4 className="text-xs font-medium text-slate-400">Activity Timeline</h4>
      {timeline.map((e, i) => (
        <div key={i} className="flex items-start gap-2.5 text-xs">
          <div className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 shrink-0" />
          <div>
            <span className="text-slate-300 capitalize">{e.action.replace(/_/g, ' ')}</span>
            {e.by && <span className="text-slate-500 ml-1">by {e.by}</span>}
            <span className="text-slate-600 ml-2">{new Date(e.at).toLocaleDateString()}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function OfferDetail({ offer, onClose, onUpdate, onGenerateLetter }) {
  const [generatingLetter, setGeneratingLetter] = useState(false);
  const [letterContent, setLetterContent] = useState('');
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  const genLetter = async () => {
    setGeneratingLetter(true);
    try {
      const res = await fetch(`${API}/api/advanced/offers/${offer.id}/generate-letter`, { method: 'POST', headers });
      if (res.ok) { const d = await res.json(); setLetterContent(d.letter); }
    } catch (e) { console.error(e); }
    setGeneratingLetter(false);
  };

  const changeStatus = async (status) => {
    try {
      await fetch(`${API}/api/advanced/offers/${offer.id}/status`, {
        method: 'PUT', headers, body: JSON.stringify({ status })
      });
      onUpdate({ ...offer, status });
    } catch (e) { console.error(e); }
  };

  const nextStatuses = STATUS_FLOW[offer.status] || [];

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span>{offer.candidate_name}</span>
            <ChevronRight className="w-3 h-3 text-slate-500" />
            <span className="text-slate-400 font-normal">{offer.job_title}</span>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Status & Actions */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className={`${STATUS_CONFIG[offer.status]?.color || 'bg-slate-600'} text-xs`} data-testid="offer-detail-status">
              {STATUS_CONFIG[offer.status]?.label || offer.status}
            </Badge>
            {nextStatuses.map(s => (
              <Button key={s} size="sm" variant="outline" className="h-6 text-[10px] border-slate-600 text-slate-300 capitalize"
                onClick={() => changeStatus(s)} data-testid={`action-${s}`}>
                {STATUS_CONFIG[s]?.label || s}
              </Button>
            ))}
          </div>

          {/* Offer Details Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <StatBadge label="Salary" value={`${offer.currency} ${offer.salary?.toLocaleString()}`} icon={DollarSign} accent="text-emerald-400" />
            {offer.bonus > 0 && <StatBadge label="Bonus" value={`${offer.currency} ${offer.bonus?.toLocaleString()}`} icon={DollarSign} accent="text-amber-400" />}
            {offer.equity && <StatBadge label="Equity" value={offer.equity} icon={Briefcase} accent="text-violet-400" />}
            {offer.start_date && <StatBadge label="Start Date" value={offer.start_date} icon={Calendar} accent="text-blue-400" />}
            {offer.hiring_manager && <StatBadge label="Hiring Manager" value={offer.hiring_manager} icon={User} accent="text-cyan-400" />}
          </div>

          {/* Benefits */}
          {offer.benefits?.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-slate-400 mb-1.5">Benefits</h4>
              <div className="flex gap-1.5 flex-wrap">
                {offer.benefits.map(b => <span key={b} className="px-2 py-0.5 text-xs bg-slate-700/60 text-slate-300 rounded">{b}</span>)}
              </div>
            </div>
          )}

          {/* Notes */}
          {offer.notes && (
            <div>
              <h4 className="text-xs font-medium text-slate-400 mb-1">Notes</h4>
              <p className="text-sm text-slate-300">{offer.notes}</p>
            </div>
          )}

          {/* Timeline */}
          <OfferTimeline timeline={offer.timeline} />

          {/* AI Letter */}
          <div className="border-t border-slate-700 pt-3">
            <Button size="sm" className="bg-violet-600 hover:bg-violet-500 text-xs" onClick={genLetter} disabled={generatingLetter} data-testid="gen-letter-detail">
              {generatingLetter ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Sparkles className="w-3 h-3 mr-1" />} Generate AI Offer Letter
            </Button>
            {letterContent && (
              <div className="mt-3 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                <pre className="whitespace-pre-wrap text-xs text-slate-300 font-sans leading-relaxed" data-testid="offer-letter-detail">{letterContent}</pre>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default function OfferManagementPage() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedOffer, setSelectedOffer] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [form, setForm] = useState({
    candidate_name: '', job_title: '', salary: '', currency: 'USD',
    start_date: '', benefits: '', notes: '', equity: '', bonus: '', hiring_manager: ''
  });
  const fetchOpts = { credentials: 'include' };
  const postOpts = { credentials: 'include', headers: { 'Content-Type': 'application/json' } };

  useEffect(() => {
    fetch(`${API}/api/advanced/offers`, fetchOpts).then(r => r.ok ? r.json() : { offers: [] }).then(d => { setOffers(d.offers || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const createOffer = async () => {
    if (!form.candidate_name || !form.job_title || !form.salary) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/advanced/offers`, {
        method: 'POST', ...postOpts,
        body: JSON.stringify({
          ...form, salary: parseFloat(form.salary), bonus: parseFloat(form.bonus) || 0,
          candidate_id: '', job_id: '',
          benefits: form.benefits.split(',').map(b => b.trim()).filter(Boolean)
        })
      });
      if (res.ok) {
        const o = await res.json();
        setOffers([o, ...offers]);
        setShowCreate(false);
        setForm({ candidate_name: '', job_title: '', salary: '', currency: 'USD', start_date: '', benefits: '', notes: '', equity: '', bonus: '', hiring_manager: '' });
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const updateStatus = async (offerId, status) => {
    try {
      await fetch(`${API}/api/advanced/offers/${offerId}/status`, { method: 'PUT', ...postOpts, body: JSON.stringify({ status }) });
      setOffers(offers.map(o => o.id === offerId ? { ...o, status } : o));
    } catch (e) { console.error(e); }
  };

  const filtered = statusFilter === 'all' ? offers : offers.filter(o => o.status === statusFilter);

  // Stats
  const stats = {
    total: offers.length,
    accepted: offers.filter(o => o.status === 'accepted').length,
    pending: offers.filter(o => ['draft', 'pending_approval', 'sent', 'negotiating'].includes(o.status)).length,
    declined: offers.filter(o => o.status === 'declined').length,
  };
  const acceptRate = stats.total ? `${Math.round((stats.accepted / stats.total) * 100)}%` : '0%';

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-pink-500/20 flex items-center justify-center">
              <FileText className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-white" data-testid="offers-title">Offer Management</h1>
              <p className="text-xs text-slate-400">Create, track, and manage job offers with AI</p>
            </div>
          </div>
          <Button className="bg-violet-600 hover:bg-violet-500 text-sm h-9" onClick={() => setShowCreate(true)} data-testid="create-offer-btn">
            <Plus className="w-4 h-4 mr-1.5" /> New Offer
          </Button>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
          <StatBadge label="Total Offers" value={stats.total} icon={FileText} accent="text-violet-400" />
          <StatBadge label="Acceptance Rate" value={acceptRate} icon={ArrowUpRight} accent="text-emerald-400" />
          <StatBadge label="Pending" value={stats.pending} icon={Clock} accent="text-amber-400" />
          <StatBadge label="Declined" value={stats.declined} icon={ArrowDownRight} accent="text-red-400" />
        </div>

        {/* Status Filters */}
        <div className="flex gap-1.5 mb-5 flex-wrap">
          {['all', 'draft', 'pending_approval', 'approved', 'sent', 'negotiating', 'accepted', 'declined'].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-2.5 py-1 text-xs rounded-full border transition-all capitalize ${statusFilter === s
                ? (STATUS_CONFIG[s]?.color || 'bg-teal-500/20 text-teal-400 border-teal-500/30')
                : 'border-slate-700 text-slate-500 hover:border-slate-600'}`}
              data-testid={`filter-${s}`}>
              {s === 'all' ? `All (${offers.length})` : `${STATUS_CONFIG[s]?.label || s} (${offers.filter(o => o.status === s).length})`}
            </button>
          ))}
        </div>

        {/* Create Offer Dialog */}
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-lg">
            <DialogHeader><DialogTitle>New Job Offer</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Input value={form.candidate_name} onChange={e => setForm({ ...form, candidate_name: e.target.value })} placeholder="Candidate name *" className="bg-slate-700 border-slate-600 text-white" data-testid="offer-candidate-name" />
                <Input value={form.job_title} onChange={e => setForm({ ...form, job_title: e.target.value })} placeholder="Job title *" className="bg-slate-700 border-slate-600 text-white" data-testid="offer-job-title" />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <Input type="number" value={form.salary} onChange={e => setForm({ ...form, salary: e.target.value })} placeholder="Salary *" className="bg-slate-700 border-slate-600 text-white" data-testid="offer-salary" />
                <Select value={form.currency} onValueChange={v => setForm({ ...form, currency: v })}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="USD">USD</SelectItem><SelectItem value="EUR">EUR</SelectItem><SelectItem value="GBP">GBP</SelectItem><SelectItem value="INR">INR</SelectItem></SelectContent>
                </Select>
                <Input type="number" value={form.bonus} onChange={e => setForm({ ...form, bonus: e.target.value })} placeholder="Bonus" className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input type="date" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} className="bg-slate-700 border-slate-600 text-white" />
                <Input value={form.equity} onChange={e => setForm({ ...form, equity: e.target.value })} placeholder="Equity (e.g., 0.1%)" className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <Input value={form.hiring_manager} onChange={e => setForm({ ...form, hiring_manager: e.target.value })} placeholder="Hiring manager" className="bg-slate-700 border-slate-600 text-white" />
              <Input value={form.benefits} onChange={e => setForm({ ...form, benefits: e.target.value })} placeholder="Benefits (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
              <Textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Notes" className="bg-slate-700 border-slate-600 text-white min-h-[60px]" />
            </div>
            <DialogFooter>
              <Button variant="ghost" className="text-slate-400" onClick={() => setShowCreate(false)}>Cancel</Button>
              <Button className="bg-violet-600 hover:bg-violet-500" onClick={createOffer} disabled={!form.candidate_name || !form.job_title || !form.salary} data-testid="save-offer-btn">Create Offer</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Offers List */}
        <div className="space-y-2" data-testid="offers-list">
          {filtered.length === 0 ? (
            <div className="text-center py-16 text-slate-500">
              <FileText className="w-10 h-10 mx-auto mb-3 opacity-15" />
              <p className="text-sm">{statusFilter === 'all' ? 'No offers yet. Create your first one.' : 'No offers with this status.'}</p>
            </div>
          ) : filtered.map(o => {
            const cfg = STATUS_CONFIG[o.status] || STATUS_CONFIG.draft;
            const nextActions = STATUS_FLOW[o.status] || [];
            return (
              <Card key={o.id} className="bg-slate-800/50 border-slate-700/40 hover:border-slate-600/60 transition-all group">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-500/30 to-pink-500/30 flex items-center justify-center text-sm font-bold text-violet-300 shrink-0">
                        {o.candidate_name?.charAt(0)?.toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium text-white truncate">{o.candidate_name}</p>
                          <ChevronRight className="w-3 h-3 text-slate-600 shrink-0" />
                          <p className="text-sm text-slate-400 truncate">{o.job_title}</p>
                        </div>
                        <div className="flex items-center gap-3 mt-0.5 text-xs text-slate-500">
                          <span className="flex items-center gap-1"><DollarSign className="w-3 h-3" /> {o.currency} {o.salary?.toLocaleString()}</span>
                          {o.start_date && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {o.start_date}</span>}
                          {o.hiring_manager && <span className="flex items-center gap-1"><User className="w-3 h-3" /> {o.hiring_manager}</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0 ml-3">
                      <Badge className={`text-[10px] ${cfg.color}`}>{cfg.label}</Badge>
                      {nextActions.slice(0, 2).map(s => (
                        <Button key={s} size="sm" variant="ghost" className="h-6 text-[10px] text-slate-400 hover:text-white hidden md:flex"
                          onClick={(e) => { e.stopPropagation(); updateStatus(o.id, s); }} data-testid={`quick-${s}-${o.id}`}>
                          {STATUS_CONFIG[s]?.label || s}
                        </Button>
                      ))}
                      <Button size="sm" variant="ghost" className="h-7 text-xs text-teal-400" onClick={() => setSelectedOffer(o)} data-testid={`view-offer-${o.id}`}>
                        <Eye className="w-3 h-3 mr-1" /> View
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Offer Detail Dialog */}
        {selectedOffer && (
          <OfferDetail
            offer={selectedOffer}
            onClose={() => setSelectedOffer(null)}
            onUpdate={(updated) => { setSelectedOffer(updated); setOffers(offers.map(o => o.id === updated.id ? updated : o)); }}
          />
        )}
      </div>
    </div>
  );
}
