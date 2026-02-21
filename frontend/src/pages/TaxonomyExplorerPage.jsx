import React, { useState, useEffect } from 'react';
import { useTranslation } from "@/utils/i18n";
import { useNavigate } from 'react-router-dom';
import { 
  FlaskConical, HeartPulse, Cog, Building2, Cpu, Search,
  Award, Briefcase, TrendingUp, ChevronRight, ArrowRight,
  Target, GraduationCap, Building, Users
} from 'lucide-react';
import TaxonomyBrowser from '../components/TaxonomyBrowser';
import CareerPivotSuggester from '../components/CareerPivotSuggester';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TaxonomyExplorerPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [selectedSector, setSelectedSector] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_URL}/api/taxonomy/summary`);
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await fetch(`${API_URL}/api/taxonomy/roles/match?title=${encodeURIComponent(searchQuery)}`);
      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleRoleSelect = (roleData) => {
    // Navigate to job search with role filter
    navigate(`/job-search?role=${encodeURIComponent(roleData.role)}&sector=${roleData.sector?.id || ''}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900" data-testid="taxonomy-explorer-page">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-teal-600 via-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4">
              MedMatch Global Talent Ecosystem
            </h1>
            <p className="text-xl text-teal-100 max-w-3xl mx-auto">
              Connecting Life Sciences, Medical Devices, Engineering, Healthcare & Technology
              — from Entry-Level to Executive
            </p>
          </div>

          {/* Stats */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{summary.summary?.total_sectors}</div>
                <div className="text-sm text-teal-200">Sectors</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{summary.summary?.total_subsectors}</div>
                <div className="text-sm text-teal-200">Subsectors</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{summary.summary?.total_roles}</div>
                <div className="text-sm text-teal-200">Roles</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{summary.summary?.total_certifications}</div>
                <div className="text-sm text-teal-200">Certifications</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{summary.summary?.total_skills}</div>
                <div className="text-sm text-teal-200">Skills</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{summary.summary?.total_career_pivots}</div>
                <div className="text-sm text-teal-200">Career Paths</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <div className="text-3xl font-bold">{summary.summary?.seniority_tiers}</div>
                <div className="text-sm text-teal-200">Tiers</div>
              </div>
            </div>
          )}

          {/* Search */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <input
                type="text"
                placeholder={t("taxonomy.searchPlaceholder")}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full px-5 py-4 pl-12 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30"
              />
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/60" />
              <button
                onClick={handleSearch}
                className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-white text-teal-600 rounded-lg font-medium hover:bg-teal-50 transition-colors"
              >
                Match
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="max-w-7xl mx-auto px-4 -mt-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-teal-500" />
              Match Results for "{searchResults.title}"
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Matched Sector */}
              {searchResults.matched_sector && (
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    Matched Sector
                  </h4>
                  <div 
                    className="flex items-center gap-3 p-3 rounded-lg"
                    style={{ backgroundColor: `${searchResults.matched_sector.color}15` }}
                  >
                    <div 
                      className="w-10 h-10 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${searchResults.matched_sector.color}25` }}
                    >
                      <Briefcase className="w-5 h-5" style={{ color: searchResults.matched_sector.color }} />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {searchResults.matched_sector.name}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {searchResults.matched_sector.description}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Estimated Tier */}
              {searchResults.estimated_tier && (
                <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                    Estimated Seniority
                  </h4>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                    <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/40 flex items-center justify-center">
                      <GraduationCap className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        Tier {searchResults.estimated_tier.level}: {searchResults.estimated_tier.name}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {searchResults.estimated_tier.years_experience} years experience
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Recommendations */}
            {(searchResults.recommended_certifications?.length > 0 || searchResults.recommended_skills?.length > 0) && (
              <div className="mt-6 grid md:grid-cols-2 gap-6">
                {searchResults.recommended_certifications?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                      <Award className="w-4 h-4 text-amber-500" />
                      Recommended Certifications
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {searchResults.recommended_certifications.map((cert, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 rounded-full text-sm font-medium"
                          title={cert.name}
                        >
                          {cert.code}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {searchResults.recommended_skills?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-blue-500" />
                      Key Skills
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {searchResults.recommended_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-full text-sm"
                        >
                          {skill.name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Search Jobs Button */}
            <div className="mt-6">
              <button
                onClick={() => navigate(`/job-search?q=${encodeURIComponent(searchResults.title)}`)}
                className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
              >
                <Search className="w-5 h-5" />
                Search Jobs for "{searchResults.title}"
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Browser - 2 columns */}
          <div className="lg:col-span-2">
            <TaxonomyBrowser 
              onSelectSector={setSelectedSector}
              onSelectRole={handleRoleSelect}
            />
          </div>

          {/* Sidebar - Career Pivots */}
          <div className="space-y-6">
            <CareerPivotSuggester 
              currentSector={selectedSector?.id || 'engineering'}
            />

            {/* Seniority Guide */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-purple-500" />
                Seniority Tiers
              </h3>
              <div className="space-y-3">
                {[
                  { tier: 1, name: 'Support / Entry', years: '0-2 yrs', color: 'bg-green-500' },
                  { tier: 2, name: 'Professional', years: '2-5 yrs', color: 'bg-blue-500' },
                  { tier: 3, name: 'Management', years: '5-10 yrs', color: 'bg-yellow-500' },
                  { tier: 4, name: 'Director', years: '10-15 yrs', color: 'bg-orange-500' },
                  { tier: 5, name: 'Executive', years: '15+ yrs', color: 'bg-red-500' }
                ].map((tier) => (
                  <div key={tier.tier} className="flex items-center gap-3">
                    <div className={`w-2 h-8 rounded-full ${tier.color}`}></div>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        Tier {tier.tier}: {tier.name}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {tier.years}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Links */}
            <div className="bg-gradient-to-br from-teal-50 to-blue-50 dark:from-teal-900/20 dark:to-blue-900/20 rounded-xl p-5 border border-teal-200 dark:border-teal-800">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                Popular Searches
              </h3>
              <div className="space-y-2">
                {[
                  'Biomedical Engineer',
                  'Clinical Research Associate',
                  'Regulatory Affairs Manager',
                  'Healthcare Data Analyst',
                  'Medical Device Sales'
                ].map((term) => (
                  <button
                    key={term}
                    onClick={() => {
                      setSearchQuery(term);
                      handleSearch();
                    }}
                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-white dark:hover:bg-gray-800 text-sm text-gray-700 dark:text-gray-300 flex items-center justify-between group transition-colors"
                  >
                    {term}
                    <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaxonomyExplorerPage;
