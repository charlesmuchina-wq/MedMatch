import { useState, useEffect } from "react";
import { 
  Eye, EyeOff, Shield, User, Building2, Search, 
  MessageSquare, Download, Clock, Check, X, AlertTriangle,
  Lock, Unlock, Filter, Star, ChevronRight, Info, Award
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import axios from "axios";
import ProfileBadgeShowcase from "@/components/ProfileBadgeShowcase";
import { TrustScoreBadge } from "@/components/TrustScoreDisplay";
import EmployerReviewForm from "@/components/EmployerReviewForm";

const API = process.env.REACT_APP_BACKEND_URL;

/**
 * Blind Screening Recruiter Dashboard
 * GDPR-compliant candidate search with identity masking
 */
const BlindScreeningDashboard = () => {
  const [blindMode, setBlindMode] = useState(true);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchSkills, setSearchSkills] = useState("");
  const [searchKeywords, setSearchKeywords] = useState("");
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [dailyDownloads, setDailyDownloads] = useState({ remaining: 50, used: 0 });
  const [contactRequestDialog, setContactRequestDialog] = useState({ open: false, candidate: null });
  const [requestMessage, setRequestMessage] = useState("");
  const [reviewDialog, setReviewDialog] = useState({ open: false, candidate: null });

  useEffect(() => {
    fetchVerificationStatus();
    fetchBlindModeStatus();
  }, []);

  // Auto-search on mount if verified
  useEffect(() => {
    if (verificationStatus?.is_verified && candidates.length === 0 && !loading) {
      searchCandidates();
    }
  }, [verificationStatus]);

  const fetchVerificationStatus = async () => {
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(`${API}/api/recruiter-rbac/verification/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setVerificationStatus(response.data);
    } catch (err) {
      console.error("Failed to fetch verification status:", err);
    }
  };

  const fetchBlindModeStatus = async () => {
    try {
      const token = localStorage.getItem("medmatch-token");
      const response = await axios.get(`${API}/api/recruiter-rbac/blind-screening/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBlindMode(response.data.blind_screening_mode);
    } catch (err) {
      setBlindMode(true); // Default to blind mode
    }
  };

  const toggleBlindMode = async () => {
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/recruiter-rbac/blind-screening/toggle`,
        { enabled: !blindMode },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setBlindMode(!blindMode);
      toast.success(`Blind screening ${!blindMode ? 'enabled' : 'disabled'}`);
    } catch (err) {
      toast.error("Failed to toggle blind screening");
    }
  };

  const searchCandidates = async () => {
    if (!verificationStatus?.is_verified) {
      toast.error("Account verification required to search candidates");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("medmatch-token");
      const params = new URLSearchParams();
      if (searchSkills) params.append("skills", searchSkills);
      if (searchKeywords) params.append("keywords", searchKeywords);
      params.append("min_match_score", "0");
      params.append("limit", "20");

      const response = await axios.get(
        `${API}/api/recruiter-rbac/candidates/search?${params.toString()}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setCandidates(response.data.candidates);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const requestContact = async (candidate, jobId) => {
    try {
      const token = localStorage.getItem("medmatch-token");
      await axios.post(
        `${API}/api/mutual-match/request`,
        {
          candidate_id: candidate.id,
          job_id: jobId,
          message: requestMessage
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("Contact request sent! The candidate will be notified.");
      setContactRequestDialog({ open: false, candidate: null });
      setRequestMessage("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to send request");
    }
  };

  // Render verification required banner
  if (verificationStatus && !verificationStatus.is_verified) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <Card className="border-amber-300 bg-amber-50 dark:bg-amber-900/20">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <AlertTriangle className="w-12 h-12 text-amber-500" />
              <div>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">
                  Verification Required
                </h2>
                <p className="text-slate-600 dark:text-slate-400 mt-1">
                  Your recruiter account is pending verification. Complete verification to access candidate search.
                </p>
                <div className="mt-4 flex gap-3">
                  <Button asChild>
                    <a href="/recruiter/verify">Complete Verification</a>
                  </Button>
                  <Badge variant="outline" className="self-center">
                    Status: {verificationStatus.status}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto" data-testid="blind-screening-dashboard">
      {/* Header with Blind Mode Toggle */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-slate-100" style={{ fontFamily: 'IBM Plex Sans' }}>
            Candidate Search
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
            {blindMode ? "Blind screening active - Focus on skills, not identities" : "Full profile view enabled"}
          </p>
        </div>

        {/* Blind Mode Toggle */}
        <div className="flex items-center gap-4">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="flex items-center gap-2 p-3 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  {blindMode ? (
                    <EyeOff className="w-5 h-5 text-turquoise" />
                  ) : (
                    <Eye className="w-5 h-5 text-slate-500" />
                  )}
                  <span className="text-sm font-medium">Blind Screening</span>
                  <Switch
                    checked={blindMode}
                    onCheckedChange={toggleBlindMode}
                    data-testid="blind-mode-toggle"
                  />
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <p>Hide candidate names and photos to reduce unconscious bias</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <Badge variant="outline" className="py-1.5">
            <Download className="w-3 h-3 mr-1" />
            {dailyDownloads.remaining} downloads left today
          </Badge>
        </div>
      </div>

      {/* Search Section */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block">
                Skills (comma-separated)
              </label>
              <Input
                placeholder="e.g., ICU, Critical Care, Python"
                value={searchSkills}
                onChange={(e) => setSearchSkills(e.target.value)}
                data-testid="search-skills-input"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 block">
                Keywords
              </label>
              <Input
                placeholder="e.g., Senior, Manager, Remote"
                value={searchKeywords}
                onChange={(e) => setSearchKeywords(e.target.value)}
                data-testid="search-keywords-input"
              />
            </div>
            <div className="flex items-end">
              <Button 
                onClick={searchCandidates} 
                disabled={loading}
                className="w-full bg-turquoise hover:bg-turquoise/90"
                data-testid="search-candidates-btn"
              >
                <Search className="w-4 h-4 mr-2" />
                {loading ? "Searching..." : "Search Candidates"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        {candidates.length === 0 && !loading && (
          <Card className="p-8 text-center">
            <Search className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">Enter skills or keywords to search for candidates</p>
          </Card>
        )}

        {candidates.map((candidate) => (
          <CandidateCard
            key={candidate.id}
            candidate={candidate}
            blindMode={blindMode}
            onRequestContact={() => setContactRequestDialog({ open: true, candidate })}
            onViewProfile={() => setSelectedCandidate(candidate)}
          />
        ))}
      </div>

      {/* Contact Request Dialog */}
      <Dialog open={contactRequestDialog.open} onOpenChange={(open) => setContactRequestDialog({ open, candidate: contactRequestDialog.candidate })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-turquoise" />
              Request Contact
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="p-4 bg-turquoise/5 border border-turquoise/20 rounded-lg">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                <strong>Privacy Notice:</strong> The candidate&apos;s contact information is hidden. 
                Your request will be sent to them, and they can choose to accept or decline.
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Introduction Message (optional)</label>
              <textarea
                className="w-full mt-1.5 p-3 border rounded-lg resize-none"
                rows={3}
                placeholder="Hi, I found your profile interesting for our open position..."
                value={requestMessage}
                onChange={(e) => setRequestMessage(e.target.value)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setContactRequestDialog({ open: false, candidate: null })}>
              Cancel
            </Button>
            <Button 
              onClick={() => requestContact(contactRequestDialog.candidate, "default")}
              className="bg-turquoise hover:bg-turquoise/90"
            >
              Send Request
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

/**
 * Candidate Card with Blind Screening
 */
const CandidateCard = ({ candidate, blindMode, onRequestContact, onViewProfile }) => {
  const displayName = blindMode ? candidate.anonymous_id || `Candidate #${candidate.id?.slice(-6).toUpperCase()}` : candidate.full_name;

  return (
    <Card className="hover:shadow-md transition-shadow" data-testid={`candidate-card-${candidate.id}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
            blindMode ? "bg-slate-200 dark:bg-slate-700" : "bg-turquoise/10"
          }`}>
            {blindMode ? (
              <User className="w-8 h-8 text-slate-400" />
            ) : candidate.photo_url ? (
              <img src={candidate.photo_url} alt="" className="w-full h-full rounded-full object-cover" />
            ) : (
              <User className="w-8 h-8 text-turquoise" />
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-slate-900 dark:text-slate-100">
                {displayName}
              </h3>
              {blindMode && (
                <Badge variant="outline" className="text-xs">
                  <EyeOff className="w-3 h-3 mr-1" />
                  Blind Mode
                </Badge>
              )}
            </div>

            {/* Match Score & Trust Score */}
            <div className="flex items-center gap-2 mb-2">
              <Badge className={`${
                candidate.match_score >= 80 ? 'bg-emerald-500' : 
                candidate.match_score >= 60 ? 'bg-amber-500' : 'bg-slate-500'
              } text-white`}>
                {candidate.match_score}% Match
              </Badge>
              {candidate.trust_score && (
                <TrustScoreBadge 
                  score={candidate.trust_score} 
                  level={candidate.trust_level || 'Building'}
                  size="xs"
                />
              )}
              {/* Match Reasoning Tooltip */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button className="text-turquoise hover:text-turquoise/80">
                      <Info className="w-4 h-4" />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p className="font-medium mb-1">Why this match?</p>
                    <p className="text-xs">{candidate.match_reasoning}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>

            {/* Skills */}
            <div className="flex flex-wrap gap-1 mb-2">
              {candidate.skills?.slice(0, 8).map((skill, i) => (
                <Badge key={i} variant="secondary" className="text-xs">
                  {typeof skill === 'string' ? skill : skill.name}
                </Badge>
              ))}
              {candidate.skills?.length > 8 && (
                <Badge variant="outline" className="text-xs">+{candidate.skills.length - 8} more</Badge>
              )}
            </div>

            {/* Verified Badges */}
            {candidate.badges?.length > 0 && (
              <div className="flex items-center gap-2 mb-2 py-1">
                <Award className="w-4 h-4 text-amber-500" />
                <div className="flex items-center gap-1">
                  {candidate.badges.slice(0, 4).map((badge, idx) => (
                    <TooltipProvider key={idx}>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="relative">
                            {badge.badge_image_url ? (
                              <img 
                                src={badge.badge_image_url} 
                                alt={badge.credential_name}
                                className="w-8 h-8 rounded object-contain bg-white border border-gray-200"
                              />
                            ) : (
                              <div className="w-8 h-8 rounded bg-amber-100 flex items-center justify-center">
                                <Award className="w-4 h-4 text-amber-600" />
                              </div>
                            )}
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="font-medium">{badge.credential_name}</p>
                          <p className="text-xs text-gray-400">{badge.issuing_authority}</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  ))}
                  {candidate.badges.length > 4 && (
                    <span className="text-xs text-gray-500 ml-1">+{candidate.badges.length - 4}</span>
                  )}
                </div>
                <Badge variant="outline" className="text-xs text-green-600 border-green-200">
                  Verified
                </Badge>
              </div>
            )}

            {/* Summary */}
            <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2">
              {candidate.summary?.slice(0, 200)}...
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-2">
            <Button 
              size="sm" 
              onClick={onRequestContact}
              className="bg-turquoise hover:bg-turquoise/90"
              data-testid={`request-contact-${candidate.id}`}
            >
              <MessageSquare className="w-4 h-4 mr-1" />
              Request Contact
            </Button>
            <Button 
              size="sm" 
              variant="outline"
              onClick={onViewProfile}
            >
              View Profile
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>

        {/* Contact Status Lock */}
        <div className="mt-3 pt-3 border-t flex items-center gap-2 text-xs text-slate-400">
          <Lock className="w-3 h-3" />
          Contact details hidden until candidate accepts your request
        </div>
      </CardContent>
    </Card>
  );
};

export default BlindScreeningDashboard;
