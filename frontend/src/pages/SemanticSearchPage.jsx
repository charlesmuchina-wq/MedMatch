import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Sparkles, Users, Briefcase, Loader2, Brain, Clock, ArrowRight, MapPin, Star, Filter, SlidersHorizontal } from 'lucide-react';
import { useTranslation } from '@/utils/i18n';

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
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [matchType, setMatchType] = useState('candidates');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);
  const [minRelevance, setMinRelevance] = useState(0);
  const [showFilters, setShowFilters] = useState(false);

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
    if (diff < 60000) return t('common.justNow') || 'just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
    return `${Math.floor(diff / 86400000)}d`;
  };

  const getRelevanceColor = (score) => {
    if (score >= 80) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    if (score >= 60) return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
    if (score >= 40) return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  };

  const getRelevanceLabel = (score) => {
    if (score >= 80) return t('candidateSearch.excellent') || 'Excellent';
    if (score >= 60) return t('candidateSearch.good') || 'Good';
    if (score >= 40) return t('candidateSearch.fair') || 'Fair';
    return t('candidateSearch.low') || 'Low';
  };

  // Filter results by minimum relevance
  const filteredMatches = results?.matches?.filter(m => {
    const score = m.relevance_score || m.score || 0;
    return score >= minRelevance;
  }) || [];

  return (
    <div className="min-h-screen bg-karau-bg p-4 md:p-8" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-2.5 bg-purple-500/10 rounded-xl border border-purple-500/20">
            <Brain className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white" data-testid="semantic-search-title">
              {t('candidateSearch.semanticSearch') || 'Semantic Search'}
            </h1>
            <p className="text-karau-muted text-sm">
              {t('candidateSearch.semanticSearchDesc') || 'AI-powered deep matching using natural language queries'}
            </p>
          </div>
        </div>

        <div className="bg-karau-card/50 border border-white/5 rounded-2xl p-4 mb-6 backdrop-blur">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <Input
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder={t('candidateSearch.searchPlaceholder') || 'Try: "bioprocess engineer with 5+ years"'}
                className="bg-karau-bg/60 border-white/10 text-white pl-10 h-11 rounded-xl focus:border-purple-500/40"
                data-testid="semantic-query"
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Select value={matchType} onValueChange={setMatchType}>
              <SelectTrigger className="w-36 bg-karau-bg/60 border-white/10 text-white h-11 rounded-xl" data-testid="match-type-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="candidates"><Users className="w-3.5 h-3.5 inline mr-1.5" />{t('candidateSearch.candidates') || 'Candidates'}</SelectItem>
                <SelectItem value="jobs"><Briefcase className="w-3.5 h-3.5 inline mr-1.5" />{t('candidateSearch.jobs') || 'Jobs'}</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={() => handleSearch()} disabled={loading || !query.trim()}
              className="bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 h-11 px-5 rounded-xl shadow-lg shadow-purple-500/20"
              data-testid="semantic-search-btn">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Search className="w-4 h-4 mr-1.5" />{t('candidateSearch.search') || 'Search'}</>}
            </Button>
          </div>
        </div>

        {results && (
          <>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30" data-testid="match-count-badge">
                  <Sparkles className="w-3 h-3 mr-1" />{results.match_count} {t('candidateSearch.matches') || 'matches'}
                </Badge>
                {results.criteria?.skills?.slice(0, 5).map(s => (
                  <Badge key={s} className="bg-karau-surface text-slate-300 border-white/10 text-xs">{s}</Badge>
                ))}
                {results.criteria?.experience_level && (
                  <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-xs">
                    <Star className="w-3 h-3 mr-0.5" />{results.criteria.experience_level}
                  </Badge>
                )}
                {results.criteria?.domain && (
                  <Badge className="bg-violet-500/10 text-violet-400 border-violet-500/20 text-xs">{results.criteria.domain}</Badge>
                )}
              </div>
              <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)}
                className={`border-white/10 text-slate-400 rounded-xl ${showFilters ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' : ''}`}
                data-testid="toggle-filters-btn">
                <SlidersHorizontal className="w-3.5 h-3.5 mr-1.5" />
                {t('candidateSearch.filters') || 'Filters'}
              </Button>
            </div>

            {showFilters && (
              <div className="mb-4 p-3 bg-karau-card/40 border border-white/5 rounded-xl" data-testid="filter-panel">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Filter className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-xs text-slate-400">{t('candidateSearch.minRelevance') || 'Min Relevance'}:</span>
                  </div>
                  <div className="flex gap-2">
                    {[0, 40, 60, 80].map(val => (
                      <button key={val} onClick={() => setMinRelevance(val)}
                        className={`px-3 py-1 rounded-lg text-xs transition-all ${
                          minRelevance === val
                            ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                            : 'bg-karau-bg/50 text-slate-500 border border-white/5 hover:border-white/10'
                        }`} data-testid={`filter-relevance-${val}`}>
                        {val === 0 ? (t('candidateSearch.all') || 'All') : `${val}%+`}
                      </button>
                    ))}
                  </div>
                  {minRelevance > 0 && (
                    <span className="text-xs text-slate-500">
                      {filteredMatches.length}/{results.matches.length} {t('candidateSearch.shown') || 'shown'}
                    </span>
                  )}
                </div>
              </div>
            )}

            <div className="space-y-3" data-testid="search-results">
              {filteredMatches.length === 0 ? (
                <div className="bg-karau-card/50 border border-white/5 rounded-2xl py-16 text-center">
                  <Search className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                  <p className="text-slate-400 text-lg">{t('candidateSearch.noMatches') || 'No matches found'}</p>
                  <p className="text-slate-500 text-sm mt-1">{t('candidateSearch.tryBroader') || 'Try broadening your search criteria'}</p>
                </div>
              ) : filteredMatches.map((m, i) => {
                const relevanceScore = m.relevance_score || m.score || Math.max(0, 95 - i * 8);
                return (
                  <Card key={i} className="bg-karau-card/50 border-white/5 hover:border-purple-500/30 transition-all duration-200 hover:shadow-lg hover:shadow-purple-500/5 rounded-xl" data-testid={`result-card-${i}`}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-white font-medium truncate">{m.name || m.title || 'Unknown'}</h3>
                            <Badge className="bg-karau-surface text-slate-400 text-[10px] shrink-0">#{i + 1}</Badge>
                          </div>
                          <p className="text-sm text-karau-muted">{m.email || m.company || m.location || ''}</p>
                          {m.location && (
                            <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                              <MapPin className="w-3 h-3" />{m.location}
                            </p>
                          )}
                          {m.skills && m.skills.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {m.skills.slice(0, 6).map(s => {
                                const isMatched = results.criteria?.skills?.some(cs => cs.toLowerCase() === s.toLowerCase());
                                return (
                                  <Badge key={s} className={`text-xs ${isMatched ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20' : 'bg-karau-surface text-slate-400 border-white/10'}`}>{s}</Badge>
                                );
                              })}
                              {m.skills.length > 6 && <Badge className="text-xs bg-karau-surface text-slate-500">+{m.skills.length - 6}</Badge>}
                            </div>
                          )}
                        </div>
                        <div className="flex flex-col items-center gap-2 shrink-0">
                          <div className={`px-2.5 py-1 rounded-lg border text-xs font-semibold ${getRelevanceColor(relevanceScore)}`} data-testid={`relevance-score-${i}`}>
                            {Math.round(relevanceScore)}%
                          </div>
                          <span className="text-[10px] text-slate-500">{getRelevanceLabel(relevanceScore)}</span>
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${matchType === 'candidates' ? 'bg-purple-500/10' : 'bg-blue-500/10'}`}>
                            {matchType === 'candidates' ? <Users className="w-5 h-5 text-purple-400" /> : <Briefcase className="w-5 h-5 text-blue-400" />}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </>
        )}

        {!results && (
          <div className="space-y-8">
            {searchHistory.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-medium text-karau-muted flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />{t('candidateSearch.recentSearches') || 'Recent Searches'}
                  </h3>
                  <button onClick={clearHistory} className="text-xs text-slate-500 hover:text-slate-300 transition-colors" data-testid="clear-history-btn">
                    {t('common.clear') || 'Clear'}
                  </button>
                </div>
                <div className="flex flex-wrap gap-2" data-testid="search-history">
                  {searchHistory.map((h, i) => (
                    <button key={i} onClick={() => { setMatchType(h.type); handleSearch(h.query); }}
                      className="flex items-center gap-2 bg-karau-card/50 border border-white/5 rounded-xl px-3 py-2 text-sm text-slate-300 hover:border-purple-500/30 hover:text-white transition-all" data-testid={`history-item-${i}`}>
                      <Clock className="w-3 h-3 text-slate-500" />
                      <span className="truncate max-w-[200px]">{h.query}</span>
                      <Badge className="bg-karau-surface text-slate-500 text-[10px]">{h.count} hits</Badge>
                      <span className="text-[10px] text-slate-600">{formatTime(h.timestamp)}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="text-center pt-8">
              <Sparkles className="w-14 h-14 mx-auto mb-4 text-slate-700" />
              <p className="text-lg text-karau-muted mb-1">{t('candidateSearch.aiSearchTitle') || 'AI-Powered Talent & Job Search'}</p>
              <p className="text-sm text-slate-500 mb-8">{t('candidateSearch.aiSearchDesc') || 'Describe what you\'re looking for in natural language'}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-3xl mx-auto" data-testid="example-queries">
                {EXAMPLE_QUERIES.map((eq, i) => (
                  <button key={i} onClick={() => handleSearch(eq)}
                    className="group flex items-center gap-2 text-left bg-karau-card/30 border border-white/5 rounded-xl px-4 py-3 text-sm text-slate-400 hover:border-purple-500/30 hover:text-slate-200 hover:bg-karau-card/50 transition-all" data-testid={`example-query-${i}`}>
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
