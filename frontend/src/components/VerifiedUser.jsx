import { useState, useEffect, createContext, useContext } from "react";
import { useTranslation } from "@/utils/i18n";
import { ShieldCheck, Award, BadgeCheck, Star, Crown, Verified } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

// Verification Levels
export const VERIFICATION_LEVELS = {
  NONE: { level: 0, name: "Unverified", color: "bg-slate-200 text-slate-600" },
  EMAIL: { level: 1, name: "Email Verified", color: "bg-blue-100 text-blue-700", icon: BadgeCheck },
  PHONE: { level: 2, name: "Phone Verified", color: "bg-green-100 text-green-700", icon: ShieldCheck },
  BIOMETRIC: { level: 3, name: "Biometric Verified", color: "bg-turquoise/20 text-turquoise", icon: Verified },
  ID_VERIFIED: { level: 4, name: "ID Verified", color: "bg-purple-100 text-purple-700", icon: Award },
  PREMIUM: { level: 5, name: "Premium Verified", color: "bg-amber-100 text-amber-700", icon: Crown },
};

// Context for verification status
const VerificationContext = createContext();

export const useVerification = () => {
  const context = useContext(VerificationContext);
  if (!context) {
    return { 
      verificationLevel: VERIFICATION_LEVELS.NONE,
      isVerified: false,
      badges: []
    };
  }
  return context;
};

export const VerificationProvider = ({ children, user }) => {
  const [verificationLevel, setVerificationLevel] = useState(VERIFICATION_LEVELS.NONE);
  const [badges, setBadges] = useState([]);

  useEffect(() => {
    if (!user) {
      setVerificationLevel(VERIFICATION_LEVELS.NONE);
      setBadges([]);
      return;
    }

    // Calculate verification level based on user data
    const userBadges = [];
    let highestLevel = VERIFICATION_LEVELS.NONE;

    if (user.email_verified || user.email) {
      userBadges.push(VERIFICATION_LEVELS.EMAIL);
      highestLevel = VERIFICATION_LEVELS.EMAIL;
    }

    if (user.phone_verified) {
      userBadges.push(VERIFICATION_LEVELS.PHONE);
      highestLevel = VERIFICATION_LEVELS.PHONE;
    }

    if (user.is_biometric_verified) {
      userBadges.push(VERIFICATION_LEVELS.BIOMETRIC);
      highestLevel = VERIFICATION_LEVELS.BIOMETRIC;
    }

    if (user.id_verified) {
      userBadges.push(VERIFICATION_LEVELS.ID_VERIFIED);
      highestLevel = VERIFICATION_LEVELS.ID_VERIFIED;
    }

    if (user.membership_status === "premium" || user.membership_status === "active") {
      userBadges.push(VERIFICATION_LEVELS.PREMIUM);
      highestLevel = VERIFICATION_LEVELS.PREMIUM;
    }

    setVerificationLevel(highestLevel);
    setBadges(userBadges);
  }, [user]);

  return (
    <VerificationContext.Provider value={{ 
      verificationLevel, 
      isVerified: verificationLevel.level >= VERIFICATION_LEVELS.BIOMETRIC.level,
      badges
    }}>
      {children}
    </VerificationContext.Provider>
  );
};

// Verified User Badge Component
export const VerifiedBadge = ({ user, size = "sm", showTooltip = true }) => {
  if (!user) return null;

  const getVerificationInfo = () => {
    if (user.membership_status === "premium" || user.membership_status === "active") {
      return { ...VERIFICATION_LEVELS.PREMIUM, show: true };
    }
    if (user.id_verified) {
      return { ...VERIFICATION_LEVELS.ID_VERIFIED, show: true };
    }
    if (user.is_biometric_verified) {
      return { ...VERIFICATION_LEVELS.BIOMETRIC, show: true };
    }
    if (user.phone_verified) {
      return { ...VERIFICATION_LEVELS.PHONE, show: true };
    }
    if (user.email_verified || user.email) {
      return { ...VERIFICATION_LEVELS.EMAIL, show: true };
    }
    return { ...VERIFICATION_LEVELS.NONE, show: false };
  };

  const info = getVerificationInfo();
  if (!info.show) return null;

  const Icon = info.icon || BadgeCheck;
  const sizeClasses = {
    xs: "w-3 h-3",
    sm: "w-4 h-4",
    md: "w-5 h-5",
    lg: "w-6 h-6"
  };

  const badge = (
    <Badge className={`${info.color} gap-1 font-medium`} data-testid="verified-badge">
      <Icon className={sizeClasses[size]} />
      {size !== "xs" && <span>{info.name}</span>}
    </Badge>
  );

  if (!showTooltip) return badge;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{badge}</TooltipTrigger>
        <TooltipContent>
          <p className="font-medium">{info.name}</p>
          <p className="text-xs text-slate-400">
            {info.level >= 3 ? "Identity verified - trusted user" : "Basic verification"}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// Verification Trust Score Component
export const TrustScore = ({ user }) => {
  if (!user) return null;

  const calculateScore = () => {
    let score = 0;
    if (user.email_verified || user.email) score += 20;
    if (user.phone_verified) score += 20;
    if (user.is_biometric_verified) score += 30;
    if (user.id_verified) score += 20;
    if (user.membership_status === "premium") score += 10;
    return Math.min(score, 100);
  };

  const score = calculateScore();
  const getScoreColor = () => {
    if (score >= 80) return "text-emerald-500";
    if (score >= 50) return "text-amber-500";
    return "text-slate-400";
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1">
        <Star className={`w-4 h-4 ${getScoreColor()}`} />
        <span className={`font-semibold ${getScoreColor()}`}>{score}%</span>
      </div>
      <span className="text-xs text-slate-500">Trust Score</span>
    </div>
  );
};

// Verification Steps Progress Component
export const VerificationProgress = ({ user, onStartVerification }) => {
  const steps = [
    { key: "email", label: "Email", done: user?.email_verified || !!user?.email },
    { key: "phone", label: "Phone", done: user?.phone_verified },
    { key: "biometric", label: "Biometric", done: user?.is_biometric_verified },
    { key: "id", label: "ID Document", done: user?.id_verified },
  ];

  const completedSteps = steps.filter(s => s.done).length;
  const progress = (completedSteps / steps.length) * 100;

  return (
    <div className="space-y-3">
      <div className="flex justify-between text-sm">
        <span className="text-slate-600 dark:text-slate-400">Verification Progress</span>
        <span className="font-medium">{completedSteps}/{steps.length}</span>
      </div>
      
      <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-turquoise to-emerald-500 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="grid grid-cols-4 gap-2">
        {steps.map((step) => (
          <div 
            key={step.key}
            className={`text-center p-2 rounded-lg text-xs ${
              step.done 
                ? "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400" 
                : "bg-slate-100 dark:bg-slate-800 text-slate-500"
            }`}
          >
            {step.done ? "✓" : "○"} {step.label}
          </div>
        ))}
      </div>

      {completedSteps < steps.length && onStartVerification && (
        <button
          onClick={onStartVerification}
          className="w-full text-sm text-turquoise hover:underline"
        >
          Complete verification to unlock benefits →
        </button>
      )}
    </div>
  );
};

// Applicant Card with Verification Badge (for Recruiters)
export const ApplicantVerificationBadge = ({ applicant }) => {
  if (!applicant?.is_biometric_verified) return null;

  return (
    <div className="inline-flex items-center gap-1 px-2 py-1 bg-turquoise/10 rounded-full">
      <Verified className="w-4 h-4 text-turquoise" />
      <span className="text-xs font-medium text-turquoise">Verified Applicant</span>
    </div>
  );
};

export default {
  VerifiedBadge,
  TrustScore,
  VerificationProgress,
  ApplicantVerificationBadge,
  VerificationProvider,
  useVerification,
  VERIFICATION_LEVELS
};
