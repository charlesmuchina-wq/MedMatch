import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  X, ChevronRight, ChevronLeft, Search, FileText, Target, 
  Mic, PenTool, BarChart3, Sparkles, CheckCircle2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const API = process.env.REACT_APP_BACKEND_URL;

const tourSteps = [
  {
    id: "welcome",
    title: "Welcome to MedMatch! 🎉",
    description: "Your AI-powered job search companion. Let's take a quick tour of the key features.",
    icon: Sparkles,
    highlight: null,
    action: null
  },
  {
    id: "resume",
    title: "Upload Your Resume",
    description: "Start by uploading your resume. Our AI will parse it and use it to find matching jobs and generate personalized content.",
    icon: FileText,
    highlight: "/resume",
    action: "Try it: Click 'My Resume' in the sidebar"
  },
  {
    id: "search",
    title: "Smart Job Search",
    description: "Search across multiple job boards simultaneously. We aggregate results from Indeed, LinkedIn, Glassdoor, and more.",
    icon: Search,
    highlight: "/search",
    action: "Try it: Search for jobs that match your skills"
  },
  {
    id: "predictor",
    title: "Success Predictor",
    description: "Get AI-powered predictions on your callback probability before applying. Know which jobs are worth your time.",
    icon: Target,
    highlight: "/predictor",
    action: "Try it: Analyze any job to see your match score"
  },
  {
    id: "interview",
    title: "Interview Preparation",
    description: "Generate tailored interview questions and practice with our AI voice coach. Export questions as PDF.",
    icon: Mic,
    highlight: "/interview",
    action: "Try it: Get questions for your target role"
  },
  {
    id: "cover-letter",
    title: "AI Cover Letters",
    description: "Generate personalized cover letters in seconds. Our AI analyzes the job description and highlights your relevant experience.",
    icon: PenTool,
    highlight: "/cover-letter",
    action: "Try it: Create a cover letter for any job"
  },
  {
    id: "analytics",
    title: "Track Your Progress",
    description: "Monitor your job search with detailed analytics. See application trends, response rates, and more.",
    icon: BarChart3,
    highlight: "/analytics",
    action: "Try it: View your job search dashboard"
  },
  {
    id: "complete",
    title: "You're All Set!",
    description: "Start your job search journey. Remember, you have a 15-day free trial to explore all features!",
    icon: CheckCircle2,
    highlight: null,
    action: null
  }
];

/**
 * Onboarding Tour Component
 * Shows a guided tour for first-time users
 */
const OnboardingTour = ({ onComplete, user }) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

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
    // Mark tour as completed in localStorage
    localStorage.setItem("medmatch-tour-completed", "true");
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
                    {step.title}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Step {currentStep + 1} of {tourSteps.length}
                  </p>
                </div>
              </div>
              <button 
                onClick={handleSkip}
                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                aria-label="Skip tour"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <p className="text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
              {step.description}
            </p>

            {step.action && (
              <div className="bg-turquoise/10 dark:bg-turquoise/20 rounded-lg p-3 mb-6">
                <p className="text-sm text-turquoise dark:text-turquoise font-medium flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  {step.action}
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
                Back
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
              >
                {isLastStep ? "Get Started" : "Next"}
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
  const [showTour, setShowTour] = useState(false);

  useEffect(() => {
    const tourCompleted = localStorage.getItem("medmatch-tour-completed");
    if (!tourCompleted) {
      // Small delay to let the app render first
      const timer = setTimeout(() => setShowTour(true), 1000);
      return () => clearTimeout(timer);
    }
  }, []);

  const completeTour = () => {
    localStorage.setItem("medmatch-tour-completed", "true");
    setShowTour(false);
  };

  const resetTour = () => {
    localStorage.removeItem("medmatch-tour-completed");
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
