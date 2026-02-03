import { useState } from "react";
import { 
  Shield, Building2, Mail, Phone, CheckCircle2, 
  AlertCircle, Linkedin, Globe, Users, Lock, ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useTranslation } from "@/utils/i18n";
import { toast } from "sonner";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Recruiter Registration & Verification Page
 * Business verification flow for recruiters
 */
const RecruiterVerificationPage = () => {
  const { t } = useTranslation();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    company_name: "",
    company_website: "",
    company_linkedin: "",
    business_email: "",
    job_title: "",
    department: "Human Resources",
    phone_number: "",
    company_address: "",
    company_size: "",
    healthcare_sector: "",
    linkedin_profile: ""
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleRegister = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/recruiter-rbac/register`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("Registration submitted!");
      setStep(2);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVerificationRequest = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/recruiter-rbac/verify/request`,
        {
          linkedin_profile: formData.linkedin_profile,
          verification_documents: [],
          additional_notes: ""
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("Verification request submitted!");
      setStep(3);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Verification request failed");
    } finally {
      setLoading(false);
    }
  };

  const handleEnableMFA = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/recruiter-rbac/mfa/enable`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("MFA enabled successfully!");
      setStep(4);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to enable MFA");
    } finally {
      setLoading(false);
    }
  };

  const companySizes = ["1-50", "51-200", "201-500", "500+"];
  const healthcareSectors = [
    "Hospital",
    "Clinic",
    "Home Care",
    "Nursing Home",
    "Medical Device",
    "Pharmaceutical",
    "Telehealth",
    "Other"
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6" data-testid="recruiter-verification-page">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-turquoise/10 mb-4">
            <Shield className="w-8 h-8 text-turquoise" />
          </div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Recruiter Verification
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">
            Complete verification to access candidate profiles and job posting features
          </p>
        </div>

        {/* Progress */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {["Business Info", "LinkedIn Verify", "Enable MFA", "Complete"].map((label, i) => (
              <div key={i} className={`text-xs font-medium ${step > i ? "text-turquoise" : "text-slate-400"}`}>
                {label}
              </div>
            ))}
          </div>
          <Progress value={(step / 4) * 100} className="h-2" />
        </div>

        {/* Step 1: Business Registration */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="w-5 h-5 text-turquoise" />
                Business Information
              </CardTitle>
              <CardDescription>
                Provide your company details for verification
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="text-sm font-medium">Company Name *</label>
                  <Input
                    placeholder="e.g., City Medical Center"
                    value={formData.company_name}
                    onChange={(e) => handleChange("company_name", e.target.value)}
                    data-testid="company-name-input"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Company Website</label>
                  <Input
                    placeholder="https://example.com"
                    value={formData.company_website}
                    onChange={(e) => handleChange("company_website", e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">LinkedIn Company Page</label>
                  <Input
                    placeholder="https://linkedin.com/company/..."
                    value={formData.company_linkedin}
                    onChange={(e) => handleChange("company_linkedin", e.target.value)}
                  />
                </div>

                <div className="col-span-2">
                  <label className="text-sm font-medium">Business Email *</label>
                  <Input
                    type="email"
                    placeholder="you@yourcompany.com"
                    value={formData.business_email}
                    onChange={(e) => handleChange("business_email", e.target.value)}
                    data-testid="business-email-input"
                  />
                  <p className="text-xs text-slate-400 mt-1">
                    Must match your company domain (no personal emails)
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium">Your Job Title *</label>
                  <Input
                    placeholder="e.g., HR Manager"
                    value={formData.job_title}
                    onChange={(e) => handleChange("job_title", e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Phone Number *</label>
                  <Input
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    value={formData.phone_number}
                    onChange={(e) => handleChange("phone_number", e.target.value)}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Company Size</label>
                  <select
                    className="w-full p-2 border rounded-lg"
                    value={formData.company_size}
                    onChange={(e) => handleChange("company_size", e.target.value)}
                  >
                    <option value="">Select...</option>
                    {companySizes.map((size) => (
                      <option key={size} value={size}>{size} employees</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium">Healthcare Sector</label>
                  <select
                    className="w-full p-2 border rounded-lg"
                    value={formData.healthcare_sector}
                    onChange={(e) => handleChange("healthcare_sector", e.target.value)}
                  >
                    <option value="">Select...</option>
                    {healthcareSectors.map((sector) => (
                      <option key={sector} value={sector}>{sector}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-amber-500 mt-0.5" />
                  <div className="text-sm text-amber-800 dark:text-amber-200">
                    <strong>Why verification?</strong>
                    <p className="mt-1">
                      We verify all recruiters to protect job seekers from unauthorized data access 
                      and ensure GDPR compliance.
                    </p>
                  </div>
                </div>
              </div>

              <Button
                onClick={handleRegister}
                disabled={loading || !formData.company_name || !formData.business_email || !formData.job_title}
                className="w-full bg-turquoise hover:bg-turquoise/90"
                data-testid="register-recruiter-btn"
              >
                {loading ? "Registering..." : "Continue"}
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 2: LinkedIn Verification */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Linkedin className="w-5 h-5 text-blue-600" />
                LinkedIn Verification
              </CardTitle>
              <CardDescription>
                Verify your professional identity with LinkedIn
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Your LinkedIn Profile URL *</label>
                <Input
                  placeholder="https://linkedin.com/in/yourprofile"
                  value={formData.linkedin_profile}
                  onChange={(e) => handleChange("linkedin_profile", e.target.value)}
                  data-testid="linkedin-profile-input"
                />
                <p className="text-xs text-slate-400 mt-1">
                  We'll verify your profile matches your company
                </p>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                  What we check:
                </h4>
                <ul className="space-y-2 text-sm text-blue-700 dark:text-blue-300">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Profile shows current employment at your company
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Job title matches HR/recruiting function
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Company page is legitimate healthcare organization
                  </li>
                </ul>
              </div>

              <Button
                onClick={handleVerificationRequest}
                disabled={loading || !formData.linkedin_profile}
                className="w-full bg-blue-600 hover:bg-blue-700"
                data-testid="submit-verification-btn"
              >
                {loading ? "Submitting..." : "Submit for Verification"}
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Enable MFA */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5 text-emerald-500" />
                Enable MFA
              </CardTitle>
              <CardDescription>
                Multi-factor authentication is required to access candidate data
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200">
                <h4 className="font-medium text-emerald-800 dark:text-emerald-200 mb-2">
                  Why MFA is required:
                </h4>
                <ul className="space-y-2 text-sm text-emerald-700 dark:text-emerald-300">
                  <li className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Protects sensitive candidate PII
                  </li>
                  <li className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Required for GDPR compliance
                  </li>
                  <li className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Prevents unauthorized account access
                  </li>
                </ul>
              </div>

              <Button
                onClick={handleEnableMFA}
                disabled={loading}
                className="w-full bg-emerald-500 hover:bg-emerald-600"
                data-testid="enable-mfa-btn"
              >
                {loading ? "Enabling..." : "Enable MFA"}
                <Lock className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Complete */}
        {step === 4 && (
          <Card className="text-center">
            <CardContent className="py-12">
              <div className="w-20 h-20 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mx-auto mb-6">
                <CheckCircle2 className="w-10 h-10 text-emerald-500" />
              </div>
              
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Verification Submitted!
              </h2>
              
              <p className="text-slate-500 dark:text-slate-400 mb-6">
                Your recruiter verification is being reviewed. This usually takes 1-2 business days.
              </p>

              <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg text-left mb-6">
                <h4 className="font-medium mb-2">What's next?</h4>
                <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-turquoise" />
                    We'll verify your LinkedIn and company
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-turquoise" />
                    You'll receive an email once approved
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-turquoise" />
                    Then you can search candidates and post jobs
                  </li>
                </ul>
              </div>

              <Button asChild className="bg-turquoise hover:bg-turquoise/90">
                <a href="/recruiter/dashboard">Go to Dashboard</a>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default RecruiterVerificationPage;
