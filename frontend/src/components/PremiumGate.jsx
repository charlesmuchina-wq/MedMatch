import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Crown, Lock, Sparkles, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Premium Feature Gate Component
 * Wraps premium features and shows upgrade prompt if user doesn't have access
 */
const PremiumGate = ({ 
  feature = "premium", 
  children, 
  fallback = null,
  showUpgradePrompt = true 
}) => {
  const navigate = useNavigate();
  const [hasAccess, setHasAccess] = useState(null);
  const [membershipInfo, setMembershipInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAccess();
  }, [feature]);

  const checkAccess = async () => {
    try {
      const response = await axios.get(`${API}/api/membership/check-access/${feature}`, {
        withCredentials: true
      });
      setHasAccess(response.data.has_access);
      setMembershipInfo(response.data);
    } catch (e) {
      // If not authenticated, treat as no access
      setHasAccess(false);
      setMembershipInfo({ reason: "Please log in to access this feature" });
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-turquoise"></div>
      </div>
    );
  }

  if (hasAccess) {
    return children;
  }

  if (!showUpgradePrompt && fallback) {
    return fallback;
  }

  // Show upgrade prompt
  return (
    <Card className="max-w-md mx-auto my-8">
      <CardContent className="p-8 text-center">
        <div className="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Lock className="w-8 h-8 text-white" />
        </div>
        
        <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2" style={{ fontFamily: 'IBM Plex Sans' }}>
          Premium Feature
        </h3>
        
        <p className="text-slate-500 dark:text-slate-400 mb-6">
          {membershipInfo?.reason || "Upgrade to access this feature"}
        </p>

        {membershipInfo?.membership_status === 'trial' && (
          <p className="text-sm text-amber-600 dark:text-amber-400 mb-4">
            {membershipInfo.days_remaining} days left in your trial
          </p>
        )}

        <div className="space-y-3">
          <Button 
            onClick={() => navigate('/membership')}
            className="w-full bg-gradient-to-r from-turquoise to-teal-600"
          >
            <Crown className="w-4 h-4 mr-2" /> Upgrade for $1
          </Button>
          
          {membershipInfo?.membership_status === 'expired' && (
            <p className="text-xs text-slate-500">
              One-time payment • Lifetime access
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * Hook to check feature access
 */
export const useFeatureAccess = (feature) => {
  const [access, setAccess] = useState({ loading: true, hasAccess: false, info: null });

  useEffect(() => {
    const checkAccess = async () => {
      try {
        const response = await axios.get(`${API}/api/membership/check-access/${feature}`, {
          withCredentials: true
        });
        setAccess({
          loading: false,
          hasAccess: response.data.has_access,
          info: response.data
        });
      } catch (e) {
        setAccess({
          loading: false,
          hasAccess: false,
          info: { reason: "Please log in" }
        });
      }
    };
    checkAccess();
  }, [feature]);

  return access;
};

/**
 * Upgrade Banner Component
 * Shows at top of pages for trial/expired users
 */
export const UpgradeBanner = ({ membership }) => {
  const navigate = useNavigate();

  if (!membership || membership.membership_status === 'active' || membership.role === 'recruiter') {
    return null;
  }

  const isExpired = membership.membership_status === 'expired';
  const daysRemaining = membership.days_remaining;

  return (
    <div className={`px-4 py-3 flex items-center justify-between flex-wrap gap-2 ${
      isExpired 
        ? 'bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800'
        : 'bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800'
    }`}>
      <div className="flex items-center gap-2">
        <Sparkles className={`w-4 h-4 ${isExpired ? 'text-red-500' : 'text-amber-500'}`} />
        <span className={`text-sm ${isExpired ? 'text-red-700 dark:text-red-300' : 'text-amber-700 dark:text-amber-300'}`}>
          {isExpired 
            ? "Your trial has expired. Upgrade to continue using MedMatch."
            : `${daysRemaining} days left in your free trial.`
          }
        </span>
      </div>
      <Button 
        size="sm" 
        onClick={() => navigate('/membership')}
        className={isExpired 
          ? 'bg-red-500 hover:bg-red-600 text-white'
          : 'bg-amber-500 hover:bg-amber-600 text-white'
        }
      >
        Upgrade for $1 <ArrowRight className="w-3 h-3 ml-1" />
      </Button>
    </div>
  );
};

export default PremiumGate;
