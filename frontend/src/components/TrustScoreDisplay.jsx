import React, { useState, useEffect } from 'react';
import { 
  Shield, Award, User, Zap, Calendar, Star, TrendingUp,
  ChevronRight, CheckCircle, ArrowUp, Info, Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useTranslation } from '@/utils/i18n';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Level color mapping
const LEVEL_COLORS = {
  'Building': { bg: 'bg-gray-100 dark:bg-gray-800', text: 'text-gray-600 dark:text-gray-400', ring: 'ring-gray-300', gradient: 'from-gray-400 to-gray-500' },
  'Emerging': { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-600 dark:text-blue-400', ring: 'ring-blue-300', gradient: 'from-blue-400 to-blue-600' },
  'Established': { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-600 dark:text-green-400', ring: 'ring-green-300', gradient: 'from-green-400 to-emerald-600' },
  'Trusted': { bg: 'bg-purple-100 dark:bg-purple-900/30', text: 'text-purple-600 dark:text-purple-400', ring: 'ring-purple-300', gradient: 'from-purple-400 to-purple-600' },
  'Elite': { bg: 'bg-amber-100 dark:bg-amber-900/30', text: 'text-amber-600 dark:text-amber-400', ring: 'ring-amber-300', gradient: 'from-amber-400 to-orange-500' },
  'Expert': { bg: 'bg-gradient-to-r from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-600', text: 'text-slate-700 dark:text-slate-200', ring: 'ring-slate-400', gradient: 'from-slate-500 to-slate-700' },
};

// Category icons
const CATEGORY_ICONS = {
  'credentials': Award,
  'profile': User,
  'engagement': Zap,
  'tenure': Calendar,
  'reviews': Star,
};

/**
 * TrustScoreDisplay - Shows user's trust score with breakdown
 */
const TrustScoreDisplay = ({ 
  userId = null,
  compact = false,
  showBreakdown = true,
  showTips = true,
  onNavigate = null,
}) => {
  const { t } = useTranslation();
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetchTrustScore();
  }, [userId]);

  const fetchTrustScore = async () => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('medmatch-token');
      const endpoint = userId 
        ? `${API_URL}/api/credentials/trust-score/${userId}`
        : `${API_URL}/api/credentials/trust-score`;
      
      const response = await fetch(endpoint, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setScoreData(data);
      }
    } catch (error) {
      console.error('Failed to fetch trust score:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse bg-gray-100 dark:bg-gray-800 rounded-xl p-6 h-32" />
    );
  }

  if (!scoreData) {
    // Show a placeholder for new users without a trust score
    return (
      <Card className="border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
              <Shield className="w-6 h-6 text-gray-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">Build Your Trust Score</h3>
              <p className="text-sm text-gray-500">Complete your profile and add credentials to build trust with recruiters</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const levelColors = LEVEL_COLORS[scoreData.level?.name] || LEVEL_COLORS['Building'];

  // Compact badge display
  if (compact) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full ${levelColors.bg} cursor-pointer`}>
              <Shield className={`w-4 h-4 ${levelColors.text}`} />
              <span className={`font-semibold text-sm ${levelColors.text}`}>
                {scoreData.total_score}
              </span>
              <Badge variant="outline" className={`text-xs ${levelColors.text} border-current`}>
                {scoreData.level?.name}
              </Badge>
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs p-3">
            <p className="font-medium mb-1">Trust Score: {scoreData.total_score} / {scoreData.max_score}</p>
            <p className="text-xs text-gray-500">{scoreData.level?.description}</p>
            {scoreData.next_level && (
              <p className="text-xs text-blue-500 mt-1">
                {scoreData.next_level.points_needed} more points to {scoreData.next_level.name}
              </p>
            )}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  // Full display
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden" data-testid="trust-score-display">
      {/* Header with score */}
      <div className={`p-5 bg-gradient-to-br ${levelColors.gradient} text-white`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-16 h-16 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center ring-2 ${levelColors.ring}`}>
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm opacity-90">Trust Score</p>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold">{scoreData.total_score}</span>
                <span className="text-lg opacity-75">/ {scoreData.max_score}</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <Badge className="bg-white/20 text-white border-white/30 text-sm px-3 py-1">
              <Sparkles className="w-3 h-3 mr-1" />
              {scoreData.level?.name}
            </Badge>
            <p className="text-xs opacity-75 mt-2">{scoreData.level?.description}</p>
          </div>
        </div>
        
        {/* Progress to next level */}
        {scoreData.next_level && (
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="opacity-75">Progress to {scoreData.next_level.name}</span>
              <span className="font-medium">{scoreData.next_level.points_needed} pts to go</span>
            </div>
            <Progress 
              value={scoreData.percentage} 
              className="h-2 bg-white/20" 
            />
          </div>
        )}
      </div>

      {/* Category breakdown */}
      {showBreakdown && (
        <div className="p-5 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900 dark:text-white">Score Breakdown</h4>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setExpanded(!expanded)}
              className="text-xs"
            >
              {expanded ? 'Collapse' : 'Expand'} Details
              <ChevronRight className={`w-4 h-4 ml-1 transition-transform ${expanded ? 'rotate-90' : ''}`} />
            </Button>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {Object.entries(scoreData.breakdown || {}).map(([category, data]) => {
              const Icon = CATEGORY_ICONS[category] || Shield;
              const hasPoints = data.points > 0;
              
              return (
                <div 
                  key={category}
                  className={`p-3 rounded-lg border ${
                    hasPoints 
                      ? 'bg-gray-50 dark:bg-gray-700/50 border-gray-200 dark:border-gray-600' 
                      : 'bg-gray-50/50 dark:bg-gray-800/50 border-dashed border-gray-200 dark:border-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-4 h-4 ${hasPoints ? 'text-teal-500' : 'text-gray-400'}`} />
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-300 capitalize">
                      {category}
                    </span>
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className={`text-xl font-bold ${hasPoints ? 'text-gray-900 dark:text-white' : 'text-gray-400'}`}>
                      {data.points}
                    </span>
                    <span className="text-xs text-gray-400">pts</span>
                  </div>
                  {data.percentage !== undefined && (
                    <Progress value={data.percentage} className="h-1 mt-2" />
                  )}
                </div>
              );
            })}
          </div>

          {/* Expanded details */}
          {expanded && (
            <div className="mt-4 space-y-3">
              {Object.entries(scoreData.breakdown || {}).map(([category, data]) => {
                if (!data.details?.length) return null;
                
                return (
                  <div key={category} className="border-t border-gray-100 dark:border-gray-700 pt-3">
                    <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                      {category} Details
                    </h5>
                    <div className="space-y-1">
                      {data.details.map((detail, idx) => (
                        <div key={idx} className="flex items-center justify-between text-sm">
                          <span className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
                            <CheckCircle className="w-3 h-3 text-green-500" />
                            {detail.item}
                          </span>
                          <span className="font-medium text-gray-900 dark:text-white">
                            +{detail.points}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Improvement tips */}
      {showTips && scoreData.improvement_tips?.length > 0 && (
        <div className="p-5 bg-blue-50 dark:bg-blue-900/20 border-t border-blue-100 dark:border-blue-900/30">
          <h4 className="font-medium text-blue-900 dark:text-blue-200 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Boost Your Score
          </h4>
          <div className="space-y-2">
            {scoreData.improvement_tips.map((tip, idx) => (
              <div 
                key={idx}
                className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded-lg cursor-pointer hover:shadow-sm transition-shadow"
                onClick={() => onNavigate?.(tip.action)}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                    tip.priority === 'high' ? 'bg-red-100 text-red-600' :
                    tip.priority === 'medium' ? 'bg-amber-100 text-amber-600' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    <ArrowUp className="w-3 h-3" />
                  </div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{tip.tip}</span>
                </div>
                <Badge variant="outline" className="text-xs text-green-600 border-green-200">
                  +{tip.potential_points}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * TrustScoreBadge - Compact inline badge for displaying trust score
 */
export const TrustScoreBadge = ({ score, level, size = 'sm' }) => {
  const levelColors = LEVEL_COLORS[level] || LEVEL_COLORS['Building'];
  
  const sizeClasses = {
    'xs': 'text-xs px-2 py-0.5',
    'sm': 'text-sm px-2.5 py-1',
    'md': 'text-base px-3 py-1.5',
  };
  
  return (
    <div className={`inline-flex items-center gap-1.5 rounded-full ${levelColors.bg} ${sizeClasses[size]}`}>
      <Shield className={`${size === 'xs' ? 'w-3 h-3' : 'w-4 h-4'} ${levelColors.text}`} />
      <span className={`font-semibold ${levelColors.text}`}>{score}</span>
    </div>
  );
};

export default TrustScoreDisplay;
