import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileText, DollarSign, Calendar, User, Send, Plus, Loader2, Sparkles, Check, Clock, X } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function OfferManagementPage() {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ candidate_id: '', candidate_name: '', job_id: '', job_title: '', salary: '', currency: 'USD', start_date: '', benefits: '', notes: '' });
  const [generatingLetter, setGeneratingLetter] = useState(null);
  const [letterContent, setLetterContent] = useState('');
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    if (token) fetch(`${API}/api/advanced/offers`, { headers }).then(r => r.ok ? r.json() : { offers: [] }).then(d => { setOffers(d.offers || []); setLoading(false); }).catch(() => setLoading(false));
    else setLoading(false);
  }, [token]);

  const createOffer = async () => {
    if (!form.candidate_name || !form.job_title || !form.salary) return;
    setLoading(true);
    const res = await fetch(`${API}/api/advanced/offers`, {
      method: 'POST', headers,
      body: JSON.stringify({ ...form, salary: parseFloat(form.salary), benefits: form.benefits.split(',').map(b => b.trim()).filter(Boolean) })
    });
    if (res.ok) { const o = await res.json(); setOffers([o, ...offers]); setShowCreate(false); setForm({ candidate_id: '', candidate_name: '', job_id: '', job_title: '', salary: '', currency: 'USD', start_date: '', benefits: '', notes: '' }); }
    setLoading(false);
  };

  const generateLetter = async (offerId) => {
    setGeneratingLetter(offerId);
    const res = await fetch(`${API}/api/advanced/offers/${offerId}/generate-letter`, { method: 'POST', headers });
    if (res.ok) { const d = await res.json(); setLetterContent(d.letter); }
    setGeneratingLetter(null);
  };

  const updateStatus = async (offerId, status) => {
    await fetch(`${API}/api/advanced/offers/${offerId}/status`, { method: 'PUT', headers, body: JSON.stringify({ status }) });
    setOffers(offers.map(o => o.id === offerId ? { ...o, status } : o));
  };

  const statusColors = { draft: 'bg-slate-600', sent: 'bg-blue-500/20 text-blue-400', accepted: 'bg-emerald-500/20 text-emerald-400', declined: 'bg-red-500/20 text-red-400', withdrawn: 'bg-yellow-500/20 text-yellow-400' };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-turquoise/10 rounded-lg"><FileText className="w-6 h-6 text-turquoise" /></div>
            <div>
              <h1 className="text-2xl font-bold text-white" data-testid="offers-title">Offer Management</h1>
              <p className="text-slate-400 text-sm">Create, track, and generate AI offer letters</p>
            </div>
          </div>
          <Button className="bg-turquoise hover:bg-turquoise/80" onClick={() => setShowCreate(true)} data-testid="create-offer-btn"><Plus className="w-4 h-4 mr-2" /> New Offer</Button>
        </div>

        {showCreate && (
          <Card className="bg-slate-800 border-slate-700 mb-6">
            <CardContent className="p-4 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Input value={form.candidate_name} onChange={e => setForm({ ...form, candidate_name: e.target.value })} placeholder="Candidate name *" className="bg-slate-700 border-slate-600 text-white" data-testid="offer-candidate-name" />
                <Input value={form.job_title} onChange={e => setForm({ ...form, job_title: e.target.value })} placeholder="Job title *" className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <Input type="number" value={form.salary} onChange={e => setForm({ ...form, salary: e.target.value })} placeholder="Salary *" className="bg-slate-700 border-slate-600 text-white" data-testid="offer-salary" />
                <Select value={form.currency} onValueChange={v => setForm({ ...form, currency: v })}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="USD">USD</SelectItem><SelectItem value="EUR">EUR</SelectItem><SelectItem value="GBP">GBP</SelectItem></SelectContent>
                </Select>
                <Input type="date" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <Input value={form.benefits} onChange={e => setForm({ ...form, benefits: e.target.value })} placeholder="Benefits (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
              <div className="flex gap-2">
                <Button onClick={createOffer} className="bg-turquoise hover:bg-turquoise/80" data-testid="save-offer-btn">Create Offer</Button>
                <Button variant="ghost" className="text-slate-400" onClick={() => setShowCreate(false)}>Cancel</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="space-y-3" data-testid="offers-list">
          {offers.length === 0 && !loading ? (
            <Card className="bg-slate-800 border-slate-700"><CardContent className="py-12 text-center text-slate-500"><FileText className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No offers yet</p></CardContent></Card>
          ) : offers.map(o => (
            <Card key={o.id} className="bg-slate-800 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="text-white font-medium">{o.candidate_name} - {o.job_title}</h3>
                    <p className="text-sm text-slate-400 mt-0.5 flex items-center gap-3">
                      <span className="flex items-center gap-1"><DollarSign className="w-3 h-3" /> {o.currency} {o.salary?.toLocaleString()}</span>
                      {o.start_date && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {o.start_date}</span>}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={statusColors[o.status] || 'bg-slate-600'}>{o.status}</Badge>
                    {o.status === 'draft' && <Button size="sm" variant="ghost" className="h-7 text-xs text-blue-400" onClick={() => updateStatus(o.id, 'sent')}><Send className="w-3 h-3 mr-1" /> Send</Button>}
                    <Button size="sm" variant="ghost" className="h-7 text-xs text-turquoise" onClick={() => generateLetter(o.id)} disabled={generatingLetter === o.id} data-testid={`gen-letter-${o.id}`}>
                      {generatingLetter === o.id ? <Loader2 className="w-3 h-3 animate-spin mr-1" /> : <Sparkles className="w-3 h-3 mr-1" />} AI Letter
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {letterContent && (
          <Card className="bg-slate-800 border-slate-700 mt-6">
            <CardHeader><div className="flex items-center justify-between"><CardTitle className="text-white text-base">Generated Offer Letter</CardTitle>
              <Button size="sm" variant="ghost" className="text-slate-400" onClick={() => setLetterContent('')}><X className="w-4 h-4" /></Button>
            </div></CardHeader>
            <CardContent><pre className="whitespace-pre-wrap text-sm text-slate-300 font-sans leading-relaxed" data-testid="offer-letter">{letterContent}</pre></CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
