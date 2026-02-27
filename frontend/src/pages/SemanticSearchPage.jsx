import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Sparkles, Users, Briefcase, Loader2, Brain } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function SemanticSearchPage() {
  const [query, setQuery] = useState('');
  const [matchType, setMatchType] = useState('candidates');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/platform/semantic-match`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, match_type: matchType, top_k: 10 })
      });
      if (res.ok) setResults(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2 bg-purple-500/10 rounded-lg"><Brain className="w-6 h-6 text-purple-400" /></div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="semantic-search-title">Semantic Search</h1>
            <p className="text-slate-400 text-sm">AI-powered deep matching using natural language queries</p>
          </div>
        </div>

        <Card className="bg-slate-800 border-slate-700 mb-6">
          <CardContent className="p-4">
            <div className="flex gap-3">
              <div className="flex-1">
                <Input value={query} onChange={e => setQuery(e.target.value)} placeholder='Try: "bioprocess engineer with 5+ years experience in monoclonal antibodies"'
                  className="bg-slate-700 border-slate-600 text-white" data-testid="semantic-query"
                  onKeyDown={e => e.key === 'Enter' && handleSearch()} />
              </div>
              <Select value={matchType} onValueChange={setMatchType}>
                <SelectTrigger className="w-40 bg-slate-700 border-slate-600 text-white"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="candidates">Candidates</SelectItem>
                  <SelectItem value="jobs">Jobs</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleSearch} disabled={loading || !query.trim()} className="bg-turquoise hover:bg-turquoise/80" data-testid="semantic-search-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              </Button>
            </div>
          </CardContent>
        </Card>

        {results && (
          <>
            <div className="flex items-center gap-2 mb-4">
              <Badge className="bg-turquoise/20 text-turquoise">{results.match_count} matches</Badge>
              {results.criteria && results.criteria.skills && (
                <div className="flex gap-1">
                  {results.criteria.skills.slice(0, 5).map(s => <Badge key={s} className="bg-slate-700 text-slate-300 text-xs">{s}</Badge>)}
                </div>
              )}
            </div>

            <div className="space-y-3" data-testid="search-results">
              {results.matches.length === 0 ? (
                <Card className="bg-slate-800 border-slate-700"><CardContent className="py-12 text-center text-slate-500"><Search className="w-10 h-10 mx-auto mb-2 opacity-30" /><p>No matches found. Try a different query.</p></CardContent></Card>
              ) : results.matches.map((m, i) => (
                <Card key={i} className="bg-slate-800 border-slate-700 hover:border-turquoise/30 transition-colors">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-white font-medium">{m.name || m.title || 'Unknown'}</h3>
                        <p className="text-sm text-slate-400 mt-0.5">{m.email || m.company || ''}</p>
                        {m.skills && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {m.skills.slice(0, 5).map(s => <Badge key={s} className="text-xs bg-slate-700 text-slate-300">{s}</Badge>)}
                            {m.skills.length > 5 && <Badge className="text-xs bg-slate-700 text-slate-400">+{m.skills.length - 5}</Badge>}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        {matchType === 'candidates' ? <Users className="w-5 h-5 text-turquoise" /> : <Briefcase className="w-5 h-5 text-turquoise" />}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}

        {!results && (
          <div className="text-center py-16 text-slate-500">
            <Sparkles className="w-16 h-16 mx-auto mb-4 opacity-20" />
            <p className="text-lg">Enter a natural language query</p>
            <p className="text-sm mt-1">AI will extract skills, experience level, and domain to find the best matches</p>
          </div>
        )}
      </div>
    </div>
  );
}
