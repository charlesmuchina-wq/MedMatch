/**
 * Interactive Language Tour Component
 * Guides new users through the app in their selected language
 * with contextual tooltips and highlights
 */
import React, { useState, useEffect, useCallback } from 'react';
import { X, ChevronRight, ChevronLeft, Globe, Sparkles, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { useTranslation } from '@/utils/i18n';

// Tour steps configuration
const TOUR_STEPS = [
  {
    id: 'welcome',
    target: null,
    titleKey: 'tour.welcome.title',
    descriptionKey: 'tour.welcome.description',
    position: 'center',
    highlight: false
  },
  {
    id: 'language',
    target: '[data-testid="language-selector"]',
    titleKey: 'tour.language.title',
    descriptionKey: 'tour.language.description',
    position: 'bottom',
    highlight: true
  },
  {
    id: 'dashboard',
    target: '[data-testid="nav-dashboard"]',
    titleKey: 'tour.dashboard.title',
    descriptionKey: 'tour.dashboard.description',
    position: 'right',
    highlight: true
  },
  {
    id: 'jobs',
    target: '[data-testid="nav-jobs"]',
    titleKey: 'tour.jobs.title',
    descriptionKey: 'tour.jobs.description',
    position: 'right',
    highlight: true
  },
  {
    id: 'dragon',
    target: '[data-testid="dragon-ai-button"]',
    titleKey: 'tour.dragon.title',
    descriptionKey: 'tour.dragon.description',
    position: 'left',
    highlight: true
  },
  {
    id: 'complete',
    target: null,
    titleKey: 'tour.complete.title',
    descriptionKey: 'tour.complete.description',
    position: 'center',
    highlight: false
  }
];

// Default tour translations (fallback)
const TOUR_TRANSLATIONS = {
  en: {
    'tour.welcome.title': 'Welcome to MedMatch-AI KARAU!',
    'tour.welcome.description': 'Let us guide you through the key features of your AI-powered career platform.',
    'tour.language.title': 'Choose Your Language',
    'tour.language.description': 'MedMatch-AI KARAU supports 33+ languages. Click here to switch anytime.',
    'tour.dashboard.title': 'Your Dashboard',
    'tour.dashboard.description': 'See your job matches, applications, and career insights at a glance.',
    'tour.jobs.title': 'Smart Job Search',
    'tour.jobs.description': 'Search 15+ job boards simultaneously. Get Trust Scores for every match.',
    'tour.dragon.title': 'Meet KARAU Dragon AI',
    'tour.dragon.description': 'Your AI assistant that helps with everything from job search to interview prep.',
    'tour.complete.title': 'You\'re All Set!',
    'tour.complete.description': 'Explore MedMatch-AI KARAU and accelerate your career. Good luck!',
    'tour.skip': 'Skip Tour',
    'tour.next': 'Next',
    'tour.prev': 'Back',
    'tour.finish': 'Get Started',
    'tour.step': 'Step'
  },
  de: {
    'tour.welcome.title': 'Willkommen bei MedMatch-AI KARAU!',
    'tour.welcome.description': 'Lassen Sie uns Sie durch die wichtigsten Funktionen Ihrer KI-gestützten Karriereplattform führen.',
    'tour.language.title': 'Wählen Sie Ihre Sprache',
    'tour.language.description': 'MedMatch-AI KARAU unterstützt 33+ Sprachen. Klicken Sie hier, um jederzeit zu wechseln.',
    'tour.dashboard.title': 'Ihr Dashboard',
    'tour.dashboard.description': 'Sehen Sie Ihre Job-Matches, Bewerbungen und Karriere-Einblicke auf einen Blick.',
    'tour.jobs.title': 'Intelligente Jobsuche',
    'tour.jobs.description': 'Durchsuchen Sie 15+ Jobbörsen gleichzeitig. Erhalten Sie Vertrauenswerte für jeden Match.',
    'tour.dragon.title': 'Lernen Sie KARAU Dragon AI kennen',
    'tour.dragon.description': 'Ihr KI-Assistent, der bei allem hilft - von der Jobsuche bis zur Interviewvorbereitung.',
    'tour.complete.title': 'Alles bereit!',
    'tour.complete.description': 'Erkunden Sie MedMatch-AI KARAU und beschleunigen Sie Ihre Karriere. Viel Erfolg!',
    'tour.skip': 'Tour überspringen',
    'tour.next': 'Weiter',
    'tour.prev': 'Zurück',
    'tour.finish': 'Loslegen',
    'tour.step': 'Schritt'
  },
  fr: {
    'tour.welcome.title': 'Bienvenue sur MedMatch-AI KARAU !',
    'tour.welcome.description': 'Laissez-nous vous guider à travers les fonctionnalités clés de votre plateforme carrière alimentée par l\'IA.',
    'tour.language.title': 'Choisissez votre langue',
    'tour.language.description': 'MedMatch-AI KARAU prend en charge plus de 33 langues. Cliquez ici pour changer à tout moment.',
    'tour.dashboard.title': 'Votre tableau de bord',
    'tour.dashboard.description': 'Voyez vos correspondances d\'emploi, candidatures et aperçus de carrière en un coup d\'œil.',
    'tour.jobs.title': 'Recherche d\'emploi intelligente',
    'tour.jobs.description': 'Recherchez sur plus de 15 sites d\'emploi simultanément. Obtenez des scores de confiance pour chaque correspondance.',
    'tour.dragon.title': 'Découvrez KARAU Dragon AI',
    'tour.dragon.description': 'Votre assistant IA qui vous aide pour tout, de la recherche d\'emploi à la préparation aux entretiens.',
    'tour.complete.title': 'Vous êtes prêt !',
    'tour.complete.description': 'Explorez MedMatch-AI KARAU et accélérez votre carrière. Bonne chance !',
    'tour.skip': 'Passer la visite',
    'tour.next': 'Suivant',
    'tour.prev': 'Précédent',
    'tour.finish': 'Commencer',
    'tour.step': 'Étape'
  },
  es: {
    'tour.welcome.title': '¡Bienvenido a MedMatch-AI KARAU!',
    'tour.welcome.description': 'Permítanos guiarlo a través de las características clave de su plataforma de carrera impulsada por IA.',
    'tour.language.title': 'Elija su idioma',
    'tour.language.description': 'MedMatch-AI KARAU admite más de 33 idiomas. Haga clic aquí para cambiar en cualquier momento.',
    'tour.dashboard.title': 'Su panel de control',
    'tour.dashboard.description': 'Vea sus coincidencias de empleo, solicitudes e información de carrera de un vistazo.',
    'tour.jobs.title': 'Búsqueda de empleo inteligente',
    'tour.jobs.description': 'Busque en más de 15 bolsas de trabajo simultáneamente. Obtenga puntuaciones de confianza para cada coincidencia.',
    'tour.dragon.title': 'Conozca a KARAU Dragon AI',
    'tour.dragon.description': 'Su asistente de IA que ayuda con todo, desde la búsqueda de empleo hasta la preparación de entrevistas.',
    'tour.complete.title': '¡Todo listo!',
    'tour.complete.description': 'Explore MedMatch-AI KARAU y acelere su carrera. ¡Buena suerte!',
    'tour.skip': 'Saltar tour',
    'tour.next': 'Siguiente',
    'tour.prev': 'Anterior',
    'tour.finish': 'Comenzar',
    'tour.step': 'Paso'
  }
};

const LanguageTour = ({ isOpen, onClose, language = 'en' }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState(null);
  const { t } = useTranslation();

  // Get translation with fallback
  const getTourText = useCallback((key) => {
    // Try main translations first
    const translated = t(key);
    if (translated !== key) return translated;
    
    // Fallback to tour-specific translations
    const fallbackLang = TOUR_TRANSLATIONS[language] ? language : 'en';
    return TOUR_TRANSLATIONS[fallbackLang][key] || TOUR_TRANSLATIONS.en[key] || key;
  }, [t, language]);

  const step = TOUR_STEPS[currentStep];
  const progress = ((currentStep + 1) / TOUR_STEPS.length) * 100;

  // Update target element position
  useEffect(() => {
    if (!isOpen || !step?.target) {
      setTargetRect(null);
      return;
    }

    const updatePosition = () => {
      const element = document.querySelector(step.target);
      if (element) {
        const rect = element.getBoundingClientRect();
        setTargetRect(rect);
      } else {
        setTargetRect(null);
      }
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
    };
  }, [isOpen, currentStep, step]);

  const handleNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    localStorage.setItem('medmatch_tour_completed', 'true');
    onClose();
  };

  const handleSkip = () => {
    localStorage.setItem('medmatch_tour_skipped', 'true');
    onClose();
  };

  if (!isOpen) return null;

  // Calculate tooltip position
  const getTooltipStyle = () => {
    if (!targetRect || step.position === 'center') {
      return {
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 10001
      };
    }

    const padding = 16;
    let style = {
      position: 'fixed',
      zIndex: 10001,
      maxWidth: '400px'
    };

    switch (step.position) {
      case 'right':
        style.left = `${targetRect.right + padding}px`;
        style.top = `${targetRect.top}px`;
        break;
      case 'left':
        style.right = `${window.innerWidth - targetRect.left + padding}px`;
        style.top = `${targetRect.top}px`;
        break;
      case 'bottom':
        style.left = `${targetRect.left}px`;
        style.top = `${targetRect.bottom + padding}px`;
        break;
      case 'top':
        style.left = `${targetRect.left}px`;
        style.bottom = `${window.innerHeight - targetRect.top + padding}px`;
        break;
      default:
        style.left = `${targetRect.left}px`;
        style.top = `${targetRect.bottom + padding}px`;
    }

    return style;
  };

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black/60 z-[10000]"
        onClick={handleSkip}
      />

      {/* Spotlight on target element */}
      {targetRect && step.highlight && (
        <div
          className="fixed z-[10000] ring-4 ring-turquoise ring-offset-4 rounded-lg transition-all duration-300"
          style={{
            left: `${targetRect.left - 4}px`,
            top: `${targetRect.top - 4}px`,
            width: `${targetRect.width + 8}px`,
            height: `${targetRect.height + 8}px`,
            boxShadow: '0 0 0 9999px rgba(0,0,0,0.6)'
          }}
        />
      )}

      {/* Tooltip Card */}
      <Card 
        className="shadow-2xl border-2 border-turquoise/30 bg-white dark:bg-gray-900"
        style={getTooltipStyle()}
        data-testid="language-tour-tooltip"
      >
        <CardContent className="p-5">
          {/* Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-turquoise/10">
                <Sparkles className="w-4 h-4 text-turquoise" />
              </div>
              <Badge variant="outline" className="text-xs">
                {getTourText('tour.step')} {currentStep + 1}/{TOUR_STEPS.length}
              </Badge>
            </div>
            <Button variant="ghost" size="sm" onClick={handleSkip} className="h-8 w-8 p-0">
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Progress */}
          <Progress value={progress} className="h-1 mb-4" />

          {/* Content */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
              {step.id === 'complete' && <CheckCircle className="w-5 h-5 text-green-500" />}
              {step.id === 'language' && <Globe className="w-5 h-5 text-turquoise" />}
              {getTourText(step.titleKey)}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
              {getTourText(step.descriptionKey)}
            </p>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-5 pt-4 border-t border-gray-100 dark:border-gray-800">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSkip}
              className="text-gray-500 hover:text-gray-700"
            >
              {getTourText('tour.skip')}
            </Button>
            
            <div className="flex items-center gap-2">
              {currentStep > 0 && (
                <Button variant="outline" size="sm" onClick={handlePrev}>
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  {getTourText('tour.prev')}
                </Button>
              )}
              <Button 
                onClick={handleNext}
                className="bg-turquoise hover:bg-turquoise/90"
                size="sm"
              >
                {currentStep === TOUR_STEPS.length - 1 
                  ? getTourText('tour.finish')
                  : getTourText('tour.next')
                }
                {currentStep < TOUR_STEPS.length - 1 && <ChevronRight className="w-4 h-4 ml-1" />}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  );
};

export default LanguageTour;
