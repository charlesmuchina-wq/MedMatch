import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Video, Users, Calendar, Plus, Loader2, Globe, ExternalLink } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function WebinarPage() {
  const [webinars, setWebinars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [maxAttendees, setMaxAttendees] = useState(500);
  const [scheduled, setScheduled] = useState('');
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    fetch(`${API}/api/advanced/webinars`).then(r => r.json()).then(d => { setWebinars(d.webinars || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const createWebinar = async () => {
    if (!title) return;
    setLoading(true);
    const res = await fetch(`${API}/api/advanced/webinars`, {
      method: 'POST', headers,
      body: JSON.stringify({ title, description: desc, max_attendees: maxAttendees, scheduled_at: scheduled })
    });
    if (res.ok) {
      const w = await res.json();
      setWebinars([w, ...webinars]);
      setTitle(''); setDesc(''); setShowCreate(false);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-turquoise/10 rounded-lg"><Video className="w-6 h-6 text-turquoise" /></div>
            <div>
              <h1 className="text-2xl font-bold text-white" data-testid="webinar-title">Webinars</h1>
              <p className="text-slate-400 text-sm">Host large-scale webinar events with up to 1000 attendees</p>
            </div>
          </div>
          <Button className="bg-turquoise hover:bg-turquoise/80" onClick={() => setShowCreate(true)} data-testid="create-webinar-btn">
            <Plus className="w-4 h-4 mr-2" /> New Webinar
          </Button>
        </div>

        {showCreate && (
          <Card className="bg-slate-800 border-slate-700 mb-6">
            <CardContent className="p-4 space-y-3">
              <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="Webinar title *" className="bg-slate-700 border-slate-600 text-white" data-testid="webinar-title-input" />
              <Textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Description" className="bg-slate-700 border-slate-600 text-white" />
              <div className="grid grid-cols-2 gap-3">
                <Input type="number" value={maxAttendees} onChange={e => setMaxAttendees(Number(e.target.value))} placeholder="Max attendees" className="bg-slate-700 border-slate-600 text-white" />
                <Input type="datetime-local" value={scheduled} onChange={e => setScheduled(e.target.value)} className="bg-slate-700 border-slate-600 text-white" />
              </div>
              <div className="flex gap-2">
                <Button onClick={createWebinar} className="bg-turquoise hover:bg-turquoise/80" data-testid="save-webinar-btn">Create</Button>
                <Button variant="ghost" className="text-slate-400" onClick={() => setShowCreate(false)}>Cancel</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="webinar-grid">
          {webinars.length === 0 && !loading ? (
            <div className="col-span-full text-center py-12 text-slate-500">
              <Video className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>No webinars scheduled</p>
            </div>
          ) : webinars.map(w => (
            <Card key={w.id} className="bg-slate-800 border-slate-700 hover:border-turquoise/30 transition-colors">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-white text-base">{w.title}</CardTitle>
                  <Badge className={w.status === 'live' ? 'bg-red-500/20 text-red-400' : 'bg-turquoise/20 text-turquoise'}>{w.status}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                {w.description && <p className="text-sm text-slate-400 mb-3 line-clamp-2">{w.description}</p>}
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {w.attendee_count}/{w.max_attendees}</span>
                  {w.scheduled_at && <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {new Date(w.scheduled_at).toLocaleDateString()}</span>}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
