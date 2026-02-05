import React, { useState, useEffect } from 'react';
import { 
  FlaskConical, HeartPulse, Cog, Building2, Cpu, 
  ChevronRight, Award, Briefcase, TrendingUp, Search,
  ArrowRight, Star, Filter, X
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Icon mapping for sectors
const SECTOR_ICONS = {
  life_sciences: FlaskConical,
  medical_devices: HeartPulse,
  engineering: Cog,
  healthcare_ops: Building2,
  technology: Cpu
};

const TaxonomyBrowser = ({ onSelectSector, onSelectRole, compact = false }) => {
  const [sectors, setSectors] = useState([]);
  const [selectedSector, setSelectedSector] = useState(null);
  const [sectorDetails, setSectorDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchSectors();
  }, []);

  const fetchSectors = async () => {
    try {
      const response = await fetch(`${API_URL}/api/taxonomy/sectors`);
      const data = await response.json();
      setSectors(data.sectors || []);
    } catch (error) {
      console.error('Failed to fetch sectors:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSectorDetails = async (sectorId) => {
    setLoadingDetails(true);
    try {
      const response = await fetch(`${API_URL}/api/taxonomy/sectors/${sectorId}`);
      const data = await response.json();
      setSectorDetails(data);
    } catch (error) {
      console.error('Failed to fetch sector details:', error);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleSectorClick = (sector) => {
    // If clicking the same sector, toggle it off
    if (selectedSector?.id === sector.id) {
      setSelectedSector(null);
      setSectorDetails(null);
      return;
    }
    setSelectedSector(sector);
    setSectorDetails(null); // Clear previous details
    fetchSectorDetails(sector.id);
    if (onSelectSector) onSelectSector(sector);
  };

  const handleRoleClick = (role) => {
    if (onSelectRole) onSelectRole(role);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
      </div>
    );
  }

  if (compact) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Browse by Sector
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {sectors.map((sector) => {
            const Icon = SECTOR_ICONS[sector.id] || Briefcase;
            return (
              <button
                key={sector.id}
                onClick={() => handleSectorClick(sector)}
                className={`p-3 rounded-lg border-2 transition-all text-center hover:scale-105 ${
                  selectedSector?.id === sector.id
                    ? 'border-teal-500 bg-teal-50 dark:bg-teal-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-teal-300'
                }`}
                style={{ borderColor: selectedSector?.id === sector.id ? sector.color : undefined }}
              >
                <Icon 
                  className="w-6 h-6 mx-auto mb-2" 
                  style={{ color: sector.color }}
                />
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300 line-clamp-2">
                  {sector.name.split('&')[0].trim()}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="taxonomy-browser">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-600 to-blue-600 rounded-xl p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">MedMatch Global Talent Taxonomy</h2>
        <p className="text-teal-100">
          Explore careers across Life Sciences, Medical Devices, Engineering, Healthcare & Technology
        </p>
      </div>

      {/* Sector Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {sectors.map((sector) => {
          const Icon = SECTOR_ICONS[sector.id] || Briefcase;
          const isSelected = selectedSector?.id === sector.id;
          
          return (
            <button
              key={sector.id}
              onClick={() => handleSectorClick(sector)}
              className={`p-5 rounded-xl border-2 transition-all text-left hover:shadow-lg ${
                isSelected
                  ? 'border-2 shadow-lg scale-[1.02]'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
              }`}
              style={{ 
                borderColor: isSelected ? sector.color : undefined,
                backgroundColor: isSelected ? `${sector.color}10` : undefined
              }}
              data-testid={`sector-${sector.id}`}
            >
              <div 
                className="w-12 h-12 rounded-lg flex items-center justify-center mb-3"
                style={{ backgroundColor: `${sector.color}20` }}
              >
                <Icon className="w-6 h-6" style={{ color: sector.color }} />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                {sector.name}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                {sector.description}
              </p>
              <div className="mt-3 flex items-center text-xs font-medium" style={{ color: sector.color }}>
                {Object.keys(sector.subsectors || {}).length} subsectors
                <ChevronRight className="w-4 h-4 ml-1" />
              </div>
            </button>
          );
        })}
      </div>

      {/* Sector Details Panel */}
      {selectedSector && sectorDetails && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          {/* Sector Header */}
          <div 
            className="p-6 border-b border-gray-200 dark:border-gray-700"
            style={{ backgroundColor: `${selectedSector.color}10` }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {(() => {
                  const Icon = SECTOR_ICONS[selectedSector.id] || Briefcase;
                  return (
                    <div 
                      className="w-14 h-14 rounded-xl flex items-center justify-center"
                      style={{ backgroundColor: `${selectedSector.color}20` }}
                    >
                      <Icon className="w-7 h-7" style={{ color: selectedSector.color }} />
                    </div>
                  );
                })()}
                <div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                    {selectedSector.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {selectedSector.description}
                  </p>
                </div>
              </div>
              <button 
                onClick={() => {
                  setSelectedSector(null);
                  setSectorDetails(null);
                }}
                className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Subsectors & Roles */}
          <div className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Roles & Positions
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(sectorDetails.sector?.subsectors || {}).map(([subId, subsector]) => (
                <div 
                  key={subId}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                >
                  <h5 className="font-medium text-gray-900 dark:text-white mb-3">
                    {subsector.name}
                  </h5>
                  <div className="space-y-2">
                    {subsector.roles?.map((role, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleRoleClick({ role, sector: selectedSector, subsector })}
                        className="w-full text-left px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300 flex items-center justify-between group"
                      >
                        {role}
                        <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications */}
          {sectorDetails.certifications?.length > 0 && (
            <div className="p-6 border-t border-gray-200 dark:border-gray-700">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Award className="w-5 h-5" />
                Relevant Certifications
              </h4>
              <div className="flex flex-wrap gap-2">
                {sectorDetails.certifications.map((cert, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 rounded-full text-sm font-medium"
                    title={cert.name}
                  >
                    {cert.code}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Career Pivots */}
          {sectorDetails.career_pivots_from?.length > 0 && (
            <div className="p-6 border-t border-gray-200 dark:border-gray-700">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Career Pivot Opportunities
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {sectorDetails.career_pivots_from.slice(0, 4).map((pivot, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-teal-300 transition-colors"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {pivot.from_role}
                      </span>
                      <ArrowRight className="w-4 h-4 text-teal-500" />
                      <span className="text-sm font-medium text-teal-600 dark:text-teal-400">
                        {pivot.to_role}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={`px-2 py-0.5 rounded-full ${
                        pivot.difficulty === 'low' ? 'bg-green-100 text-green-700' :
                        pivot.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {pivot.difficulty} difficulty
                      </span>
                      <span className="text-green-600 font-medium">{pivot.salary_change}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TaxonomyBrowser;
