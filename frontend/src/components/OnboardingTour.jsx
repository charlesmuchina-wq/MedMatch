import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  X, ChevronRight, ChevronLeft, Search, FileText, Target, 
  Mic, PenTool, BarChart3, Sparkles, CheckCircle2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useTranslation } from "@/utils/i18n";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Onboarding Tour Component
 * Shows a guided tour for first-time users with i18n support
 */
const OnboardingTour = ({ onComplete, user }) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  // Tour steps with translation keys
  const tourSteps = [
    {
      id: "welcome",
      titleKey: "onboarding.welcome",
      descriptionKey: "onboarding.welcomeDesc",
      icon: Sparkles,
      highlight: null,
      actionKey: null
    },
    {
      id: "resume",
      titleKey: "onboarding.uploadResume",
      descriptionKey: "onboarding.uploadResumeDesc",
      icon: FileText,
      highlight: "/resume",
      actionKey: "onboarding.uploadResumeAction"
    },
    {
      id: "search",
      titleKey: "onboarding.smartSearch",
      descriptionKey: "onboarding.smartSearchDesc",
      icon: Search,
      highlight: "/search",
      actionKey: "onboarding.smartSearchAction"
    },
    {
      id: "predictor",
      titleKey: "onboarding.successPredictor",
      descriptionKey: "onboarding.successPredictorDesc",
      icon: Target,
      highlight: "/predictor",
      actionKey: "onboarding.successPredictorAction"
    },
    {
      id: "interview",
      titleKey: "onboarding.interviewPrep",
      descriptionKey: "onboarding.interviewPrepDesc",
      icon: Mic,
      highlight: "/interview",
      actionKey: "onboarding.interviewPrepAction"
    },
    {
      id: "cover-letter",
      titleKey: "onboarding.coverLetter",
      descriptionKey: "onboarding.coverLetterDesc",
      icon: PenTool,
      highlight: "/cover-letter",
      actionKey: "onboarding.coverLetterAction"
    },
    {
      id: "analytics",
      titleKey: "onboarding.analytics",
      descriptionKey: "onboarding.analyticsDesc",
      icon: BarChart3,
      highlight: "/analytics",
      actionKey: "onboarding.analyticsAction"
    },
    {
      id: "complete",
      titleKey: "onboarding.complete",
      descriptionKey: "onboarding.completeDesc",
      icon: CheckCircle2,
      highlight: null,
      actionKey: null
    }
  ];

  const step = tourSteps[currentStep];
  const isLastStep = currentStep === tourSteps.length - 1;
  const isFirstStep = currentStep === 0;

  const handleNext = () => {
    if (isLastStep) {
      handleComplete();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (!isFirstStep) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    localStorage.setItem("medmatch-tour-completed", "true");
    localStorage.setItem("medmatch_tour_completed", "true");
    setIsVisible(false);
    if (onComplete) onComplete();
  };

  const handleNavigate = (path) => {
    if (path) {
      navigate(path);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in" data-testid="onboarding-tour">
      <Card className="w-full max-w-lg mx-4 shadow-2xl border-2 border-turquoise/30">
        <CardContent className="p-0">
          {/* Progress bar */}
          <div className="h-1 bg-slate-200 dark:bg-slate-700">
            <div 
              className="h-full bg-gradient-to-r from-turquoise to-teal-500 transition-all duration-300"
              style={{ width: `${((currentStep + 1) / tourSteps.length) * 100}%` }}
            />
          </div>

          <div className="p-6">
            {/* Header */}
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-turquoise to-teal-600 flex items-center justify-center">
                  <step.icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
                    {t(step.titleKey)}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {t("onboarding.stepOf", { current: currentStep + 1, total: tourSteps.length })}
                  </p>
                </div>
              </div>
              <button 
                onClick={handleSkip}
                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                aria-label={t("onboarding.skip")}
                data-testid="onboarding-skip"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <p className="text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
              {t(step.descriptionKey)}
            </p>

            {step.actionKey && (
              <div className="bg-turquoise/10 dark:bg-turquoise/20 rounded-lg p-3 mb-6">
                <p className="text-sm text-turquoise dark:text-turquoise font-medium flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  {t(step.actionKey)}
                </p>
              </div>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
              <Button
                variant="ghost"
                onClick={handlePrev}
                disabled={isFirstStep}
                className="text-slate-500"
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                {t("common.back")}
              </Button>

              <div className="flex items-center gap-2">
                {tourSteps.map((_, idx) => (
                  <div
                    key={idx}
                    className={`w-2 h-2 rounded-full transition-colors ${
                      idx === currentStep 
                        ? 'bg-turquoise' 
                        : idx < currentStep 
                          ? 'bg-turquoise/50' 
                          : 'bg-slate-300 dark:bg-slate-600'
                    }`}
                  />
                ))}
              </div>

              <Button
                onClick={handleNext}
                className="bg-gradient-to-r from-turquoise to-teal-600"
                data-testid="onboarding-next"
              >
                {isLastStep ? t("onboarding.getStarted") : t("common.next")}
                {!isLastStep && <ChevronRight className="w-4 h-4 ml-1" />}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

/**
 * Hook to check if user should see the onboarding tour
 */
export const useOnboardingTour = () => {
  // Check localStorage synchronously during initialization
  const [showTour, setShowTour] = useState(() => {
    // Never show initially - we'll set it via useEffect only if needed
    return false;
  });
  
  // Track if we've already checked (to prevent re-showing on re-renders)
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    // Only check once per session
    if (hasChecked) return;
    
    // Check localStorage value
    const tourCompleted = localStorage.getItem("medmatch-tour-completed") === "true";
    
    // Mark as checked
    setHasChecked(true);
    
    // Only show tour if not completed
    if (!tourCompleted) {
      const timer = setTimeout(() => setShowTour(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [hasChecked]);

  const completeTour = () => {
    localStorage.setItem("medmatch-tour-completed", "true");
    localStorage.setItem("medmatch_tour_completed", "true");
    setShowTour(false);
  };

  const resetTour = () => {
    localStorage.removeItem("medmatch-tour-completed");
    setHasChecked(false);
    setShowTour(true);
  };

  return { showTour, completeTour, resetTour };
};

/**
 * Welcome Tooltip - Shows a quick tip on first visit to a page
 */
export const WelcomeTooltip = ({ feature, children, position = "bottom" }) => {
  const [dismissed, setDismissed] = useState(false);
  const storageKey = `medmatch-tooltip-${feature}`;

  useEffect(() => {
    const seen = localStorage.getItem(storageKey);
    if (seen) setDismissed(true);
  }, [storageKey]);

  const handleDismiss = () => {
    localStorage.setItem(storageKey, "true");
    setDismissed(true);
  };

  if (dismissed) return null;

  const positionClasses = {
    top: "bottom-full mb-2",
    bottom: "top-full mt-2",
    left: "right-full mr-2",
    right: "left-full ml-2"
  };

  return (
    <div className="relative inline-block">
      <div className={`absolute ${positionClasses[position]} z-50 w-64`}>
        <div className="bg-slate-900 dark:bg-slate-800 text-white p-3 rounded-lg shadow-lg text-sm">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-turquoise flex-shrink-0" />
              <span>{children}</span>
            </div>
            <button onClick={handleDismiss} className="text-slate-400 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className={`absolute w-3 h-3 bg-slate-900 dark:bg-slate-800 transform rotate-45 ${
            position === 'bottom' ? '-top-1.5 left-1/2 -translate-x-1/2' :
            position === 'top' ? '-bottom-1.5 left-1/2 -translate-x-1/2' :
            position === 'left' ? '-right-1.5 top-1/2 -translate-y-1/2' :
            '-left-1.5 top-1/2 -translate-y-1/2'
          }`} />
        </div>
      </div>
    </div>
  );
};

export default OnboardingTour;
