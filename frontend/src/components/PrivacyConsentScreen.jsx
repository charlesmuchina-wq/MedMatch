import { useState, useEffect } from "react";
import { Shield, Check, ChevronDown, ChevronUp, ExternalLink, FileText, Mic, Brain, Trash2, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useTranslation } from "@/utils/i18n";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Privacy Consent Screen
 * GDPR/CCPA compliant consent collection for AI features
 */
const PrivacyConsentScreen = ({ onConsentGranted, onSkip, showSkip = false }) => {
  const { t } = useTranslation();
  const [consents, setConsents] = useState({
    resume_processing: false,
    voice_processing: false,
    ai_matching: false,
    marketing_communications: false,
    third_party_sharing: false
  });
  const [expandedSections, setExpandedSections] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const requiredConsents = ["resume_processing", "ai_matching"];
  const allRequiredChecked = requiredConsents.every(key => consents[key]);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleConsentChange = (key, checked) => {
    setConsents(prev => ({
      ...prev,
      [key]: checked
    }));
  };

  const handleSubmit = async () => {
    if (!allRequiredChecked) {
      setError("Please accept the required consents to continue");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/privacy/consent/grant`,
        consents,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Store consent locally
      localStorage.setItem("medmatch-consent-granted", "true");
      
      if (onConsentGranted) {
        onConsentGranted(consents);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to record consent");
    } finally {
      setIsSubmitting(false);
    }
  };

  const privacySections = [
    {
      id: "resume",
      icon: FileText,
      title: "Resume Analysis",
      consentKey: "resume_processing",
      required: true,
      description: "Our AI scans your resume to match your skills with live job postings. We only extract professional data (like certifications and experience) to create your matching score.",
      details: [
        "AI extracts skills, experience, and education",
        "Professional data is used for job matching",
        "Personal identifiers (name, email) are protected",
        "You can delete your resume at any time"
      ]
    },
    {
      id: "voice",
      icon: Mic,
      title: "Voice & Audio",
      consentKey: "voice_processing",
      required: false,
      description: "When you use voice input, we convert your speech to text for searching or translation. We do not store your original audio recordings once the text is processed.",
      details: [
        "Voice is converted to text in real-time",
        "Original audio is NOT stored",
        "Text may be processed by OpenAI Whisper",
        "You can disable voice features anytime"
      ]
    },
    {
      id: "matching",
      icon: Brain,
      title: "AI Matching Logic",
      consentKey: "ai_matching",
      required: true,
      description: "Our algorithms rank you based on job requirements. You can always tap the 'Match Info' icon on any job to see exactly why the AI recommended it to you.",
      details: [
        "Matching based on skills and experience",
        "No demographic data used in ranking",
        "Explainable AI - see why you matched",
        "Request human review of any decision"
      ]
    },
    {
      id: "control",
      icon: Trash2,
      title: "Data Control",
      consentKey: null,
      required: false,
      description: "Your data belongs to you. You can delete your resume, voice history, or entire account at any time via the Settings menu. We never sell your personal information to third parties.",
      details: [
        "One-tap data deletion",
        "Export all your data (GDPR portability)",
        "View audit log of data access",
        "Data never sold to third parties"
      ]
    },
    {
      id: "human",
      icon: Users,
      title: "Human Oversight",
      consentKey: null,
      required: false,
      description: "Our AI is a helper, not a final judge. Recruiters always make the final hiring decisions, and you can request a manual review of any AI-generated match.",
      details: [
        "AI assists, humans decide",
        "Request manual review anytime",
        "Response within 2-3 business days",
        "Appeal any automated decision"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-turquoise/10 mb-4">
            <Shield className="w-8 h-8 text-turquoise" />
          </div>
          <h1 className="text-2xl md:text-3xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            🔒 Your Privacy at MedMatch-AI KARAU AI
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">
            To help you land your next role, MedMatch-AI KARAU AI uses advanced technology to analyze your experience. 
            Here is exactly how we handle your data:
          </p>
        </div>

        {/* Privacy Sections */}
        <div className="space-y-4 mb-8">
          {privacySections.map((section) => (
            <Card key={section.id} className="border-slate-200 dark:border-slate-700">
              <CardHeader 
                className="cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                onClick={() => toggleSection(section.id)}
              >
                <div className="flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-turquoise/10">
                    <section.icon className="w-5 h-5 text-turquoise" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base font-medium text-slate-900 dark:text-slate-100">
                        {section.title}
                        {section.required && (
                          <span className="ml-2 text-xs text-rose-500 font-normal">Required</span>
                        )}
                      </CardTitle>
                      {expandedSections[section.id] ? (
                        <ChevronUp className="w-5 h-5 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                      )}
                    </div>
                    <CardDescription className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      {section.description}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              
              {expandedSections[section.id] && (
                <CardContent className="pt-0">
                  <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-300 ml-12">
                    {section.details.map((detail, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-turquoise flex-shrink-0" />
                        {detail}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              )}
            </Card>
          ))}
        </div>

        {/* Consent Checkboxes */}
        <Card className="mb-6 border-turquoise/30 bg-turquoise/5">
          <CardContent className="p-6">
            <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-4">
              Your Consent
            </h3>
            
            <div className="space-y-4">
              {/* Required: Resume & AI Matching */}
              <label className="flex items-start gap-3 cursor-pointer">
                <Checkbox
                  checked={consents.resume_processing && consents.ai_matching}
                  onCheckedChange={(checked) => {
                    handleConsentChange("resume_processing", checked);
                    handleConsentChange("ai_matching", checked);
                  }}
                  className="mt-0.5"
                  data-testid="consent-required"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  I agree to the processing of my professional data as described above.
                  <span className="text-rose-500 ml-1">*</span>
                </span>
              </label>

              {/* Optional: Voice */}
              <label className="flex items-start gap-3 cursor-pointer">
                <Checkbox
                  checked={consents.voice_processing}
                  onCheckedChange={(checked) => handleConsentChange("voice_processing", checked)}
                  className="mt-0.5"
                  data-testid="consent-voice"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  I agree to voice input processing for search and transcription (optional)
                </span>
              </label>

              {/* Optional: Marketing */}
              <label className="flex items-start gap-3 cursor-pointer">
                <Checkbox
                  checked={consents.marketing_communications}
                  onCheckedChange={(checked) => handleConsentChange("marketing_communications", checked)}
                  className="mt-0.5"
                  data-testid="consent-marketing"
                />
                <span className="text-sm text-slate-700 dark:text-slate-300">
                  I'd like to receive job alerts and career tips via email (optional)
                </span>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 rounded-lg text-rose-700 dark:text-rose-300 text-sm">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex flex-col gap-3">
          <Button
            onClick={handleSubmit}
            disabled={!allRequiredChecked || isSubmitting}
            className="w-full bg-turquoise hover:bg-turquoise/90 text-white py-6 text-lg"
            data-testid="consent-continue-btn"
          >
            {isSubmitting ? "Processing..." : "Continue"}
          </Button>

          {showSkip && (
            <Button
              variant="ghost"
              onClick={onSkip}
              className="text-slate-500"
            >
              Skip for now (limited features)
            </Button>
          )}
        </div>

        {/* Footer Links */}
        <div className="mt-6 text-center text-xs text-slate-400 dark:text-slate-500">
          <p className="mb-2">
            By continuing, you agree to our{" "}
            <a href="/privacy-policy" className="text-turquoise hover:underline">Privacy Policy</a>
            {" "}and{" "}
            <a href="/terms" className="text-turquoise hover:underline">Terms of Service</a>
          </p>
          <p className="flex items-center justify-center gap-1">
            <ExternalLink className="w-3 h-3" />
            <a href="/privacy/sub-processors" className="text-turquoise hover:underline">
              View Third-Party Services
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyConsentScreen;
