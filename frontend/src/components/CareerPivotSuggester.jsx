import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, ArrowRight, Award, Briefcase, DollarSign,
  ChevronRight, Sparkles, Target, BookOpen, CheckCircle2
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CareerPivotSuggester = ({ userProfile, currentSector, currentRole }) => {
  const [pivots, setPivots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPivot, setSelectedPivot] = useState(null);

  useEffect(() => {
    if (currentSector) {
      fetchPivots();
    }
  }, [currentSector, currentRole]);

  const fetchPivots = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        current_sector: currentSector,
        ...(currentRole && { current_role: currentRole })
      });
      
      const response = await fetch(`${API_URL}/api/taxonomy/career-pivots/suggest?${params}`);
      const data = await response.json();
      setPivots(data.suggestions || []);
    } catch (error) {
      console.error('Failed to fetch career pivots:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'low':
        return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'high':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 animate-pulse">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
          <div className="h-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (!currentSector || pivots.length === 0) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">Career Pivot Opportunities</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Complete your profile to see personalized career transition paths
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
      data-testid="career-pivot-suggester"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-5 text-white">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Career Pivot Opportunities</h3>
            <p className="text-purple-100 text-sm">
              Cross-sector transitions based on your experience
            </p>
          </div>
        </div>
      </div>

      {/* Pivot Suggestions */}
      <div className="p-5 space-y-4">
        {pivots.map((sectorGroup, groupIdx) => (
          <div key={groupIdx} className="space-y-3">
            {/* Target Sector Header */}
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-gray-400" />
              <span 
                className="text-sm font-medium px-2 py-0.5 rounded-full"
                style={{ 
                  backgroundColor: `${sectorGroup.sector?.color}20`,
                  color: sectorGroup.sector?.color
                }}
              >
                {sectorGroup.sector?.name || 'Other Sector'}
              </span>
            </div>

            {/* Pivot Cards */}
            {sectorGroup.pivots?.map((pivot, pivotIdx) => (
              <div
                key={pivotIdx}
                className={`border rounded-xl p-4 transition-all cursor-pointer ${
                  selectedPivot === `${groupIdx}-${pivotIdx}`
                    ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-md'
                    : 'border-gray-200 dark:border-gray-700 hover:border-purple-300 hover:shadow-sm'
                }`}
                onClick={() => setSelectedPivot(
                  selectedPivot === `${groupIdx}-${pivotIdx}` ? null : `${groupIdx}-${pivotIdx}`
                )}
              >
                {/* Transition Header */}
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {pivot.from_role}
                      </span>
                      <ArrowRight className="w-4 h-4 text-purple-500 flex-shrink-0" />
                      <span className="font-medium text-purple-600 dark:text-purple-400">
                        {pivot.to_role}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div className="flex items-center gap-3 flex-wrap">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(pivot.difficulty)}`}>
                    {pivot.difficulty} difficulty
                  </span>
                  <span className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400 font-medium">
                    <DollarSign className="w-4 h-4" />
                    {pivot.salary_change}
                  </span>
                </div>

                {/* Expanded Details */}
                {selectedPivot === `${groupIdx}-${pivotIdx}` && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
                    {/* Transferable Skills */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-amber-500" />
                        Transferable Skills
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {pivot.transferable_skills?.map((skill, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 rounded-full text-xs"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Bridge Certifications */}
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                        <Award className="w-4 h-4 text-blue-500" />
                        Bridge Certifications (Recommended)
                      </h5>
                      <div className="flex flex-wrap gap-2">
                        {pivot.bridge_certifications?.map((cert, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium"
                          >
                            {cert}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Action Button */}
                    <button className="w-full py-2 px-4 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors">
                      <BookOpen className="w-4 h-4" />
                      View Learning Path
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Footer CTA */}
      <div className="px-5 pb-5">
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-800/50 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-teal-500" />
            <span className="text-sm text-gray-600 dark:text-gray-300">
              {pivots.reduce((acc, g) => acc + (g.pivots?.length || 0), 0)} career paths available
            </span>
          </div>
          <button className="text-sm font-medium text-teal-600 dark:text-teal-400 hover:text-teal-700 flex items-center gap-1">
            See all <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CareerPivotSuggester;
