import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  Search, MapPin, Globe, Calendar, Filter,
  Sparkles, Loader2, ShieldCheck, Award, CheckCircle, 
  FileText, Code, HeartPulse, Settings, FileSearch
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { JobCard } from "@/components/shared/JobCard";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Icon mapping for presets
const PresetIcons = {
  "shield-check": ShieldCheck,
  "award": Award,
  "check-circle": CheckCircle,
  "file-text": FileText,
  "code": Code,
  "heart-pulse": HeartPulse,
  "settings": Settings,
  "search": FileSearch
};

const JobSearchPage = ({ savedJobs, onSave, onApply, onAnalyze }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("all");
  const [location, setLocation] = useState("any");
  const [days, setDays] = useState("0");
  const [presets, setPresets] = useState({ presets: [], locations: [], quality_terms: [] });
  const [deepSearching, setDeepSearching] = useState(false);
  const [searchStats, setSearchStats] = useState(null);

  useEffect(() => {
    // Fetch presets
    axios.get(`${API}/jobs/presets`).then(res => setPresets(res.data)).catch(() => {});
    searchJobs();
    // eslint-disable-next-line
  }, []);

  const searchJobs = async (searchQuery = query) => {
    setLoading(true);
    setSearchStats(null);
    try {
      const response = await axios.get(`${API}/jobs/search`, {
        params: { query: searchQuery, source, location: location === "any" ? "" : location, days: parseInt(days) }
      });
      setJobs(response.data);
    } catch (e) {
      toast.error("Failed to fetch jobs");
    }
    setLoading(false);
  };

  const deepSearch = async () => {
    setDeepSearching(true);
    setSearchStats(null);
    try {
      const response = await axios.post(`${API}/jobs/deep-search`, { use_ai: true });
      setJobs(response.data.jobs || []);
      setSearchStats({
        total: response.data.total_found,
        queries: response.data.queries_used,
        strategy: response.data.search_strategy
      });
      toast.success(`AI Deep Search found ${response.data.total_found} relevant jobs!`);
    } catch (e) {
      toast.error("Deep search failed");
    }
    setDeepSearching(false);
  };

  const handlePresetClick = (presetQuery) => {
    setQuery(presetQuery);
    searchJobs(presetQuery);
  };

  const savedJobIds = savedJobs.map(s => s.job.id);

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-6xl mx-auto animate-fade-in" data-testid="job-search-page">
      <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100 tracking-tight mb-6" style={{ fontFamily: 'IBM Plex Sans' }}>
        Find Remote Jobs
      </h1>

      {/* Quick Search Presets */}
      <div className="mb-6">
        <p className="text-sm text-slate-500 mb-3">Quick Search:</p>
        <div className="flex flex-wrap gap-2">
          {presets.presets?.map(preset => {
            const Icon = PresetIcons[preset.icon] || Search;
            return (
              <Button
                key={preset.id}
                variant="outline"
                size="sm"
                onClick={() => handlePresetClick(preset.query)}
                className="gap-2"
                data-testid={`preset-${preset.id}`}
              >
                <Icon className="w-4 h-4" />
                {preset.name}
              </Button>
            );
          })}
        </div>
      </div>

      {/* Search Bar & Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col gap-4">
            {/* Search input row */}
            <div className="flex flex-col md:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  placeholder="Search jobs by title, company, or skills..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && searchJobs()}
                  className="pl-10"
                  data-testid="job-search-input"
                />
              </div>
              <Button onClick={() => searchJobs()} disabled={loading} data-testid="search-btn">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Search"}
              </Button>
              <Button 
                variant="default" 
                onClick={deepSearch} 
                disabled={deepSearching}
                className="bg-gradient-to-r from-sky-500 to-emerald-500 hover:from-sky-600 hover:to-emerald-600"
                data-testid="deep-search-btn"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                {deepSearching ? "Deep Searching..." : "AI Deep Search"}
              </Button>
            </div>

            {/* Filters row */}
            <div className="flex flex-wrap gap-3">
              <Select value={source} onValueChange={setSource}>
                <SelectTrigger className="w-36" data-testid="source-select">
                  <Globe className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Source" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sources</SelectItem>
                  <SelectItem value="google">Google CSE</SelectItem>
                  <SelectItem value="remoteok">RemoteOK</SelectItem>
                  <SelectItem value="remotive">Remotive</SelectItem>
                  <SelectItem value="jobicy">Jobicy</SelectItem>
                  <SelectItem value="arbeitnow">Arbeitnow</SelectItem>
                  <SelectItem value="himalayas">Himalayas</SelectItem>
                </SelectContent>
              </Select>

              <Select value={location} onValueChange={setLocation}>
                <SelectTrigger className="w-36" data-testid="location-select">
                  <MapPin className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="any">Any Location</SelectItem>
                  {presets.locations?.map(loc => (
                    <SelectItem key={loc} value={loc.toLowerCase()}>{loc}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={days} onValueChange={setDays}>
                <SelectTrigger className="w-36" data-testid="date-select">
                  <Calendar className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Posted" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Any Time</SelectItem>
                  <SelectItem value="1">Last 24 hours</SelectItem>
                  <SelectItem value="3">Last 3 days</SelectItem>
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="14">Last 2 weeks</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Advanced Filters - TheirStack inspired */}
            <div className="pt-3 border-t border-slate-100">
              <p className="text-xs text-slate-400 mb-2 flex items-center gap-1">
                <Filter className="w-3 h-3" /> Advanced Filters (Industries & Technologies)
              </p>
              <div className="flex flex-wrap gap-2">
                {presets.industries?.slice(0, 5).map(industry => (
                  <Badge 
                    key={industry} 
                    variant="outline" 
                    className="cursor-pointer hover:bg-slate-100 text-xs"
                    onClick={() => { setQuery(industry); searchJobs(industry); }}
                  >
                    {industry}
                  </Badge>
                ))}
                {presets.technologies?.slice(0, 4).map(tech => (
                  <Badge 
                    key={tech} 
                    variant="secondary" 
                    className="cursor-pointer hover:bg-slate-200 text-xs"
                    onClick={() => { setQuery(tech); searchJobs(tech); }}
                  >
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        {/* Search Stats from Deep Search */}
        {searchStats && (
          <Card className="bg-gradient-to-r from-sky-50 to-emerald-50 border-sky-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-sky-500" />
                <span className="font-medium text-slate-900 dark:text-slate-100">AI Deep Search Results</span>
                {searchStats.jobspy_enabled && (
                  <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200">
                    JobSpy
                  </Badge>
                )}
                {searchStats.google_cse_enabled && (
                  <Badge variant="outline" className="text-xs bg-sky-50 text-sky-700 border-sky-200">
                    Google CSE
                  </Badge>
                )}
              </div>
              <p className="text-sm text-slate-600 mb-2">
                Found <strong>{searchStats.total}</strong> relevant jobs across <strong>{searchStats.sources_searched?.length || 9}</strong> sources
              </p>
              <div className="flex flex-wrap gap-1 mb-2">
                {searchStats.sources_searched?.map((source, i) => (
                  <Badge key={i} variant="outline" className="text-xs">{source}</Badge>
                ))}
              </div>
              <p className="text-xs text-slate-400">Searched: {searchStats.queries?.slice(0, 4).join(', ')}</p>
            </CardContent>
          </Card>
        )}
        
        {loading || deepSearching ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-4 bg-slate-50 rounded-lg">
              <Loader2 className="w-5 h-5 animate-spin text-sky-500" />
              <span className="text-slate-600">
                {deepSearching ? "AI is searching LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter, and 5 more job boards..." : "Searching..."}
              </span>
            </div>
            {[1, 2, 3].map(i => (
              <Card key={i}>
                <CardContent className="p-6">
                  <div className="skeleton h-6 w-48 rounded mb-3" />
                  <div className="skeleton h-4 w-32 rounded mb-4" />
                  <div className="skeleton h-4 w-full rounded" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="empty-state">
            <Search className="w-12 h-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">No jobs found</h3>
            <p className="text-slate-500 mb-4">Try AI Deep Search to find Quality & Medical Device jobs</p>
            <Button onClick={deepSearch} className="bg-gradient-to-r from-sky-500 to-emerald-500">
              <Sparkles className="w-4 h-4 mr-2" /> Run AI Deep Search
            </Button>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-500 mb-4">{jobs.length} jobs found</p>
            {jobs.map(job => (
              <JobCard
                key={job.id}
                job={job}
                onSave={onSave}
                onApply={onApply}
                onAnalyze={onAnalyze}
                isSaved={savedJobIds.includes(job.id)}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default JobSearchPage;
