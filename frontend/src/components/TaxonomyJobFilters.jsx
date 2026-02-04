import React, { useState, useEffect } from 'react';
import { 
  Filter, ChevronDown, ChevronUp, X, Search, Award, 
  Briefcase, TrendingUp, Building2, MapPin
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TaxonomyJobFilters = ({ onFiltersChange, initialFilters = {} }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [sectors, setSectors] = useState([]);
  const [certifications, setCertifications] = useState([]);
  const [seniorityTiers, setSeniorityTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [filters, setFilters] = useState({
    sector: initialFilters.sector || '',
    subsector: initialFilters.subsector || '',
    seniority: initialFilters.seniority || '',
    certifications: initialFilters.certifications || [],
    ...initialFilters
  });

  const [subsectors, setSubsectors] = useState([]);

  useEffect(() => {
    fetchTaxonomyData();
  }, []);

  useEffect(() => {
    // Update subsectors when sector changes
    if (filters.sector) {
      const sector = sectors.find(s => s.id === filters.sector);
      if (sector?.subsectors) {
        setSubsectors(Object.entries(sector.subsectors).map(([id, sub]) => ({
          id,
          name: sub.name
        })));
      }
    } else {
      setSubsectors([]);
    }
  }, [filters.sector, sectors]);

  const fetchTaxonomyData = async () => {
    try {
      const [sectorsRes, certsRes, tiersRes] = await Promise.all([
        fetch(`${API_URL}/api/taxonomy/sectors`),
        fetch(`${API_URL}/api/taxonomy/certifications`),
        fetch(`${API_URL}/api/taxonomy/seniority-tiers`)
      ]);
      
      const sectorsData = await sectorsRes.json();
      const certsData = await certsRes.json();
      const tiersData = await tiersRes.json();
      
      setSectors(sectorsData.sectors || []);
      setCertifications(certsData.certifications || []);
      setSeniorityTiers(tiersData.tiers || []);
    } catch (error) {
      console.error('Failed to fetch taxonomy data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateFilter = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    
    // Reset subsector if sector changes
    if (key === 'sector') {
      newFilters.subsector = '';
    }
    
    setFilters(newFilters);
    onFiltersChange?.(newFilters);
  };

  const toggleCertification = (certCode) => {
    const current = filters.certifications || [];
    const updated = current.includes(certCode)
      ? current.filter(c => c !== certCode)
      : [...current, certCode];
    updateFilter('certifications', updated);
  };

  const clearFilters = () => {
    const cleared = {
      sector: '',
      subsector: '',
      seniority: '',
      certifications: []
    };
    setFilters(cleared);
    onFiltersChange?.(cleared);
  };

  const activeFilterCount = [
    filters.sector,
    filters.subsector,
    filters.seniority,
    ...(filters.certifications || [])
  ].filter(Boolean).length;

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 animate-pulse">
        <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
      </div>
    );
  }

  return (
    <div 
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700"
      data-testid="taxonomy-job-filters"
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors rounded-xl"
      >
        <div className="flex items-center gap-3">
          <Filter className="w-5 h-5 text-teal-600" />
          <span className="font-medium text-gray-900 dark:text-white">
            Life Sciences & Engineering Filters
          </span>
          {activeFilterCount > 0 && (
            <span className="px-2 py-0.5 bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 rounded-full text-xs font-medium">
              {activeFilterCount} active
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {/* Expanded Filters */}
      {isExpanded && (
        <div className="p-4 pt-0 space-y-4 border-t border-gray-200 dark:border-gray-700">
          {/* Sector Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <Briefcase className="w-4 h-4 inline mr-2" />
              Sector
            </label>
            <select
              value={filters.sector}
              onChange={(e) => updateFilter('sector', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-teal-500"
              data-testid="sector-filter"
            >
              <option value="">All Sectors</option>
              {sectors.map((sector) => (
                <option key={sector.id} value={sector.id}>
                  {sector.name}
                </option>
              ))}
            </select>
          </div>

          {/* Subsector Selection (conditional) */}
          {subsectors.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Subsector
              </label>
              <select
                value={filters.subsector}
                onChange={(e) => updateFilter('subsector', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-teal-500"
                data-testid="subsector-filter"
              >
                <option value="">All Subsectors</option>
                {subsectors.map((sub) => (
                  <option key={sub.id} value={sub.id}>
                    {sub.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Seniority Tier */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <TrendingUp className="w-4 h-4 inline mr-2" />
              Seniority Level
            </label>
            <select
              value={filters.seniority}
              onChange={(e) => updateFilter('seniority', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-teal-500"
              data-testid="seniority-filter"
            >
              <option value="">All Levels</option>
              {seniorityTiers.map((tier) => (
                <option key={tier.level} value={`tier_${tier.level}`}>
                  Tier {tier.level}: {tier.name} ({tier.years_experience} yrs)
                </option>
              ))}
            </select>
          </div>

          {/* Certifications (multi-select chips) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <Award className="w-4 h-4 inline mr-2" />
              Required Certifications
            </label>
            <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto p-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-900/50">
              {certifications.slice(0, 20).map((cert) => {
                const isSelected = (filters.certifications || []).includes(cert.code);
                return (
                  <button
                    key={cert.code}
                    onClick={() => toggleCertification(cert.code)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      isSelected
                        ? 'bg-teal-500 text-white'
                        : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:border-teal-400'
                    }`}
                    title={cert.name}
                  >
                    {cert.code}
                  </button>
                );
              })}
            </div>
            {(filters.certifications || []).length > 0 && (
              <div className="mt-2 text-xs text-gray-500">
                Selected: {(filters.certifications || []).join(', ')}
              </div>
            )}
          </div>

          {/* Clear Filters */}
          {activeFilterCount > 0 && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-2 text-sm text-red-600 hover:text-red-700 dark:text-red-400"
            >
              <X className="w-4 h-4" />
              Clear all filters
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default TaxonomyJobFilters;
