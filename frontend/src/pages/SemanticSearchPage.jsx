import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Sparkles, Users, Briefcase, Loader2, Brain, Clock, X, ArrowRight, MapPin, Star } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;
const HISTORY_KEY = 'semantic_search_history';
const MAX_HISTORY = 8;

const EXAMPLE_QUERIES = [
  'Bioprocess engineer with 5+ years in monoclonal antibodies',
  'Senior data scientist experienced in drug discovery ML',
  'Quality assurance lead with FDA 21 CFR Part 11 knowledge',
  'Clinical trial manager with Phase III oncology experience',
  'Regulatory affairs specialist for EU MDR compliance',
  'Bioinformatics researcher with NGS pipeline experience'
];

export default function SemanticSearchPage() {
  const [query, setQuery] = useState('');
  const [matchType, setMatchType] = useState('candidates');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
      setSearchHistory(saved);
    } catch { setSearchHistory([]); }
  }, []);

  const saveToHistory = (q, type, count) => {
    const entry = { query: q, type, count, timestamp: Date.now() };
    const updated = [entry, ...searchHistory.filter(h => h.query !== q)].slice(0, MAX_HISTORY);
    setSearchHistory(updated);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  };

  const clearHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem(HISTORY_KEY);
  };

  const handleSearch = async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) return;
    setQuery(q);
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/platform/semantic-match`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, match_type: matchType, top_k: 10 })
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data);
        saveToHistory(q, matchType, data.match_count);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const formatTime = (ts) => {
    const diff = Date.now() - ts;
    if (diff < 60000) return 'just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20">
            <Brain className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="semantic-search-title">Semantic Search</h1>
            <p className="text-slate-400 text-sm">AI-powered deep matching using natural language queries</p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4 mb-6 backdrop-blur">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <Input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder='Try: "bioprocess engineer with 5+ years in monoclonal antibodies"'
                className="bg-slate-700/50 border-slate-600 text-white pl-10 h-11"
                data-testid="semantic-query"
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Select value={matchType} onValueChange={setMatchType}>
              <SelectTrigger className="w-36 bg-slate-700/50 border-slate-600 text-white h-11" data-testid="match-type-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="candidates"><Users className="w-3.5 h-3.5 inline mr-1.5" />Candidates</SelectItem>
                <SelectItem value="jobs"><Briefcase className="w-3.5 h-3.5 inline mr-1.5" />Jobs</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={() => handleSearch()} disabled={loading || !query.trim()} className="bg-turquoise hover:bg-turquoise/80 h-11 px-5" data-testid="semantic-search-btn">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Search className="w-4 h-4 mr-1.5" />Search</>}
            </Button>
          </div>
        </div>

        {/* Results */}
        {results && (
          <>
            {/* AI Criteria Badges */}
            <div className="flex items-center gap-2 mb-4 flex-wrap">
              <Badge className="bg-turquoise/20 text-turquoise border-turquoise/30" data-testid="match-count-badge">
                <Sparkles className="w-3 h-3 mr-1" />{results.match_count} matches
              </Badge>
              {results.criteria?.skills?.slice(0, 5).map(s => (
                <Badge key={s} className="bg-slate-700/50 text-slate-300 border-slate-600 text-xs">{s}</Badge>
              ))}
              {results.criteria?.experience_level && (
                <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-xs">
                  <Star className="w-3 h-3 mr-0.5" />{results.criteria.experience_level}
                </Badge>
              )}
              {results.criteria?.domain && (
                <Badge className="bg-purple-500/10 text-purple-400 border-purple-500/20 text-xs">
                  {results.criteria.domain}
                </Badge>
              )}
            </div>

            {/* Result Cards */}
            <div className="space-y-3" data-testid="search-results">
              {results.matches.length === 0 ? (
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl py-16 text-center">
                  <Search className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                  <p className="text-slate-400 text-lg">No matches found</p>
                  <p className="text-slate-500 text-sm mt-1">Try broadening your search criteria</p>
                </div>
              ) : results.matches.map((m, i) => (
                <Card key={i} className="bg-slate-800/50 border-slate-700/50 hover:border-turquoise/30 transition-all duration-200 hover:shadow-lg hover:shadow-turquoise/5" data-testid={`result-card-${i}`}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-white font-medium truncate">{m.name || m.title || 'Unknown'}</h3>
                          <Badge className="bg-slate-700 text-slate-400 text-[10px] shrink-0">#{i + 1}</Badge>
                        </div>
                        <p className="text-sm text-slate-400">{m.email || m.company || m.location || ''}</p>
                        {m.location && <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5"><MapPin className="w-3 h-3" />{m.location}</p>}
                        {m.skills && m.skills.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {m.skills.slice(0, 6).map(s => {
                              const isMatched = results.criteria?.skills?.some(cs => cs.toLowerCase() === s.toLowerCase());
                              return (
                                <Badge key={s} className={`text-xs ${isMatched ? 'bg-turquoise/15 text-turquoise border-turquoise/20' : 'bg-slate-700/50 text-slate-400 border-slate-600'}`}>{s}</Badge>
                              );
                            })}
                            {m.skills.length > 6 && <Badge className="text-xs bg-slate-700/50 text-slate-500">+{m.skills.length - 6}</Badge>}
                          </div>
                        )}
                      </div>
                      <div className="flex flex-col items-center gap-1 shrink-0">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${matchType === 'candidates' ? 'bg-turquoise/10' : 'bg-blue-500/10'}`}>
                          {matchType === 'candidates' ? <Users className="w-5 h-5 text-turquoise" /> : <Briefcase className="w-5 h-5 text-blue-400" />}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}

        {/* Empty State: Search History + Example Queries */}
        {!results && (
          <div className="space-y-8">
            {/* Search History */}
            {searchHistory.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-slate-400 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />Recent Searches
                  </h3>
                  <button onClick={clearHistory} className="text-xs text-slate-500 hover:text-slate-300 transition-colors" data-testid="clear-history-btn">
                    Clear
                  </button>
                </div>
                <div className="flex flex-wrap gap-2" data-testid="search-history">
                  {searchHistory.map((h, i) => (
                    <button key={i} onClick={() => { setMatchType(h.type); handleSearch(h.query); }}
                      className="flex items-center gap-2 bg-slate-800/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-300 hover:border-turquoise/30 hover:text-white transition-all" data-testid={`history-item-${i}`}>
                      <Clock className="w-3 h-3 text-slate-500" />
                      <span className="truncate max-w-[200px]">{h.query}</span>
                      <Badge className="bg-slate-700/50 text-slate-500 text-[10px]">{h.count} hits</Badge>
                      <span className="text-[10px] text-slate-600">{formatTime(h.timestamp)}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Example Queries */}
            <div className="text-center pt-8">
              <Sparkles className="w-14 h-14 mx-auto mb-4 text-slate-700" />
              <p className="text-lg text-slate-400 mb-1">AI-Powered Talent & Job Search</p>
              <p className="text-sm text-slate-500 mb-8">Describe what you're looking for in natural language</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-3xl mx-auto" data-testid="example-queries">
                {EXAMPLE_QUERIES.map((eq, i) => (
                  <button key={i} onClick={() => handleSearch(eq)}
                    className="group flex items-center gap-2 text-left bg-slate-800/30 border border-slate-700/30 rounded-xl px-4 py-3 text-sm text-slate-400 hover:border-purple-500/30 hover:text-slate-200 hover:bg-slate-800/50 transition-all" data-testid={`example-query-${i}`}>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-purple-400 transition-colors shrink-0" />
                    <span className="truncate">{eq}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
