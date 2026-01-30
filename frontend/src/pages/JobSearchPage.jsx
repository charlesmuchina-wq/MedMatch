import { useState, useEffect } from "react";
import { toast } from "sonner";
import { 
  Search, MapPin, Globe, Calendar, Filter,
  Sparkles, Loader2, ShieldCheck, Award, CheckCircle, 
  FileText, Code, HeartPulse, Settings, FileSearch,
  Building, Home, Laptop, ChevronDown
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { JobCard } from "@/components/shared/JobCard";
import { useTranslation } from "@/utils/i18n";
import api from "@/utils/apiClient";

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

// Location type icons
const LocationTypeIcons = {
  "remote": Laptop,
  "onsite": Building,
  "hybrid": Home
};

// Countries and cities data
const COUNTRIES_DATA = {
  "United States": ["New York", "Los Angeles", "San Francisco", "Chicago", "Seattle", "Austin", "Boston", "Denver", "Atlanta", "Miami", "Dallas", "San Diego", "Phoenix", "Portland", "Washington DC"],
  "United Kingdom": ["London", "Manchester", "Birmingham", "Edinburgh", "Glasgow", "Bristol", "Leeds", "Liverpool", "Cambridge", "Oxford"],
  "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa", "Edmonton", "Winnipeg", "Quebec City"],
  "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne", "Stuttgart", "Düsseldorf"],
  "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra"],
  "India": ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"],
  "Singapore": ["Singapore"],
  "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven"],
  "France": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Bordeaux"],
  "Ireland": ["Dublin", "Cork", "Galway", "Limerick"],
  "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao"],
  "Italy": ["Milan", "Rome", "Turin", "Florence", "Bologna"],
  "Switzerland": ["Zurich", "Geneva", "Basel", "Bern"],
  "Sweden": ["Stockholm", "Gothenburg", "Malmö"],
  "Japan": ["Tokyo", "Osaka", "Yokohama", "Nagoya", "Fukuoka"],
  "South Korea": ["Seoul", "Busan", "Incheon"],
  "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Belo Horizonte"],
  "Mexico": ["Mexico City", "Guadalajara", "Monterrey"],
  "UAE": ["Dubai", "Abu Dhabi", "Sharjah"],
  "Israel": ["Tel Aviv", "Jerusalem", "Haifa"],
  "Poland": ["Warsaw", "Krakow", "Wroclaw", "Gdansk"],
  "Portugal": ["Lisbon", "Porto", "Braga"],
  "Remote/Global": ["Worldwide", "Any Location"]
};

// Location types
const LOCATION_TYPES = [
  { value: "all", label: "All Types", icon: Globe },
  { value: "remote", label: "Remote", icon: Laptop },
  { value: "hybrid", label: "Hybrid", icon: Home },
  { value: "onsite", label: "On-site", icon: Building }
];

const JobSearchPage = ({ savedJobs, onSave, onApply, onAnalyze }) => {
  const { t } = useTranslation();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("all");
  const [country, setCountry] = useState("any");
  const [city, setCity] = useState("any");
  const [locationType, setLocationType] = useState("all");
  const [days, setDays] = useState("0");
  const [presets, setPresets] = useState({ presets: [], locations: [], quality_terms: [] });
  const [deepSearching, setDeepSearching] = useState(false);
  const [searchStats, setSearchStats] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Get cities for selected country
  const availableCities = country && country !== "any" ? COUNTRIES_DATA[country] || [] : [];

  useEffect(() => {
    // Fetch presets using apiClient
    api.client.get('/api/jobs/presets').then(res => setPresets(res.data)).catch(() => {});
    searchJobs();
    // eslint-disable-next-line
  }, []);

  // Reset city when country changes
  useEffect(() => {
    setCity("any");
  }, [country]);

  const searchJobs = async (searchQuery = query) => {
    setLoading(true);
    setSearchStats(null);
    try {
      // Build location string from country/city
      let locationStr = "";
      if (country !== "any") {
        locationStr = country;
        if (city !== "any") {
          locationStr = `${city}, ${country}`;
        }
      }
      
      const response = await api.searchJobs({
        query: searchQuery, 
        source, 
        location: locationStr,
        location_type: locationType !== "all" ? locationType : "",
        days: parseInt(days)
      });
      // API returns { data: { jobs: [...], total: ... } }
      const result = response.data;
      let filteredJobs = result.jobs || result || [];
      
      // Client-side filter for location type if API doesn't support it fully
      if (locationType !== "all") {
        filteredJobs = filteredJobs.filter(job => {
          const jobLocation = (job.location || "").toLowerCase();
          const jobTitle = (job.title || "").toLowerCase();
          const isRemote = jobLocation.includes("remote") || jobTitle.includes("remote");
          const isHybrid = jobLocation.includes("hybrid") || jobTitle.includes("hybrid");
          
          if (locationType === "remote") return isRemote;
          if (locationType === "hybrid") return isHybrid;
          if (locationType === "onsite") return !isRemote && !isHybrid;
          return true;
        });
      }
      
      setJobs(filteredJobs);
    } catch (e) {
      toast.error(t("jobs.searchFailed") || "Failed to fetch jobs");
      setJobs([]);
    }
    setLoading(false);
  };

  const deepSearch = async () => {
    setDeepSearching(true);
    setSearchStats(null);
    try {
      const response = await api.client.post('/api/jobs/deep-search', { use_ai: true });
      setJobs(response.data.jobs || []);
      setSearchStats({
        total: response.data.total_found,
        queries: response.data.queries_used,
        strategy: response.data.search_strategy
      });
      toast.success(t("jobs.deepSearchSuccess", { count: response.data.total_found }) || `AI Deep Search found ${response.data.total_found} relevant jobs!`);
    } catch (e) {
      toast.error(t("jobs.deepSearchFailed") || "Deep search failed");
    }
    setDeepSearching(false);
  };

  const handlePresetClick = (presetQuery) => {
    setQuery(presetQuery);
    searchJobs(presetQuery);
  };

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-7xl mx-auto animate-fade-in" data-testid="job-search-page">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-3" style={{ fontFamily: 'IBM Plex Sans' }}>
          {t("jobs.findYourPerfectJob")}
        </h1>
        <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
          {t("jobs.searchDescription") || "Search across multiple job boards simultaneously with AI-powered matching"}
        </p>
      </div>

      {/* Search Bar */}
      <Card className="mb-6">
        <CardContent className="p-4">
          {/* Main Search Row */}
          <div className="flex flex-col md:flex-row gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
              <Input
                placeholder={t("jobs.searchPlaceholder")}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchJobs()}
                className="pl-10"
                data-testid="job-search-input"
              />
            </div>
            
            {/* Location Type Dropdown */}
            <Select value={locationType} onValueChange={setLocationType}>
              <SelectTrigger className="w-full md:w-40" data-testid="location-type-select">
                {locationType === "remote" && <Laptop className="w-4 h-4 mr-2 text-turquoise" />}
                {locationType === "hybrid" && <Home className="w-4 h-4 mr-2 text-purple-500" />}
                {locationType === "onsite" && <Building className="w-4 h-4 mr-2 text-orange-500" />}
                {locationType === "all" && <Globe className="w-4 h-4 mr-2 text-slate-400" />}
                <SelectValue placeholder="Work Type" />
              </SelectTrigger>
              <SelectContent>
                {LOCATION_TYPES.map(type => {
                  const Icon = type.icon;
                  return (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex items-center gap-2">
                        <Icon className="w-4 h-4" />
                        {type.label}
                      </div>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>

            <Button 
              onClick={() => searchJobs()} 
              disabled={loading}
              className="bg-gradient-to-r from-turquoise to-teal-600"
              data-testid="search-btn"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
              {t("common.search")}
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="md:w-auto"
            >
              <Filter className="w-4 h-4 mr-2" />
              {showAdvanced ? "Less Filters" : "More Filters"}
              <ChevronDown className={`w-4 h-4 ml-2 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
            </Button>
          </div>
          
          {/* Advanced Filters Row */}
          {showAdvanced && (
            <div className="flex flex-col md:flex-row gap-4 pt-4 border-t border-slate-200 dark:border-slate-700 animate-fade-in">
              {/* Country Dropdown */}
              <Select value={country} onValueChange={setCountry}>
                <SelectTrigger className="w-full md:w-48" data-testid="country-select">
                  <Globe className="w-4 h-4 mr-2 text-slate-400" />
                  <SelectValue placeholder="Select Country" />
                </SelectTrigger>
                <SelectContent className="max-h-[300px]">
                  <SelectItem value="any">🌍 Any Country</SelectItem>
                  {Object.keys(COUNTRIES_DATA).map(countryName => (
                    <SelectItem key={countryName} value={countryName}>
                      {countryName === "Remote/Global" ? "🌐 " : ""}
                      {countryName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              {/* City Dropdown (dependent on country) */}
              <Select 
                value={city} 
                onValueChange={setCity}
                disabled={country === "any" || availableCities.length === 0}
              >
                <SelectTrigger className="w-full md:w-48" data-testid="city-select">
                  <MapPin className="w-4 h-4 mr-2 text-slate-400" />
                  <SelectValue placeholder={country === "any" ? "Select Country First" : "Select City"} />
                </SelectTrigger>
                <SelectContent className="max-h-[300px]">
                  <SelectItem value="any">All Cities in {country}</SelectItem>
                  {availableCities.map(cityName => (
                    <SelectItem key={cityName} value={cityName}>
                      {cityName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Source Dropdown */}
              <Select value={source} onValueChange={setSource}>
                <SelectTrigger className="w-full md:w-40" data-testid="source-select">
                  <Globe className="w-4 h-4 mr-2 text-slate-400" />
                  <SelectValue placeholder={t("jobs.source") || "Source"} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t("jobs.allSources") || "All Sources"}</SelectItem>
                  <SelectItem value="indeed">Indeed</SelectItem>
                  <SelectItem value="linkedin">LinkedIn</SelectItem>
                  <SelectItem value="glassdoor">Glassdoor</SelectItem>
                  <SelectItem value="remoteok">RemoteOK</SelectItem>
                  <SelectItem value="remotive">Remotive</SelectItem>
                </SelectContent>
              </Select>

              {/* Date Posted Dropdown */}
              <Select value={days} onValueChange={setDays}>
                <SelectTrigger className="w-full md:w-40" data-testid="days-select">
                  <Calendar className="w-4 h-4 mr-2 text-slate-400" />
                  <SelectValue placeholder={t("jobs.postedDate")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">{t("jobs.anyTime") || "Any Time"}</SelectItem>
                  <SelectItem value="1">{t("jobs.last24h") || "Last 24h"}</SelectItem>
                  <SelectItem value="3">{t("jobs.last3Days") || "Last 3 Days"}</SelectItem>
                  <SelectItem value="7">{t("jobs.lastWeek") || "Last Week"}</SelectItem>
                  <SelectItem value="30">{t("jobs.lastMonth") || "Last Month"}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
          
          {/* Active Filters Display */}
          {(country !== "any" || locationType !== "all" || city !== "any") && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <span className="text-sm text-slate-500">Active filters:</span>
              {locationType !== "all" && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  {locationType === "remote" && <Laptop className="w-3 h-3" />}
                  {locationType === "hybrid" && <Home className="w-3 h-3" />}
                  {locationType === "onsite" && <Building className="w-3 h-3" />}
                  {LOCATION_TYPES.find(t => t.value === locationType)?.label}
                  <button 
                    onClick={() => setLocationType("all")}
                    className="ml-1 hover:text-red-500"
                  >×</button>
                </Badge>
              )}
              {country !== "any" && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Globe className="w-3 h-3" />
                  {country}
                  <button 
                    onClick={() => { setCountry("any"); setCity("any"); }}
                    className="ml-1 hover:text-red-500"
                  >×</button>
                </Badge>
              )}
              {city !== "any" && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {city}
                  <button 
                    onClick={() => setCity("any")}
                    className="ml-1 hover:text-red-500"
                  >×</button>
                </Badge>
              )}
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => { setCountry("any"); setCity("any"); setLocationType("all"); }}
                className="text-xs text-red-500 hover:text-red-700"
              >
                Clear all
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Deep Search */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Filter className="w-4 h-4" />
          {jobs.length} {t("jobs.jobsFound") || "jobs found"}
        </div>
        <Button 
          variant="outline" 
          onClick={deepSearch}
          disabled={deepSearching}
          className="gap-2"
          data-testid="deep-search-btn"
        >
          {deepSearching ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4 text-violet-500" />
          )}
          {t("jobs.aiDeepSearch") || "AI Deep Search"}
        </Button>
      </div>

      {/* Search Stats */}
      {searchStats && (
        <Card className="mb-6 bg-violet-50 dark:bg-violet-900/20 border-violet-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <Sparkles className="w-5 h-5 text-violet-500" />
              <div>
                <p className="font-medium text-violet-700 dark:text-violet-300">
                  {t("jobs.deepSearchResults") || "AI Deep Search Results"}
                </p>
                <p className="text-sm text-violet-600 dark:text-violet-400">
                  {t("jobs.foundJobs", { count: searchStats.total }) || `Found ${searchStats.total} jobs`} • {searchStats.queries} {t("jobs.queriesUsed") || "queries used"} • {searchStats.strategy}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Presets */}
      {presets.presets?.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6">
          {presets.presets.map((preset, idx) => {
            const IconComponent = PresetIcons[preset.icon] || FileSearch;
            return (
              <Badge
                key={idx}
                variant="outline"
                className="cursor-pointer hover:bg-turquoise/10 hover:border-turquoise transition-colors py-2 px-3"
                onClick={() => handlePresetClick(preset.query)}
              >
                <IconComponent className="w-4 h-4 mr-2" />
                {preset.name}
              </Badge>
            );
          })}
        </div>
      )}

      {/* Job Results */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">
          <Search className="w-12 h-12 text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300">{t("jobs.noJobsFound")}</h3>
          <p className="text-slate-500">{t("jobs.tryDifferentSearch")}</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map(job => (
            <JobCard 
              key={job.id} 
              job={job}
              isSaved={savedJobs.some(s => s.job?.id === job.id)}
              onSave={onSave}
              onApply={onApply}
              onAnalyze={onAnalyze}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default JobSearchPage;
