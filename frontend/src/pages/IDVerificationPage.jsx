import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { useTheme } from "@/App";
import { 
  ShieldCheck, Upload, Camera, User, Building, BadgeCheck,
  Loader2, CheckCircle2, AlertCircle, Clock, Star,
  FileText, Globe, Link as LinkIcon, ChevronRight, X, RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const IDVerificationPage = ({ user }) => {
  const { isDark } = useTheme();
  const fileInputRef = useRef(null);
  
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [step, setStep] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  
  // ID Verification Form
  const [documentType, setDocumentType] = useState('government_id');
  const [fullName, setFullName] = useState(user?.name || '');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [country, setCountry] = useState('US');
  const [uploadedDocs, setUploadedDocs] = useState({ front: null, selfie: null });
  
  // Company Verification Form
  const [companyName, setCompanyName] = useState('');
  const [companyWebsite, setCompanyWebsite] = useState('');
  const [companyEmailDomain, setCompanyEmailDomain] = useState('');
  const [roleAtCompany, setRoleAtCompany] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');

  useEffect(() => {
    fetchVerificationStatus();
  }, []);

  const fetchVerificationStatus = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API}/id-verification/status`);
      setVerificationStatus(response.data);
      
      // Set step based on status
      if (response.data.status === 'approved') {
        setStep(4);
      } else if (response.data.status === 'pending') {
        setStep(3);
      }
    } catch (e) {
      console.error("Failed to fetch verification status:", e);
    }
    setIsLoading(false);
  };

  const startVerification = async () => {
    try {
      const response = await axios.post(`${API}/id-verification/request-verification`, {
        document_type: documentType,
        full_name: fullName,
        date_of_birth: dateOfBirth,
        country
      });
      
      toast.success("Verification request created");
      setStep(2);
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to start verification");
    }
  };

  const uploadDocument = async (file, side) => {
    if (!file) return;
    
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_side', side);
      
      const response = await axios.post(
        `${API}/id-verification/upload-document`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      
      setUploadedDocs(prev => ({ ...prev, [side]: file.name }));
      toast.success(`${side} document uploaded`);
      
      if (response.data.next_step === 'processing') {
        setStep(3);
        fetchVerificationStatus();
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || "Upload failed");
    }
    setIsUploading(false);
  };

  const verifyCompany = async () => {
    try {
      const response = await axios.post(`${API}/id-verification/verify-company`, {
        company_name: companyName,
        company_website: companyWebsite,
        company_email_domain: companyEmailDomain,
        role_at_company: roleAtCompany,
        linkedin_url: linkedinUrl
      });
      
      if (response.data.status === 'approved') {
        toast.success("Company verified automatically!");
      } else {
        toast.info("Company verification pending review");
      }
      
      fetchVerificationStatus();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Company verification failed");
    }
  };

  const getStatusBadge = () => {
    if (!verificationStatus) return null;
    
    const { status, verification_level } = verificationStatus;
    
    const configs = {
      approved: { color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', icon: CheckCircle2, text: 'Verified' },
      pending: { color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400', icon: Clock, text: 'Pending' },
      rejected: { color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', icon: AlertCircle, text: 'Rejected' },
      unverified: { color: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400', icon: ShieldCheck, text: 'Unverified' }
    };
    
    const config = configs[status] || configs.unverified;
    const Icon = config.icon;
    
    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {config.text} (Level {verification_level})
      </Badge>
    );
  };

  const isRecruiter = user?.role === 'recruiter';

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-turquoise" />
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 lg:p-12 max-w-4xl mx-auto" data-testid="id-verification-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Identity Verification
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            {isRecruiter ? "Verify your identity to unlock premium recruiter features" : "Verify your identity for trusted interactions"}
          </p>
        </div>
        {getStatusBadge()}
      </div>

      {/* Verification Levels Info */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Star className="w-5 h-5 text-amber-500" />
            Verification Levels
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-4 gap-4">
            {[
              { level: 0, name: 'Unverified', icon: User, features: ['Basic search'] },
              { level: 1, name: 'Email Verified', icon: FileText, features: ['Job posting'] },
              { level: 2, name: 'Company Verified', icon: Building, features: ['Contact candidates'] },
              { level: 3, name: 'ID Verified', icon: BadgeCheck, features: ['Premium features'] }
            ].map((lvl) => {
              const Icon = lvl.icon;
              const isActive = verificationStatus?.verification_level >= lvl.level;
              
              return (
                <div 
                  key={lvl.level}
                  className={`p-4 rounded-lg border-2 text-center transition-all ${
                    isActive 
                      ? 'border-turquoise bg-turquoise/5 dark:bg-turquoise/10' 
                      : 'border-slate-200 dark:border-slate-700'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center ${
                    isActive ? 'bg-turquoise text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                  }`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <p className={`font-medium text-sm ${isActive ? 'text-turquoise' : 'text-slate-500'}`}>
                    Level {lvl.level}
                  </p>
                  <p className="font-semibold text-slate-900 dark:text-slate-100 mb-2">
                    {lvl.name}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {lvl.features[0]}
                  </p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Verification Flow */}
      {verificationStatus?.status !== 'approved' && (
        <div className="space-y-6">
          {/* Company Verification (for recruiters) */}
          {isRecruiter && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="w-5 h-5 text-blue-500" />
                  Company Verification
                </CardTitle>
                <CardDescription>
                  Verify your company affiliation to reach Level 2
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <Label>Company Name *</Label>
                    <Input 
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="Acme Corporation"
                      data-testid="company-name-input"
                    />
                  </div>
                  <div>
                    <Label>Company Website</Label>
                    <Input 
                      value={companyWebsite}
                      onChange={(e) => setCompanyWebsite(e.target.value)}
                      placeholder="https://acme.com"
                    />
                  </div>
                  <div>
                    <Label>Company Email Domain *</Label>
                    <Input 
                      value={companyEmailDomain}
                      onChange={(e) => setCompanyEmailDomain(e.target.value)}
                      placeholder="acme.com"
                      data-testid="company-domain-input"
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Should match your email domain for auto-verification
                    </p>
                  </div>
                  <div>
                    <Label>Your Role *</Label>
                    <Input 
                      value={roleAtCompany}
                      onChange={(e) => setRoleAtCompany(e.target.value)}
                      placeholder="Talent Acquisition Manager"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <Label>LinkedIn Profile URL</Label>
                    <Input 
                      value={linkedinUrl}
                      onChange={(e) => setLinkedinUrl(e.target.value)}
                      placeholder="https://linkedin.com/in/yourprofile"
                    />
                  </div>
                </div>
                
                <Button 
                  onClick={verifyCompany}
                  disabled={!companyName || !companyEmailDomain || !roleAtCompany}
                  className="w-full bg-blue-500 hover:bg-blue-600"
                  data-testid="verify-company-btn"
                >
                  <Building className="w-4 h-4 mr-2" />
                  Verify Company Affiliation
                </Button>
              </CardContent>
            </Card>
          )}

          {/* ID Verification */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-turquoise" />
                Government ID Verification
              </CardTitle>
              <CardDescription>
                Upload your government ID to reach Level 3 (highest trust)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Progress Steps */}
              <div className="flex items-center mb-8">
                {['Personal Info', 'Upload Documents', 'Processing', 'Verified'].map((label, i) => (
                  <div key={label} className="flex-1 flex items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      step > i + 1 ? 'bg-turquoise text-white' : 
                      step === i + 1 ? 'bg-turquoise/20 text-turquoise border-2 border-turquoise' :
                      'bg-slate-100 dark:bg-slate-800 text-slate-400'
                    }`}>
                      {step > i + 1 ? <CheckCircle2 className="w-4 h-4" /> : i + 1}
                    </div>
                    {i < 3 && (
                      <div className={`flex-1 h-1 mx-2 ${step > i + 1 ? 'bg-turquoise' : 'bg-slate-200 dark:bg-slate-700'}`} />
                    )}
                  </div>
                ))}
              </div>

              {/* Step 1: Personal Info */}
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <Label>Document Type</Label>
                    <Select value={documentType} onValueChange={setDocumentType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="government_id">Government ID</SelectItem>
                        <SelectItem value="passport">Passport</SelectItem>
                        <SelectItem value="drivers_license">Driver's License</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div>
                      <Label>Full Legal Name *</Label>
                      <Input 
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="John Doe"
                        data-testid="full-name-input"
                      />
                    </div>
                    <div>
                      <Label>Date of Birth</Label>
                      <Input 
                        type="date"
                        value={dateOfBirth}
                        onChange={(e) => setDateOfBirth(e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label>Country</Label>
                    <Select value={country} onValueChange={setCountry}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="US">United States</SelectItem>
                        <SelectItem value="CA">Canada</SelectItem>
                        <SelectItem value="GB">United Kingdom</SelectItem>
                        <SelectItem value="AU">Australia</SelectItem>
                        <SelectItem value="DE">Germany</SelectItem>
                        <SelectItem value="FR">France</SelectItem>
                        <SelectItem value="OTHER">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <Button 
                    onClick={startVerification}
                    disabled={!fullName}
                    className="w-full bg-turquoise hover:bg-turquoise/90"
                    data-testid="start-verification-btn"
                  >
                    Continue to Document Upload <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              )}

              {/* Step 2: Upload Documents */}
              {step === 2 && (
                <div className="space-y-6">
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Please upload clear photos of your {documentType.replace('_', ' ')} and a selfie
                  </p>
                  
                  <div className="grid sm:grid-cols-2 gap-4">
                    {/* Front of ID */}
                    <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                      uploadedDocs.front ? 'border-turquoise bg-turquoise/5' : 'border-slate-300 dark:border-slate-600 hover:border-turquoise'
                    }`}>
                      <input
                        type="file"
                        accept="image/*,.pdf"
                        className="hidden"
                        id="front-upload"
                        onChange={(e) => uploadDocument(e.target.files[0], 'front')}
                      />
                      <label htmlFor="front-upload" className="cursor-pointer">
                        {uploadedDocs.front ? (
                          <>
                            <CheckCircle2 className="w-12 h-12 text-turquoise mx-auto mb-3" />
                            <p className="font-medium text-turquoise">Front Uploaded</p>
                            <p className="text-xs text-slate-500 mt-1">{uploadedDocs.front}</p>
                          </>
                        ) : (
                          <>
                            <Upload className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                            <p className="font-medium text-slate-700 dark:text-slate-300">Front of ID</p>
                            <p className="text-xs text-slate-500 mt-1">Click to upload</p>
                          </>
                        )}
                      </label>
                    </div>
                    
                    {/* Selfie */}
                    <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                      uploadedDocs.selfie ? 'border-turquoise bg-turquoise/5' : 'border-slate-300 dark:border-slate-600 hover:border-turquoise'
                    }`}>
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        id="selfie-upload"
                        onChange={(e) => uploadDocument(e.target.files[0], 'selfie')}
                      />
                      <label htmlFor="selfie-upload" className="cursor-pointer">
                        {uploadedDocs.selfie ? (
                          <>
                            <CheckCircle2 className="w-12 h-12 text-turquoise mx-auto mb-3" />
                            <p className="font-medium text-turquoise">Selfie Uploaded</p>
                            <p className="text-xs text-slate-500 mt-1">{uploadedDocs.selfie}</p>
                          </>
                        ) : (
                          <>
                            <Camera className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                            <p className="font-medium text-slate-700 dark:text-slate-300">Selfie Photo</p>
                            <p className="text-xs text-slate-500 mt-1">Click to upload</p>
                          </>
                        )}
                      </label>
                    </div>
                  </div>
                  
                  {isUploading && (
                    <div className="flex items-center justify-center gap-2 text-turquoise">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Uploading...</span>
                    </div>
                  )}
                  
                  <Button variant="outline" onClick={() => setStep(1)}>
                    Back
                  </Button>
                </div>
              )}

              {/* Step 3: Processing */}
              {step === 3 && (
                <div className="text-center py-8">
                  <div className="w-20 h-20 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Clock className="w-10 h-10 text-amber-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                    Verification in Progress
                  </h3>
                  <p className="text-slate-500 dark:text-slate-400 mb-6">
                    We're reviewing your documents. This usually takes a few minutes.
                  </p>
                  <Button variant="outline" onClick={fetchVerificationStatus}>
                    <RefreshCw className="w-4 h-4 mr-2" /> Check Status
                  </Button>
                </div>
              )}

              {/* Step 4: Verified */}
              {step === 4 && (
                <div className="text-center py-8">
                  <div className="w-20 h-20 bg-emerald-100 dark:bg-emerald-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                    <BadgeCheck className="w-10 h-10 text-emerald-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                    Identity Verified!
                  </h3>
                  <p className="text-slate-500 dark:text-slate-400 mb-2">
                    You've achieved Level {verificationStatus?.verification_level} verification
                  </p>
                  {verificationStatus?.expires_at && (
                    <p className="text-sm text-slate-400">
                      Valid until {new Date(verificationStatus.expires_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Already Verified */}
      {verificationStatus?.status === 'approved' && (
        <Card className="border-2 border-emerald-200 dark:border-emerald-800">
          <CardContent className="py-12 text-center">
            <div className="w-24 h-24 bg-emerald-100 dark:bg-emerald-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <BadgeCheck className="w-12 h-12 text-emerald-500" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
              You're Verified!
            </h2>
            <p className="text-slate-500 dark:text-slate-400 mb-4">
              Level {verificationStatus.verification_level} • {verificationStatus.level_info?.name}
            </p>
            {verificationStatus.expires_at && (
              <p className="text-sm text-slate-400">
                Valid until {new Date(verificationStatus.expires_at).toLocaleDateString()}
              </p>
            )}
            
            <div className="mt-8 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg max-w-md mx-auto">
              <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Unlocked Features:
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {verificationStatus.level_info?.features?.map((feature) => (
                  <Badge key={feature} variant="outline" className="capitalize">
                    {feature.replace('_', ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default IDVerificationPage;
