import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Users, Send, MessageSquare, Mail, Smartphone, Linkedin, Plus, Clock, Check, FileText, Loader2 } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function TeamOutreachPage() {
  const [tab, setTab] = useState('collaborate');
  const [comments, setComments] = useState([]);
  const [outreachHistory, setOutreachHistory] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [candidateId, setCandidateId] = useState('');
  const [outreachMsg, setOutreachMsg] = useState('');
  const [outreachSubject, setOutreachSubject] = useState('');
  const [outreachChannel, setOutreachChannel] = useState('email');
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    if (token) {
      fetch(`${API}/api/talent-tools/outreach/history`, { headers }).then(r => r.ok ? r.json() : { messages: [] }).then(d => setOutreachHistory(d.messages || [])).catch(() => {});
      fetch(`${API}/api/talent-tools/outreach/templates`, { headers }).then(r => r.ok ? r.json() : { templates: [] }).then(d => setTemplates(d.templates || [])).catch(() => {});
    }
  }, [token]);

  const loadComments = async (cid) => {
    if (!cid) return;
    const res = await fetch(`${API}/api/talent-tools/collaborate/comments/${cid}`, { headers });
    if (res.ok) { const d = await res.json(); setComments(d.comments || []); }
  };

  const addComment = async () => {
    if (!candidateId || !newComment.trim()) return;
    setLoading(true);
    const res = await fetch(`${API}/api/talent-tools/collaborate/comment`, {
      method: 'POST', headers,
      body: JSON.stringify({ candidate_id: candidateId, comment: newComment, mentions: [] })
    });
    if (res.ok) { setNewComment(''); loadComments(candidateId); }
    setLoading(false);
  };

  const sendOutreach = async () => {
    if (!outreachMsg.trim()) return;
    setLoading(true);
    const res = await fetch(`${API}/api/talent-tools/outreach/send`, {
      method: 'POST', headers,
      body: JSON.stringify({ candidate_ids: [candidateId || 'sample'], channel: outreachChannel, subject: outreachSubject, message: outreachMsg })
    });
    if (res.ok) {
      const d = await res.json();
      setOutreachHistory([d, ...outreachHistory]);
      setOutreachMsg(''); setOutreachSubject('');
    }
    setLoading(false);
  };

  const channelIcons = { email: Mail, sms: Smartphone, inmail: Linkedin };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-turquoise/10 rounded-lg"><Users className="w-6 h-6 text-turquoise" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="team-outreach-title">Team Collaboration & Outreach</h1>
            <p className="text-slate-400 text-sm">Collaborate on candidates and send multi-channel outreach</p>
          </div>
        </div>

        <Tabs value={tab} onValueChange={setTab}>
          <TabsList className="bg-slate-800 mb-6">
            <TabsTrigger value="collaborate" data-testid="tab-collaborate"><MessageSquare className="w-4 h-4 mr-1.5" /> Collaborate</TabsTrigger>
            <TabsTrigger value="outreach" data-testid="tab-outreach"><Send className="w-4 h-4 mr-1.5" /> Outreach</TabsTrigger>
            <TabsTrigger value="history" data-testid="tab-history"><Clock className="w-4 h-4 mr-1.5" /> History</TabsTrigger>
          </TabsList>

          <TabsContent value="collaborate">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader><CardTitle className="text-white text-base">Candidate Discussion</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <Input value={candidateId} onChange={e => { setCandidateId(e.target.value); loadComments(e.target.value); }}
                    placeholder="Enter candidate ID" className="bg-slate-700 border-slate-600 text-white" data-testid="collab-candidate-id" />
                  <ScrollArea className="h-64">
                    {comments.length === 0 ? (
                      <p className="text-slate-500 text-sm text-center py-8">No comments yet</p>
                    ) : comments.map(c => (
                      <div key={c.id} className="p-2 mb-2 bg-slate-700 rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-turquoise">{c.author_name}</span>
                          <span className="text-xs text-slate-500">{new Date(c.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-sm text-slate-300">{c.comment}</p>
                      </div>
                    ))}
                  </ScrollArea>
                  <div className="flex gap-2">
                    <Input value={newComment} onChange={e => setNewComment(e.target.value)} placeholder="Add comment..."
                      className="bg-slate-700 border-slate-600 text-white" data-testid="collab-comment-input"
                      onKeyDown={e => e.key === 'Enter' && addComment()} />
                    <Button onClick={addComment} disabled={loading} className="bg-turquoise hover:bg-turquoise/80" data-testid="add-comment-btn">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader><CardTitle className="text-white text-base">Templates</CardTitle></CardHeader>
                <CardContent>
                  {templates.length === 0 ? (
                    <p className="text-slate-500 text-sm text-center py-8">No templates created yet</p>
                  ) : templates.map(t => (
                    <div key={t.id} className="p-3 bg-slate-700 rounded-lg mb-2">
                      <p className="text-sm font-medium text-white">{t.name}</p>
                      <p className="text-xs text-slate-400 mt-1">{t.body.substring(0, 80)}...</p>
                      <Badge className="mt-1 text-xs bg-slate-600">{t.channel}</Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="outreach">
            <Card className="bg-slate-800 border-slate-700 max-w-2xl">
              <CardHeader><CardTitle className="text-white text-base flex items-center gap-2"><Send className="w-4 h-4 text-turquoise" /> Send Outreach</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <Select value={outreachChannel} onValueChange={setOutreachChannel}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="inmail">InMail</SelectItem>
                  </SelectContent>
                </Select>
                {outreachChannel === 'email' && <Input value={outreachSubject} onChange={e => setOutreachSubject(e.target.value)} placeholder="Subject line" className="bg-slate-700 border-slate-600 text-white" />}
                <Textarea value={outreachMsg} onChange={e => setOutreachMsg(e.target.value)} placeholder="Your message..." className="bg-slate-700 border-slate-600 text-white min-h-[120px]" data-testid="outreach-message" />
                <Button onClick={sendOutreach} disabled={loading || !outreachMsg.trim()} className="w-full bg-turquoise hover:bg-turquoise/80" data-testid="send-outreach-btn">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />} Send
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <div className="space-y-3" data-testid="outreach-history">
              {outreachHistory.length === 0 ? (
                <Card className="bg-slate-800 border-slate-700"><CardContent className="py-12 text-center text-slate-500"><Send className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No outreach sent yet</p></CardContent></Card>
              ) : outreachHistory.map(m => {
                const ChannelIcon = channelIcons[m.channel] || Mail;
                return (
                  <Card key={m.id} className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-slate-700 rounded-lg"><ChannelIcon className="w-4 h-4 text-turquoise" /></div>
                        <div>
                          <p className="text-sm text-white">{m.message?.substring(0, 60)}...</p>
                          <p className="text-xs text-slate-400 mt-0.5">Sent to {m.sent_count} candidate(s) via {m.channel}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <Badge className="bg-emerald-500/20 text-emerald-400">{m.status}</Badge>
                        <p className="text-xs text-slate-500 mt-1">{new Date(m.sent_at).toLocaleDateString()}</p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
