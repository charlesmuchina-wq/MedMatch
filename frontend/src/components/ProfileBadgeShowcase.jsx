import React, { useState, useEffect } from 'react';
import { 
  Award, Shield, ChevronRight, ExternalLink, RefreshCw,
  CheckCircle, Star, Verified
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { useTranslation } from '@/utils/i18n';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * ProfileBadgeShowcase - Displays verified digital badges prominently
 * Used in user dashboard, profile views, and recruiter candidate views
 */
const ProfileBadgeShowcase = ({ 
  userId = null, // If null, fetches current user's badges
  showConnectButton = true,
  maxBadges = 6,
  compact = false,
  onBadgeClick = null
}) => {
  const [badges, setBadges] = useState([]);
  const [credlyStatus, setCredlyStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    fetchBadges();
    if (!userId) {
      fetchCredlyStatus();
    }
  }, [userId]);

  const fetchBadges = async () => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('medmatch-token');
      const endpoint = userId 
        ? `${API_URL}/api/credentials/user/${userId}/badges`
        : `${API_URL}/api/credentials/credly/badges`;
      
      const response = await fetch(endpoint, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBadges(data.badges || []);
      }
    } catch (error) {
      console.error('Failed to fetch badges:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCredlyStatus = async () => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('medmatch-token');
      const response = await fetch(`${API_URL}/api/credentials/credly/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCredlyStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch Credly status:', error);
    }
  };

  const handleConnectCredly = async () => {
    setConnecting(true);
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('medmatch-token');
      const response = await fetch(`${API_URL}/api/credentials/credly/auth`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      
      if (data.auth_url) {
        // Demo mode simulation
        if (data.auth_url.includes('DEMO_CLIENT')) {
          const callbackResponse = await fetch(
            `${API_URL}/api/credentials/credly/callback?code=demo_code&state=${data.state}`,
            { headers: { 'Authorization': `Bearer ${token}` } }
          );
          const callbackData = await callbackResponse.json();
          
          if (callbackData.success) {
            toast.success(`Imported ${callbackData.imported_count} badges!`);
            fetchBadges();
            fetchCredlyStatus();
          }
        } else {
          window.location.href = data.auth_url;
        }
      }
    } catch (error) {
      toast.error('Failed to connect to Credly');
    } finally {
      setConnecting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-6">
        <RefreshCw className="w-5 h-5 animate-spin text-gray-400" />
      </div>
    );
  }

  // Compact mode for smaller display areas
  if (compact) {
    return (
      <div className="flex items-center gap-2 flex-wrap">
        {badges.slice(0, maxBadges).map((badge, idx) => (
          <div 
            key={badge.id || idx}
            className="relative group cursor-pointer"
            onClick={() => onBadgeClick?.(badge) || window.open(badge.badge_url, '_blank')}
            title={badge.credential_name}
          >
            {badge.badge_image_url ? (
              <img 
                src={badge.badge_image_url} 
                alt={badge.credential_name}
                className="w-10 h-10 rounded-lg object-contain bg-white border border-gray-200 hover:border-teal-400 transition-colors"
              />
            ) : (
              <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                <Award className="w-5 h-5 text-amber-600" />
              </div>
            )}
            <CheckCircle className="absolute -bottom-1 -right-1 w-4 h-4 text-green-500 bg-white rounded-full" />
          </div>
        ))}
        {badges.length > maxBadges && (
          <span className="text-xs text-gray-500 font-medium">
            +{badges.length - maxBadges} more
          </span>
        )}
        {badges.length === 0 && !userId && showConnectButton && (
          <Button 
            size="sm" 
            variant="outline" 
            onClick={handleConnectCredly}
            disabled={connecting}
            className="text-xs"
          >
            <Award className="w-3 h-3 mr-1" />
            Add Badges
          </Button>
        )}
      </div>
    );
  }

  // Full showcase mode
  return (
    <div className="bg-gradient-to-br from-slate-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-700" data-testid="badge-showcase">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
            <Award className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              Verified Badges
              {badges.length > 0 && (
                <Badge className="bg-green-100 text-green-700 text-xs">
                  <Verified className="w-3 h-3 mr-1" />
                  {badges.length} Verified
                </Badge>
              )}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Professional certifications from trusted issuers
            </p>
          </div>
        </div>
        
        {!userId && showConnectButton && !credlyStatus?.connected && (
          <Button
            size="sm"
            onClick={handleConnectCredly}
            disabled={connecting}
            className="bg-orange-500 hover:bg-orange-600 text-white gap-1"
          >
            <Award className="w-4 h-4" />
            {connecting ? 'Connecting...' : 'Import Badges'}
          </Button>
        )}
      </div>

      {/* Badges Grid */}
      {badges.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {badges.slice(0, maxBadges).map((badge, idx) => (
            <div
              key={badge.id || idx}
              className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 hover:shadow-md hover:border-teal-300 transition-all cursor-pointer group"
              onClick={() => onBadgeClick?.(badge) || window.open(badge.badge_url, '_blank')}
            >
              <div className="flex items-start gap-3">
                {badge.badge_image_url ? (
                  <img 
                    src={badge.badge_image_url} 
                    alt={badge.credential_name}
                    className="w-12 h-12 rounded-lg object-contain bg-gray-50 flex-shrink-0"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center flex-shrink-0">
                    <Award className="w-6 h-6 text-amber-600" />
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <h4 className="font-medium text-sm text-gray-900 dark:text-white truncate">
                    {badge.credential_name}
                  </h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {badge.issuing_authority}
                  </p>
                  <div className="flex items-center gap-1 mt-1">
                    <CheckCircle className="w-3 h-3 text-green-500" />
                    <span className="text-xs text-green-600 dark:text-green-400">Verified</span>
                  </div>
                </div>
              </div>
              
              {/* Skills preview */}
              {badge.skills?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {badge.skills.slice(0, 2).map((skill, i) => (
                    <span key={i} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-600 dark:text-gray-300">
                      {skill}
                    </span>
                  ))}
                </div>
              )}
              
              {/* Hover indicator */}
              <div className="mt-2 flex items-center justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                <ExternalLink className="w-3 h-3 text-gray-400" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-6">
          <Award className="w-10 h-10 mx-auto text-gray-300 mb-2" />
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {userId ? 'No verified badges yet' : 'Showcase your certifications'}
          </p>
          {!userId && showConnectButton && (
            <Button 
              size="sm" 
              variant="outline" 
              onClick={handleConnectCredly}
              disabled={connecting}
            >
              Import from Credly
            </Button>
          )}
        </div>
      )}

      {/* View All Link */}
      {badges.length > maxBadges && (
        <div className="mt-3 text-center">
          <Button variant="ghost" size="sm" className="text-teal-600 hover:text-teal-700">
            View all {badges.length} badges
            <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      )}

      {/* Issuer logos footer */}
      {badges.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-400 mb-2">Verified by:</p>
          <div className="flex items-center gap-2 flex-wrap">
            {[...new Set(badges.map(b => b.issuing_authority))].slice(0, 5).map((issuer, idx) => (
              <span key={idx} className="px-2 py-1 bg-white dark:bg-gray-800 rounded text-xs text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
                {issuer}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileBadgeShowcase;
