import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Users, Plus, FolderOpen, Send, MessageSquare, StickyNote, Loader2, Tag, Trash2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function TalentCRMPage() {
  const [pools, setPools] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [poolName, setPoolName] = useState('');
  const [poolDesc, setPoolDesc] = useState('');
  const [poolTags, setPoolTags] = useState('');
  const [activeTab, setActiveTab] = useState('pools');

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/talent-crm/pools`).then(r => r.json()),
      fetch(`${API}/api/talent-crm/campaigns`).then(r => r.json())
    ]).then(([p, c]) => {
      setPools(p.pools || []);
      setCampaigns(c.campaigns || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const createPool = async () => {
    if (!poolName.trim()) return;
    try {
      const res = await fetch(`${API}/api/talent-crm/pools`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: poolName, description: poolDesc, tags: poolTags.split(',').map(t => t.trim()).filter(Boolean) })
      });
      if (res.ok) {
        const pool = await res.json();
        setPools([pool, ...pools]);
        setPoolName(''); setPoolDesc(''); setPoolTags(''); setShowCreate(false);
      }
    } catch (e) { console.error(e); }
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center"><Loader2 className="w-8 h-8 text-turquoise animate-spin" /></div>;

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-turquoise/10 rounded-lg"><Users className="w-6 h-6 text-turquoise" /></div>
            <div>
              <h1 className="text-2xl font-bold text-white" data-testid="crm-page-title">Talent CRM</h1>
              <p className="text-slate-400 text-sm">Manage talent pools, notes, and nurture campaigns</p>
            </div>
          </div>
          <Button className="bg-turquoise hover:bg-turquoise/80" onClick={() => setShowCreate(true)} data-testid="create-pool-btn">
            <Plus className="w-4 h-4 mr-2" /> New Pool
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {['pools', 'campaigns'].map(tab => (
            <Button key={tab} variant={activeTab === tab ? 'default' : 'ghost'}
              className={activeTab === tab ? 'bg-turquoise' : 'text-slate-400'}
              onClick={() => setActiveTab(tab)} data-testid={`tab-${tab}`}>
              {tab === 'pools' ? <FolderOpen className="w-4 h-4 mr-1.5" /> : <Send className="w-4 h-4 mr-1.5" />}
              {tab === 'pools' ? 'Talent Pools' : 'Campaigns'}
            </Button>
          ))}
        </div>

        {/* Create Pool Modal */}
        {showCreate && (
          <Card className="bg-slate-800 border-slate-700 mb-6">
            <CardContent className="p-4 space-y-3">
              <Input value={poolName} onChange={e => setPoolName(e.target.value)} placeholder="Pool name *" className="bg-slate-700 border-slate-600 text-white" data-testid="pool-name-input" />
              <Textarea value={poolDesc} onChange={e => setPoolDesc(e.target.value)} placeholder="Description" className="bg-slate-700 border-slate-600 text-white" />
              <Input value={poolTags} onChange={e => setPoolTags(e.target.value)} placeholder="Tags (comma-separated)" className="bg-slate-700 border-slate-600 text-white" />
              <div className="flex gap-2">
                <Button className="bg-turquoise hover:bg-turquoise/80" onClick={createPool} data-testid="save-pool-btn">Create Pool</Button>
                <Button variant="ghost" className="text-slate-400" onClick={() => setShowCreate(false)}>Cancel</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'pools' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="pools-grid">
            {pools.length === 0 ? (
              <div className="col-span-full text-center py-12 text-slate-500">
                <FolderOpen className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>No talent pools yet. Create one to start organizing candidates.</p>
              </div>
            ) : pools.map(pool => (
              <Card key={pool.pool_id} className="bg-slate-800 border-slate-700 hover:border-turquoise/30 transition-colors">
                <CardHeader className="pb-2">
                  <CardTitle className="text-white text-base">{pool.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  {pool.description && <p className="text-sm text-slate-400 mb-3">{pool.description}</p>}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1 text-sm text-slate-400">
                      <Users className="w-3.5 h-3.5" /> {pool.candidate_count || 0} candidates
                    </div>
                    <div className="flex gap-1">
                      {(pool.tags || []).slice(0, 2).map(t => (
                        <Badge key={t} className="bg-slate-700 text-slate-300 text-xs">{t}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div className="space-y-4" data-testid="campaigns-list">
            {campaigns.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Send className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>No nurture campaigns yet.</p>
              </div>
            ) : campaigns.map(c => (
              <Card key={c.campaign_id} className="bg-slate-800 border-slate-700">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-medium">{c.name}</h3>
                      <p className="text-xs text-slate-400 mt-1">
                        Sent: {c.sent_count} | Opened: {c.open_count} | Replied: {c.reply_count}
                      </p>
                    </div>
                    <Badge className={c.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-600 text-slate-300'}>
                      {c.status}
                    </Badge>
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
